import tkinter as tk
from tkinter import filedialog as diálogo

from Interfaz import CajasGenéricas as CjG
from Interfaz import CajasSubEtapas as CjSE
from Interfaz import Controles as Ctrl
from Interfaz import ControlesGenéricos as CtrG
from Interfaz import Formatos as Fm, Botones as Bt, Arte as Art, Animaciones as Anim

from Conectado import Conectado


class CajaInic(tk.Frame):
    def __init__(símismo, apli):
        super().__init__(**Fm.formato_CjInic)
        trads = apli.Trads
        símismo.logo = Art.imagen('LogoInic')
        logo = tk.Label(símismo, image=símismo.logo, **Fm.formato_LogoInic)
        logo.pack(Fm.ubic_LogoInic)

        cj_bts_inic = tk.Frame(símismo, **Fm.formato_cajas)
        Bt.BotónTexto(cj_bts_inic, comanda=símismo.acción_bt_empezar, texto=trads['Empezar'],
                      formato_norm=Fm.formato_BtsInic,
                      formato_sel=Fm.formato_bts_sel,
                      ubicación=Fm.ubic_BtsInic, tipo_ubic='pack')
        Bt.BotónTexto(cj_bts_inic, comanda=símismo.acción_bt_ayuda, texto=trads['Ayuda'],
                      formato_norm=Fm.formato_BtsInic,
                      formato_sel=Fm.formato_bts_sel,
                      ubicación=Fm.ubic_BtsInic, tipo_ubic='pack')
        cj_bts_inic.pack()

        símismo.place(**Fm.ubic_CjInic)

    def acción_bt_empezar(símismo):
        Anim.quitar(símismo, 'arriba')
        símismo.destroy()

    def acción_bt_ayuda(símismo):
        pass


class CajaLeng(tk.Frame):
    def __init__(símismo, apli):
        super().__init__(**Fm.formato_cajas)
        símismo.apli = apli
        símismo.DicLeng = símismo.apli.DicLeng

        símismo.bt_regreso = Bt.BotónImagen(símismo, comanda=símismo.acción_bt_regreso,
                                            img_norm=Art.imagen('BtRegrCent_norm'),
                                            img_sel=Art.imagen('BtRegrCent_sel'),
                                            formato=Fm.formato_botones,
                                            ubicación=Fm.ubic_BtRegrCent, tipo_ubic='place')
        etiq = tk.Label(símismo, text=apli.Trads['OpsLengs'], **Fm.formato_CbzLeng)
        etiq.place(**Fm.ubic_CbzLeng)

        cj_central = tk.Frame(símismo, **Fm.formato_cajas)

        cj_izq = tk.Frame(cj_central, **Fm.formato_cajas)
        etiq_izq = tk.Label(cj_izq, text=apli.Trads['EnTrabajo'], **Fm.formato_EtiqLengLados)
        etiq_izq.place(**Fm.ubic_EtiqCbzColsLeng)
        símismo.lista_izq = CtrG.ListaItemas(cj_izq, formato_cj=Fm.formato_CjLstLengLados,
                                             ubicación=Fm.ubic_LstsLeng, tipo_ubic='place')

        lín_vert_1 = tk.Frame(cj_central, **Fm.formato_LínVert)

        cj_med = tk.Frame(cj_central, **Fm.formato_cajas)
        etiq_med = tk.Label(cj_med, text=apli.Trads['Listas'], **Fm.formato_EtiqLengCentro)
        etiq_med.place(**Fm.ubic_EtiqCbzColsLeng)
        símismo.lista_med = CtrG.ListaItemas(cj_med, formato_cj=Fm.formato_CjLstLengCentro,
                                             ubicación=Fm.ubic_LstsLeng, tipo_ubic='place')

        lín_vert_2 = tk.Frame(cj_central, **Fm.formato_LínVert)

        cj_derech = tk.Frame(cj_central, **Fm.formato_cajas)
        etiq_derech = tk.Label(cj_derech, text=apli.Trads['ParaHacer'], **Fm.formato_EtiqLengLados)
        etiq_derech.place(**Fm.ubic_EtiqCbzColsLeng)
        cj_añadir = Ctrl.CajaAñadirLeng(símismo, cj_derech)
        símismo.lista_derech = CtrG.ListaItemas(cj_derech, formato_cj=Fm.formato_CjLstLengLados,
                                                ubicación=Fm.ubic_LstsLeng_bajo, tipo_ubic='place')

        símismo.establecer_cols()

        cj_izq.place(**Fm.ubic_CjIzqLeng)
        lín_vert_1.place(**Fm.ubic_LínVert1)

        cj_med.place(**Fm.ubic_CjMedLeng)
        lín_vert_2.place(**Fm.ubic_LínVert2)

        cj_añadir.place(**Fm.ubic_CjAñadirLeng)
        cj_derech.place(**Fm.ubic_CjDerchLeng)

        cj_central.place(**Fm.ubic_CjCentLeng)
        símismo.place(**Fm.ubic_CjLeng)

    def acción_bt_regreso(símismo):
        Anim.quitar(símismo, 'derecha')

    def establecer_cols(símismo):
        símismo.DicLeng.verificar_estados()
        for nombre, leng in sorted(símismo.DicLeng.lenguas.items()):
            if 0 < leng['Estado'] < 1:
                lista = símismo.lista_izq
                utilzb = True
            elif leng['Estado'] == 1:
                lista = símismo.lista_med
                utilzb = True
            elif leng['Estado'] == 0:
                lista = símismo.lista_derech
                utilzb = False
            else:
                raise ValueError

            borr = True
            if nombre == símismo.DicLeng.estándar:
                borr = False

            utilznd = False
            if nombre == símismo.DicLeng.dic['Actual']:
                utilznd = True

            Ctrl.ItemaLeng(símismo, lista=lista, nombre=nombre, lengua=leng, estado=leng['Estado'],
                           utilizando=utilznd, utilizable=utilzb, borrable=borr)

    def refrescar(símismo):
        for lista in [símismo.lista_izq, símismo.lista_med, símismo.lista_derech]:
            lista.borrar()
        símismo.establecer_cols()

    def añadir_lengua(símismo, nombre, izqder):
        símismo.DicLeng.lenguas[nombre] = {'Estado': 0.0, 'IzqaDerech': izqder, 'Trads': {}}
        símismo.DicLeng.guardar()
        símismo.refrescar()

    def utilizar(símismo, nombre):
        if nombre != símismo.DicLeng.leng_act:
            if 'AvisoReinic' in símismo.DicLeng.lenguas[nombre]['Trads'].keys():
                texto = símismo.DicLeng.lenguas[nombre]['Trads']['AvisoReinic']
            else:
                texto = símismo.DicLeng.lenguas[símismo.DicLeng.estándar]['Trads']['AvisoReinic']
            Ctrl.CajaAvisoReinic(texto=texto, apli=símismo.apli)
            símismo.DicLeng.dic['Actual'] = nombre
            símismo.DicLeng.guardar()
            símismo.refrescar()

    def editar(símismo, nombre):
        leng_base = símismo.DicLeng.dic['Actual']
        if leng_base == nombre:
            leng_base = símismo.DicLeng.estándar
        dic_leng_base = símismo.DicLeng.lenguas[leng_base]

        dic_leng_edit = símismo.DicLeng.lenguas[nombre]
        Ctrl.CajaEditLeng(símismo, símismo.apli, leng_base=leng_base, dic_leng_base=dic_leng_base,
                          leng_edit=nombre, dic_leng_edit=dic_leng_edit)

    def confirmar_borrar(símismo, nombre):
        Ctrl.CajaAvisoBorrar(apli=símismo.apli, nombre=nombre, acción=símismo.borrar)

        símismo.DicLeng.guardar()

    def borrar(símismo, nombre):
        símismo.DicLeng.lenguas.pop(nombre)
        if símismo.DicLeng.dic['Actual'] == nombre:
            símismo.DicLeng.dic['Actual'] = símismo.DicLeng.estándar
        símismo.DicLeng.guardar()
        símismo.refrescar()


class CajaCentral(tk.Frame):
    def __init__(símismo, apli):
        super().__init__(**Fm.formato_CjCent)
        símismo.CjCabeza = CajaCabeza(símismo, apli=apli)

        símismo.ContCjEtapas = CjG.ContCajaEtps(símismo)
        núm_etapas = 4
        símismo.CajasEtapas = [CajaEtp1(símismo.ContCjEtapas, apli, núm_etapas),
                               CajaEtp2(símismo.ContCjEtapas, apli, núm_etapas),
                               CajaEtp3(símismo.ContCjEtapas, apli, núm_etapas),
                               CajaEtp4(símismo.ContCjEtapas, apli, núm_etapas),
                               ]
        símismo.ContCjEtapas.establecer_cajas(símismo.CajasEtapas)

        símismo.CjIzq = CajaIzq(símismo, cajas_etapas=símismo.CajasEtapas)

        símismo.bloquear_cajas(list(range(2, len(símismo.CajasEtapas) + 1)))

        símismo.place(**Fm.ubic_CjCent)

    def bloquear_cajas(símismo, núms_cajas):
        for n in núms_cajas:
            if n > 1:
                símismo.CajasEtapas[n - 2].bloquear_transición(dirección='siguiente')
            if n < len(símismo.CajasEtapas):
                símismo.CajasEtapas[n].bloquear_transición(dirección='anterior')
            símismo.CjIzq.bts[n - 1].bloquear()

    def desbloquear_cajas(símismo, núms_cajas):
        for n in núms_cajas:
            símismo.CajasEtapas[n-1].acción_desbloquear()
            if n > 1:
                símismo.CajasEtapas[n - 2].desbloquear_transición(dirección='siguiente')
            if n < len(símismo.CajasEtapas):
                símismo.CajasEtapas[n].desbloquear_transición(dirección='anterior')
            símismo.CjIzq.bts[n - 1].desbloquear()


class CajaCabeza(tk.Frame):
    def __init__(símismo, pariente, apli):
        super().__init__(pariente, **Fm.formato_CjCabeza)
        símismo.apli = apli
        símismo.pariente = pariente
        símismo.logo_cabeza = Art.imagen('LogoCent')
        logo_cabeza = tk.Label(símismo, image=símismo.logo_cabeza, **Fm.formato_LogoCabz)
        logo_cabeza.place(**Fm.ubic_LogoCabz)

        cj_bts_archivo = tk.Frame(símismo, **Fm.formato_cajas)
        Bt.BotónImagen(cj_bts_archivo, comanda=símismo.acción_bt_nuevo,
                       img_norm=Art.imagen('BtNuevo_norm'),
                       img_sel=Art.imagen('BtNuevo_sel'),
                       formato=Fm.formato_botones,
                       ubicación=Fm.ubic_BtNuevo, tipo_ubic='grid')
        Bt.BotónImagen(cj_bts_archivo, comanda=símismo.acción_bt_guardar,
                       img_norm=Art.imagen('BtGuardar_norm'),
                       img_sel=Art.imagen('BtGuardar_sel'),
                       formato=Fm.formato_botones,
                       ubicación=Fm.ubic_BtGuardar, tipo_ubic='grid')
        Bt.BotónImagen(cj_bts_archivo, comanda=símismo.acción_bt_guardar_como,
                       img_norm=Art.imagen('BtGuardarComo_norm'),
                       img_sel=Art.imagen('BtGuardarComo_sel'),
                       formato=Fm.formato_botones,
                       ubicación=Fm.ubic_BtGuardarComo, tipo_ubic='grid')
        Bt.BotónImagen(cj_bts_archivo, comanda=símismo.acción_bt_abrir,
                       img_norm=Art.imagen('BtAbrir_norm'),
                       img_sel=Art.imagen('BtAbrir_sel'),
                       formato=Fm.formato_botones,
                       ubicación=Fm.ubic_BtAbrir, tipo_ubic='grid')
        cj_bts_archivo.place(**Fm.ubic_BtsArchivo)

        Bt.BotónImagen(símismo, comanda=símismo.acción_bt_leng,
                       img_norm=Art.imagen('BtLeng_norm'),
                       img_sel=Art.imagen('BtLeng_sel'),
                       formato=Fm.formato_botones,
                       ubicación=Fm.ubic_BtLeng, tipo_ubic='place')
        símismo.pack(**Fm.ubic_CjCabeza)

    def acción_bt_nuevo(símismo):
        símismo.apli.Modelo.reinic()
        símismo.pariente.ContCjEtapas.ir_a_caja(1)
        símismo.pariente.desbloquear_cajas([1])
        símismo.pariente.bloquear_cajas([2, 3, 4])

    def acción_bt_guardar(símismo):
        if símismo.apli.Modelo.archivo_receta is not None:
            símismo.apli.Modelo.guardar()
        else:
            símismo.acción_bt_guardar_como()

    def acción_bt_abrir(símismo):
        apli = símismo.apli
        nombre_archivo_con = diálogo.askopenfile(filetypes=[(apli.Trads['ArchivoTinamit'], '*.tin')],
                                                       title=apli.Trads['CargarModeloConectado'])
        if nombre_archivo_con:
            símismo.apli.Modelo.cargar(nombre_archivo_con)
            símismo.pariente.ContCjEtapas.ir_a_caja(1)
            símismo.pariente.desbloquear_cajas([1])

    def acción_bt_guardar_como(símismo):
        apli = símismo.apli
        nombre_archivo_con = diálogo.asksaveasfilename(defaultextension='.tin',
                                                       filetypes=[(apli.Trads['ArchivoTinamit'], '*.tin')],
                                                       title=apli.Trads['CargarModeloConectado'])
        símismo.apli.Modelo.archivo_receta = nombre_archivo_con
        símismo.apli.Modelo.guardar()

    def acción_bt_leng(símismo):
        Anim.sobreponer(símismo.apli.CajaCentral, símismo.apli.CajaLenguas, 'izquierda')


class CajaIzq(tk.Frame):
    def __init__(símismo, pariente, cajas_etapas):
        super().__init__(pariente, **Fm.formato_cajas)

        símismo.bts = []
        for cj in cajas_etapas:
            símismo.bts.append(Bt.BotónNavIzq(símismo, caja=cj))

        símismo.pack(**Fm.ubic_CjIzq)


class CajaEtp1(CjG.CajaEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=apli.Trads['CargarModelos'], núm=1, total=total)

        total_subcajas = 1
        subcajas = [CjSE.CajaSubEtp11(símismo, apli, total=total_subcajas)]

        símismo.especificar_subcajas(subcajas)

    def acción_desbloquear(símismo):
        símismo.desbloquear_subcajas([1])


class CajaEtp2(CjG.CajaEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=apli.Trads['ConectarVariables'], núm=2, total=total)
        total_subcajas = 1
        subcajas = [CjSE.CajaSubEtp21(símismo, apli, total=total_subcajas)]

        símismo.especificar_subcajas(subcajas)

    def acción_desbloquear(símismo):
        símismo.desbloquear_subcajas([1])


class CajaEtp3(CjG.CajaEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=apli.Trads['Simular'], núm=3, total=total)

        total_subcajas = 1
        subcajas = [CjSE.CajaSubEtp31(símismo, apli, total=total_subcajas)]

        símismo.especificar_subcajas(subcajas)

    def acción_desbloquear(símismo):
        símismo.desbloquear_subcajas([1])


class CajaEtp4(CjG.CajaEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=apli.Trads['AnálisisIncert'], núm=4, total=total)
        total_subcajas = 1
        subcajas = [CjSE.CajaSubEtp41(símismo, apli, total=total_subcajas)]

        símismo.especificar_subcajas(subcajas)

    def acción_desbloquear(símismo):
        símismo.desbloquear_subcajas([1])
