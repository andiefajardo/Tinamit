from Conectado import Conectado


modelo = Conectado()
modelo.estab_mds("F:\\Julien\\PhD\\Iximulew\\MDS 2015\\Tz'olöj Ya'\\Taller 12\\Para tinamit.vpm")
modelo.estab_bf('F:\\Julien\\PhD\\Python\\Tikon\\Tinamit.py')

modelo.conectar('mds', 'riego', 'riego')
modelo.conectar('bf', 'Rendimiento milpa', 'rendimiento_maíz')

modelo.simular(paso=1, tiempo_final=12)
