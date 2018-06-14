import os
import unittest

from tinamit.EnvolturasMDS import ModeloVensim, ModeloPySD, ModeloVensimMdl, generar_mds
from tinamit.MDS import EnvolturaMDS


# Los tipos de modelos DS que queremos comprobar.
tipos_modelos = {
    'mdlVensim': {'envlt': ModeloVensimMdl, 'prueba': 'recursos/prueba_senc.mdl'},
    'PySDVensim': {'envlt': ModeloPySD, 'prueba': 'recursos/prueba_senc.mdl'},
    'PySD_XMILE': {'envlt': ModeloPySD, 'prueba': 'recursos/prueba_senc_.xmile'},
    'dllVensim': {'envlt': ModeloVensim, 'prueba': 'recursos/prueba_senc.vpm'}
}

# Quitar los modelos no instalados en la computadora actual
for nmb in list(tipos_modelos):
    if not tipos_modelos[nmb]['envlt'].instalado:
        tipos_modelos.pop(nmb)

# Agregar la ubicación del archivo actual
dir_act = os.path.split(__file__)[0]
for d_m in tipos_modelos.values():
    d_m['prueba'] = os.path.join(dir_act, d_m['prueba'])


class Test_ModeloSenc(unittest.TestCase):
    """
    Verifica el funcionamiento de los programas de MDS.
    """

    @classmethod
    def setUpClass(cls):

        # Generar las instancias de los modelos
        cls.modelos = {ll: d['envlt'](d['prueba']) for ll, d in tipos_modelos.items()}  # type: dict[str, EnvolturaMDS]

        # Información sobre los variables del modelo de prueba
        cls.info_vars = {
            'Lluvia': {'unidades': 'm3/mes', 'líms': (0, None)},
            'Nivel lago inicial': {'unidades': 'm3', 'líms': (0, None), 'val_inic': 1500},
            'Flujo río': {'unidades': 'm3/mes', 'líms': (0, None)},
            'Lago': {'unidades': 'm3', 'líms': (0, None)},
            'Evaporación': {'unidades': 'm3/mes', 'líms': (0, None)},
            'Aleatorio': {'unidades': 'Sdmn', 'líms': (0, 1), 'val_inic': 2.3},
        }  # type: dict[str, dict]

        # Para cada modelo...
        for mod in cls.modelos.values():

            # Inicializar los variables iniciales
            for v, d_v in cls.info_vars.items():

                # Iniciar los valores iniciales, si hay
                if 'val_inic' in d_v:
                    mod.inic_val_var(v, d_v['val_inic'])

            # Correr el modelo para 200 pasos, guardando los egresos del variable "Lago"
            mod.simular(tiempo_final=200, vars_interés=['Lago', 'Aleatorio'])

    def test_leer_vars(símismo):
        """
        Comprobar que los nombres de los variables se leyeron correctamente.
        """
        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                vars_modelo = set(mod.variables)
                símismo.assertSetEqual(set(símismo.info_vars), vars_modelo)

    def test_unid_tiempo(símismo):
        """
        Comprobar que las unidades de tiempo se leyeron correctamente.
        """
        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                símismo.assertEqual('mes', mod.unidad_tiempo())

    def test_leer_info(símismo):
        """
        Comprobar que la documentación de cada variable se leyó correctamente.
        """

        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                símismo.assertTrue(len(mod.obt_info_var(v)) > 0 for v in mod.variables)

    def test_leer_unidades(símismo):
        """
        Comprobar que las unidades de los variables se leyeron correctamente.
        """

        unids = {v: d_v['unidades'].lower() for v, d_v in símismo.info_vars.items()}

        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                unids_mod = {v: mod.obt_unidades_var(v).lower() for v in mod.variables}
                símismo.assertDictEqual(unids, unids_mod)

    def test_leer_líms(símismo):
        """
        Comprobar que los límites de los variables se leyeron correctamente.
        """

        unids = {v: d_v['líms'] for v, d_v in símismo.info_vars.items()}

        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                unids_mod = {v: mod.obt_lims_var(v) for v in mod.variables}
                símismo.assertDictEqual(unids, unids_mod)

    def test_cmb_vals_inic_constante(símismo):
        """
        Comprobar que los valores iniciales se establecieron correctamente en el diccionario interno.
        """

        for ll, mod in símismo.modelos.items():
            v = 'Nivel lago inicial'
            d_v = símismo.info_vars[v]

            with símismo.subTest(mod=ll):
                símismo.assertEqual(mod.obt_val_actual_var(v), d_v['val_inic'])

    def test_cambiar_vals_inic_var_dinámico(símismo):
        """
        Asegurarse que los valores iniciales de variables dinámicos aparezcan en el paso 0 de los resultados.
        """

        for ll, mod in símismo.modelos.items():
            v = 'Aleatorio'
            d_v = símismo.info_vars[v]

            with símismo.subTest(mod=ll):
                símismo.assertEqual(mod.leer_resultados(v)[0], d_v['val_inic'])

    def test_cambiar_vals_inic_nivel(símismo):
        """
        Comprobar que valores iniciales pasados a un variable de valor inicial aparezcan en los resultados también.
        """
        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                símismo.assertEqual(
                    mod.leer_resultados('Lago')[0],
                    símismo.info_vars['Nivel lago inicial']['val_inic']
                )

    def test_simul(símismo):
        """
        Assegurarse que la simulación dió los resultados esperados.
        """

        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                # Leer el resultado del último día de simulación pára el variable "Lago"
                val_simulado = mod.leer_resultados('Lago')[-1]

                # Debería ser aproximativamente igual a 100
                símismo.assertEqual(round(val_simulado, 3), 100)

    @classmethod
    def tearDownClass(cls):
        """
        Limpiar todos los archivos temporarios.
        """

        limpiar_mds()


def limpiar_mds():
    # Limpiamos todos los documentos temporarios generados por los programas de modelos DS.
    for c in os.walk('../recursos'):
        for a in c[2]:
            nmbr, ext = os.path.splitext(a)
            try:
                if 'Corrida Tinamït' in nmbr:
                    os.remove(a)
                elif ext in ['.2mdl', '.vdf']:
                    os.remove(a)
                elif a == 'prueba_senc.py':
                    os.remove(a)
                elif a == 'prueba_senc_.py':
                    os.remove(a)
            except PermissionError:
                pass


class Test_GenerarMDS(unittest.TestCase):
    """
    Verifica el funcionamiento del generado automático de modelos DS.
    """

    def test_generación_auto_mds(símismo):
        # Verificamos que funcione la generación automática de modelos DS a base de un archivo.

        for m, d in tipos_modelos.items():
            with símismo.subTest(ext=os.path.splitext(d['prueba'])[1], envlt=d['envlt'].__name__):
                try:
                    mod = generar_mds(d['prueba'])  # Generar el modelo
                    símismo.assertIsInstance(mod, EnvolturaMDS)
                except ValueError:
                    # No hay problema si el MDS no se pudo leer en la computadora actual. De pronto no estaba instalado.
                    pass

    def test_generación_auto_mds_con_error_extensión(símismo):
        # Comprobar que extensiones no reconocidas devuelvan un error.

        with símismo.assertRaises(ValueError):
            generar_mds('Modelo con extensión no reconocida.abc')

    def test_generación_auto_mds_con_motor_especificado(símismo):
        # Comprobar la generación de modelos DS con el motor de simulación especificado.

        mod = generar_mds(tipos_modelos['PySDVensim']['prueba'], motor=ModeloPySD)
        símismo.assertIsInstance(mod, ModeloPySD)

        mod = generar_mds(tipos_modelos['PySDVensim']['prueba'], motor=ModeloVensimMdl)
        símismo.assertIsInstance(mod, ModeloVensimMdl)

    def test_generación_auto_mds_modelo_erróneo(símismo):
        # Asegurarse que un archivo erróneo devuelva un error.

        with símismo.assertRaises(ValueError):
            generar_mds('Yo no existo.mdl')
