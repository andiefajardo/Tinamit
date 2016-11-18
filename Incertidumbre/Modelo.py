import io
import os
import re
import ctypes


class ModeloMDS(object):

    regex_var = NotImplemented
    lím_línea = NotImplemented

    def __init__(símismo, archivo_mds):
        """

        :param archivo_mds:
        :type archivo_mds: str
        """

        símismo.archivo_mds = archivo_mds

        # Formato {var1: {ecuación: '', unidades: '', comentarios: ''}
        símismo.vars = {}

        símismo.internos = []
        símismo.auxiliares = []
        símismo.flujos = []
        símismo.niveles = []
        símismo.constantes = []

        # Para guardar en memoria información necesaria para reescribir el documento del modelo MDS
        símismo.dic_doc = {}

        símismo.leer_modelo()

    def vacíos(símismo):
        """

        :return:
        :rtype: list
        """
        return [x for x in símismo.vars if símismo.vars[x]['ecuación'] is None]

    def detalles_var(símismo, var):
        """

        :param var:
        :type var: str

        :return:
        :rtype: dict
        """

        return símismo.vars[var]

    def leer_modelo(símismo):
        with open(símismo.archivo_mds) as d:
            símismo._leer_doc_modelo(d)

    def _gen_doc_modelo(símismo):
        raise NotImplementedError

    def _leer_doc_modelo(símismo, doc):
        raise NotImplementedError

    def _leer_var(símismo, texto):
        raise NotImplementedError

    def guardar_mds(símismo, archivo=None):
        if archivo is None:
            archivo = símismo.archivo_mds
        else:
            símismo.archivo_mds = archivo
        doc = símismo._gen_doc_modelo()
        with io.open(archivo, 'w', encoding='utf8') as d:
            d.write(doc)


class ModeloVENSIM(ModeloMDS):

    lím_línea = 80

    # l = ['abd = 1', 'abc d = 1', 'abc_d = 1', '"ab3 *" = 1', '"-1\"f" = 1', 'a', 'é = A FUNCTION OF ()',
    #      'வணக்கம்', 'a3b', '"5a"']
    regex_var = r'[^\W\d]+[\w\d_ ்]*(?=$|[\w\d_ ])[\w\d_்]*(?![\w\d_ ]*\()|".*"'
    # for i in l:
    #     print(re.findall(regex_var, i))

    def __init__(símismo, archivo_mds):
        símismo.dll = None
        super().__init__(archivo_mds=archivo_mds)

    def _leer_doc_modelo(símismo, d):

        try:
            símismo.dll = ctypes.WinDLL('C:\\Windows\\System32\\vendll32.dll')
            símismo.dll.vensim_command(('SPECIAL>LOADMODEL|%s' % símismo.archivo_mds).encode())
        except OSError:
            pass

        símismo.vars.clear()

        l_texto_temp = []
        n = 0
        símismo.dic_doc['cabeza'] = d[n]

        n += 1
        l = d[n]
        while re.search(r'', l) is None:

            while l != '\t|':
                l_texto_temp.append(l)
                n += 1
                l = d[n]

            nombre, dic_var = símismo._leer_var(texto=l_texto_temp)

            símismo.vars[nombre] = dic_var
            l_texto_temp = []

        símismo.dic_doc['cola'] = d[n:]

        for var, d_var in símismo.vars.items():
            for hijo in d_var['hijos']:
                símismo.vars[hijo]['parientes'].append(var)

        símismo.flujos.clear()
        símismo.auxiliares.clear()
        símismo.constantes.clear()
        símismo.niveles.clear()

        if símismo.dll is not None:
            tamaño_mem = 10

            for var in símismo.vars:
                mem_inter = ctypes.create_string_buffer(tamaño_mem)
                símismo.dll.vensim_get_varattrib(var.encode(), 14, mem_inter, tamaño_mem)
                tipo_var = mem_inter.raw.decode()
                if tipo_var == 'Auxiliary':
                    símismo.auxiliares.append(var)
                elif tipo_var == 'Constant':
                    símismo.constantes.append(var)
                elif tipo_var == 'Level':
                    símismo.niveles.append(var)
                else:
                    pass

            for var in símismo.constantes:
                for hijo in símismo.vars[var]['hijos']:
                    if hijo in símismo.niveles:
                        símismo.flujos.append(var)
                        símismo.constantes.remove(var)
        else:
            símismo.niveles += [x for x in símismo.vars if re.match(r'INTEG *\(', símismo.vars[x]['ec']) is not None]

            for niv in símismo.niveles:
                for flujo in símismo.vars[niv]['parientes']:
                    if flujo not in símismo.flujos:
                        símismo.flujos.append(flujo)

            símismo.auxiliares += [x for x, d in símismo.vars.items()
                                   if x not in símismo.niveles and x not in símismo.flujos
                                   and len(d['parientes'])]
            símismo.constantes += [x for x in símismo.vars if x not in símismo.niveles and x not in símismo.flujos
                                   and x not in símismo.auxiliares]

    def _gen_doc_modelo(símismo):
        dic_doc = símismo.dic_doc
        doc = ''.join([dic_doc['cabeza'], *[símismo.escribir_var(x) for x in símismo.vars], dic_doc['fin']])

        return doc

    def _leer_var(símismo, texto):
        """

        :param texto:
        :type texto: list

        :return:
        :rtype: (str, dict)
        """

        nombre = sacar_variables(texto[0], regex=símismo.regex_var, n=1)

        dic_var = {'nombre': '', 'unidades': '', 'comentarios': '', 'hijos': [], 'parientes': [], 'ec': ''}

        l_texto_temp = re.match(r' += +.*$', texto[len(nombre), :]).groups()[0]
        n = 1
        l = texto[n]
        while '\t~\t' not in l:
            l_texto_temp.append(l.remove('\t'))
            n += 1
            l = texto[n]

        ec = juntar(l_texto_temp)

        # Esto no funcionará si hay un variable que se llama "A FUNCTION OF ("
        if re.match(r'A FUNCTION OF *\(', ec) is not None:
            dic_var['ec'] = ''
        else:
            dic_var['ec'] = ec

        l_texto_temp.append(l.replace('\t~\t', ''))
        n += 1
        l = texto[n]

        while '\t~\t' not in l:
            l_texto_temp.append(l.remove('\t'))
            n += 1
            l = texto[n]
        dic_var['unidades'] = juntar(l_texto_temp)

        l_texto_temp = []

        while n != len(texto):
            l_texto_temp.append(l.remove('\t'))
            n += 1
            l = texto[n]

        dic_var['comentarios'] = juntar(l_texto_temp)

        dic_var['parientes'] = sacar_variables(texto=dic_var['ec'], regex=símismo.regex_var)

        return nombre, dic_var

    def escribir_var(símismo, var):
        """

        :param var:
        :type var: str

        :return:
        :rtype: str
        """

        dic_var = símismo.vars[var]

        if dic_var['ec'] == '':
            dic_var['ec'] = 'A FUNCTION OF (%s)' % ', '.join(dic_var['parientes'])

        texto = [var + '=\n',
                 cortar(dic_var['ec'], símismo.lím_línea, lín_1='\t', lín_otras='\t\t'),
                 cortar(dic_var['unidades'], símismo.lím_línea, lín_1='\t', lín_otras='\t\t'),
                 cortar(dic_var['comentarios'], símismo.lím_línea, lín_1='\t~\t', lín_otras='\t\t'), '\t' + '|']

        return texto


def mds(archivo_mds):
    """

    :param archivo_mds:
    :type archivo_mds: str

    :return:
    :rtype: ModeloMDS

    """
    ext = os.path.splitext(archivo_mds)[0]

    if ext == '.mdl':
        modelo = ModeloVENSIM(archivo_mds=archivo_mds)
    else:
        raise NotImplementedError('No se han implementado modelos de tipo %s' % ext)

    return modelo


def cortar(texto, máx_car, lín_1=None, lín_otras=None):

    lista = []

    while len(texto):
        if len(texto) <= máx_car:
            l = texto
        else:
            dif = máx_car - texto

            l = re.search(r'(.*)\W.[%s,]' % dif, texto).groups()[0]

        lista.append(l)
        texto = texto[len(l):]

    if lín_1 is not None:
        lista[0] = lín_1 + lista[0]

    if lín_otras is not None:
        for n, l in enumerate(lista[1:]):
            lista[n] = lín_otras + l

    return lista


def juntar(l):
    """

    :param l:
    :type l: list

    :return:
    :rtype: str
    """

    l = [x.remove('\t').replace('\\\n', ' ') for x in l]

    texto = ''.join(l)

    return texto


def sacar_variables(texto, regex, n=None):
    """

    :param texto:
    :type texto: str

    :param regex:
    :type regex: str

    :param n:
    :type n: int

    :return:
    :rtype: list
    """
    b = re.findall(regex, texto)

    if n is None:
        return b
    else:
        return b[:n]
