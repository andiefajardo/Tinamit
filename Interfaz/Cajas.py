import tkinter as tk

from Interfaz import Formatos as Fms
from Interfaz import Botones as Bts


class CajaIzquierda(object):
    def __init__(símismo, apli, pariente, imgs):

        símismo.caja = tk.Frame(pariente, **Fms.formato_cajas)
        # Crear las líneas de progreso y las cajas necesarias para contenerlas
        cj_líns_izq = tk.Frame(símismo.caja, **Fms.formato_cajas)
        símismo.líneas = {}
        for i in range(1, 5):
            símismo.líneas[str(i)] = tk.Canvas(cj_líns_izq, **Fms.formato_lín_bts)
            símismo.líneas[str(i)].col = Fms.color_bts[str(i)]

        # Crear la los botones de navigación y las cajas necesarias para contenerlos
        cj_bts_izq = tk.Frame(símismo.caja, **Fms.formato_cajas)
        símismo.bts = {}
        for i in range(1, 5):
            símismo.bts[str(i)] = Bts.BotónIzq(apli=apli, pariente=cj_bts_izq, lín=símismo.líneas[str(i)], núm=i,
                                               img=imgs['img_bt_%i' % i], img_bloc=imgs['img_bt_%i_bloc' % i],
                                               img_sel=imgs['img_bt_%i_sel' % i], **Fms.formato_bts_cent)

        for l in range(1, len(símismo.líneas) + 1):
            símismo.líneas[str(l)].pack(**Fms.emplacimiento_lín_bts)
        cj_líns_izq.pack(side='right')

        for b in range(1, len(símismo.bts) + 1):
            símismo.bts[str(b)].bt.pack(**Fms.emplacimiento_bts_cent)
        cj_bts_izq.pack(side='right')

        símismo.caja.place(**Fms.emplacimiento_cj_izq)

    def activar(símismo, núm):
        n = str(núm)
        símismo.bts[n].activar()
        símismo.líneas[n].configure(bg=símismo.líneas[n].col)

    def desactivar(símismo, núm):
        n = str(núm)
        símismo.bts[n].desactivar()
        símismo.líneas[n].configure(bg='#C3C3C3')


class CajaTrabajo(object):
    def __init__(símismo, apli, pariente, núm, imgs):
        símismo.núm = núm
        símismo.caja = tk.Frame(pariente, **Fms.formato_cajas_trab)

        prueba = tk.Label(símismo.caja, text='prueba%i' % núm, bg='white')
        prueba.pack()

        if núm > 1:
            símismo.bt_anterior = Bts.Botón(símismo.caja, comanda=apli.ir_atrás,
                                            img=imgs['bt_ant'], img_sel=imgs['bt_ant_sel'],
                                            img_bloc=imgs['bt_ant_bloc'],
                                            **Fms.formato_bts_ant_sig)
            símismo.bt_anterior.bt.place(**Fms.emplacimiento_bt_anterior)

        if núm < 4:
            símismo.bt_siguiente = Bts.Botón(símismo.caja, comanda=apli.ir_adelante,
                                             img=imgs['bt_sig'], img_sel=imgs['bt_sig_sel'],
                                             img_bloc=imgs['bt_sig_bloc'],
                                             **Fms.formato_bts_ant_sig)
            símismo.bt_siguiente.bt.place(**Fms.emplacimiento_bt_siguiente)

        símismo.caja.place(**Fms.emplacimiento_cajas_trab)

    def traer(símismo):
        símismo.caja.lift()

    def quitar(símismo):
        símismo.caja.lower()
