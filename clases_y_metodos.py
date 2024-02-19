#Acá definimos las clases

#Clase Check_fecha
from datetime import date
from datetime import datetime
from datetime import timedelta

"""Esto para restringir los input de fechas, para que no sea anterior a 2 años
para atras, porque la API no brinda esa info sin pagar. Y ademas verifica que
la segunda fecha sea posterior a la primera"""

class Check_fecha:
  #Inicializador:
  def __init__(self, fecha):
    self.fecha = fecha

  #Métodos:
  def fecha_tope(self):
    now = date.today()
    fecha_tope = now - timedelta(days = 365*2)
    return fecha_tope

  def fecha_consulta_min(self):
    año_min = int(self.fecha[0:4])
    mes_min = int(self.fecha[5:7])
    dia_min = int(self.fecha[8:10])
    fecha_consulta_min = date(año_min, mes_min, dia_min) - timedelta(days = 7)
    return fecha_consulta_min

  def fecha_consulta_max(self):
    año_max = int(self.fecha[0:4])
    mes_max = int(self.fecha[5:7])
    dia_max = int(self.fecha[8:10])
    fecha_consulta_max = date(año_max, mes_max, dia_max) + timedelta(days = 7)
    return fecha_consulta_max

  def fecha_ini(self):
    año = int(self.fecha[0:4])
    mes = int(self.fecha[5:7])
    dia = int(self.fecha[8:10])
    fecha_ini = date(año, mes, dia)
    while fecha_ini < self.fecha_tope():
      print(f"Por favor ingrese una fecha de inicio posterior o igual al {self.fecha_tope()} ")
      fecha_i = input(f'Ingrese la fecha de inicio: (Formato: AAAA-MM-DD) ')
      año = int(fecha_i[0:4])
      mes = int(fecha_i[5:7])
      dia = int(fecha_i[8:10])
      fecha_ini = date(año, mes, dia)
    return fecha_ini

  def fecha_fin(self, fecha_ini):
    año = int(self.fecha[0:4])
    mes = int(self.fecha[5:7])
    dia = int(self.fecha[8:10])
    fecha_fin = date(año, mes, dia)
    while fecha_fin < fecha_ini:
      print(f"Por favor ingrese una fecha de fin posterior o igual al {fecha_ini}")
      fecha_f = input(f'Ingrese la fecha de fin: (Formato: AAAA-MM-DD) ')
      año = int(fecha_f[0:4])
      mes = int(fecha_f[5:7])
      dia = int(fecha_f[8:10])
      fecha_fin = date(año, mes, dia)
    return fecha_fin

#Clase Rango_fechas:
class Rango_fechas:
  def __init__(self, fecha_ini, fecha_fin):
    self.fecha_ini = fecha_ini
    self.fecha_fin = fecha_fin

  #Métodos:
  def fechas_para_pd(self): #Nos quedamos con los días hábiles dentro del rango solicitado en formato pandas
    us_bd = CustomBusinessDay(calendar = USFederalHolidayCalendar())
    fechas_para_pd = pd.date_range(start = self.fecha_ini, end = self.fecha_fin, freq = us_bd)
    return fechas_para_pd


  def fechas_para_db(self):
    aux = self.fechas_para_pd().strftime("%Y-%m-%d")
    fechas_para_db = list(aux)
    viernes_santos = ['2022-04-15', '2023-04-07', '2024-03-29'] #Hubo que sacarle a mano los viernes santos...
    for viernes in viernes_santos:
      if (viernes in fechas_para_db) == True:
        fechas_para_db.remove(viernes)
    return fechas_para_db

  def fechas_dif(self, fechas: list):
    fechas_dif = (self.fechas_para_db()).copy()
    for k in fechas:
      if (k in fechas_dif) == True:
        fechas_dif.remove(k)
    return fechas_dif

  def indices(self, fechas_dif: list):
    indices = []
    fechas_para_db = self.fechas_para_db()
    for k in fechas_dif:
      indices.append(fechas_para_db.index(k))
    return indices

  def intervalos_vacios(self, indices):
    intervalos_vacios = []
    intervalos_vacios.append(indices[0])
    for k in range(len(indices)-1):
      if indices[k+1] != indices[k]+1:
        intervalos_vacios.append(indices[k])
        intervalos_vacios.append(indices[k+1])
    intervalos_vacios.append(indices[-1])
    return intervalos_vacios

  def intervalos_llenos(self, intervalos_vacios):
    intervalos_llenos = []
    for i in range(int(len(intervalos_vacios)/2)-1):
      intervalos_llenos.append(intervalos_vacios[2*i+1]+1)
      intervalos_llenos.append(intervalos_vacios[2*i+2]-1)
    return intervalos_llenos

class Consulta:
  #Inicializador:
  def __init__(self, archivo: str):
    self.archivo = archivo

  #Metodo:
  def resumen_db(self):
    con = sqlite3.connect(f"{self.archivo}.db")
    cur = con.cursor()
    ticker_fecha_aux = cur.execute(f"SELECT ticker, date FROM coti ORDER BY ticker ASC, date ASC")
    ticker_fecha = list(ticker_fecha_aux.fetchall()) #Lista de tuplas, con ticker, fecha
    repuesta = []
    print("Lo guardado en la db es:")

    #Nos da los ticker que figuran en la db
    lista_ticker_aux = [] #Set de los tickers
    for i in range(len(ticker_fecha)):
      lista_ticker_aux.append(ticker_fecha[i][0])
    lista_ticker = sorted(list(set(lista_ticker_aux)))

    #Nos da un rango de fechas para "empezar la consulta"
    lista_fecha_aux = [] #Set de las fechas
    for i in range(len(ticker_fecha)):
      lista_fecha_aux.append(ticker_fecha[i][1])
    lista_fecha = sorted(list(set(lista_fecha_aux)))
    fecha_min = Check_fecha(lista_fecha[0]).fecha_consulta_min()
    fecha_max = Check_fecha(lista_fecha[-1]).fecha_consulta_max()

    # #Hay que extraer de aca lo que ya esta en la db y guardarlo en llenos
    consulta_total = {}
    for ticker in lista_ticker:
      consulta_fechas_aux = cur.execute(f"SELECT date FROM coti WHERE ticker LIKE {ticker!r} ORDER BY date ASC")
      consultas_fechas = list(ticker_fecha_aux.fetchall()) #Lista de tuplas
      consulta_por_ticker = []

      #Armamos una lista con las fechas que figuran en la db, para un ticker dado
      for i in range(len(consultas_fechas)):
        consulta_por_ticker.append(consultas_fechas[i][0])
        consulta_total[ticker] = consulta_por_ticker


    #Ver entre estas fechas, que hay guardado en la db
    rango_fechas = Rango_fechas(fecha_min, fecha_max)
    rango_fechas_consulta_para_db = rango_fechas.fechas_para_db()


    for i in range(0,len(lista_ticker)):

      fechas = consulta_total[lista_ticker[i]]

      diferencias = rango_fechas.fechas_dif(fechas)

      indices = rango_fechas.indices(diferencias)

      vacios = rango_fechas.intervalos_vacios(indices)

      llenos = rango_fechas.intervalos_llenos(vacios)


      for n in (range(0,len(llenos),2)):
        j = llenos[n]
        k = llenos[n+1]
        fecha_ini = rango_fechas_consulta_para_db[j]
        fecha_fin = rango_fechas_consulta_para_db[k]
        print(f'{lista_ticker[i]}: {fecha_ini} <-> {fecha_fin}')

      con.close()

#Clase Coti

import requests
import pandas as pd
import numpy as np
import sqlite3
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay
import matplotlib.pyplot as plt


class Coti:
  #Inicializador:
  def __init__(self, ticker, fecha_ini, fecha_fin):
    self.ticker = ticker.upper()
    self.fecha_ini = fecha_ini
    self.fecha_fin = fecha_fin

  #Métodos:
  def fechas_para_pd(self): #Nos quedamos con los días hábiles dentro del rango solicitado en formato pandas
    us_bd = CustomBusinessDay(calendar = USFederalHolidayCalendar())
    fechas_para_pd = pd.date_range(start = self.fecha_ini, end = self.fecha_fin, freq = us_bd)
    return fechas_para_pd

  def dato(self): #Hacemos el llamado a la api, y guarda lo pedido en la variable dato, devuelve un diccionario con los resultados
    dato = requests.get(f'https://api.polygon.io/v2/aggs/ticker/{(self.ticker)}/range/1/day/{self.fecha_ini}/{self.fecha_fin}?adjusted=true&sort=asc&limit=5000&apiKey=C564RQLrE8spm47d35eQpZERpNfgD3IJ')
    d = dato.json()
    resultados = d['results']
    return resultados

  def fechas_para_db(self):
    aux = self.fechas_para_pd().strftime("%Y-%m-%d")
    fechas_para_db = list(aux)
    viernes_santos = ['2022-04-15', '2023-04-07', '2024-03-29']
    for viernes in viernes_santos:
      if (viernes in fechas_para_db) == True:
        fechas_para_db.remove(viernes)
    return fechas_para_db

  def valores_db(self, resultados: dict): #Pasamos a una lista, porque la db lo necesita en este formato
    valores_db = []
    lista_aux = []
    fechas_para_db = self.fechas_para_db()
    for i in range(len(fechas_para_db)):
        fechas_aux = fechas_para_db
        lista_aux.append(self.ticker)
        lista_aux.append(fechas_para_db[i])

        for j in range(len(resultados[0].values())):
          valores_aux = list(resultados[i].values())
          lista_aux.append(valores_aux[j])

        valores_db.append(tuple(lista_aux))
        lista_aux = []
    return valores_db

  def crear_archivo_db(self, archivo: str):
    con = sqlite3.connect(f"{archivo}.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE coti(ticker, date, v, vw, open, close, highest, lowest, t, n)")
    con.close()

  def escritura_db(self, data: list, archivo: str):
    con = sqlite3.connect(f"{archivo}.db")
    cur = con.cursor()
    cur.executemany("INSERT INTO coti VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
    con.commit()  # Remember to commit the transaction after executing INSERT.
    escri_aux = cur.execute("SELECT * FROM coti")
    res_aux = escri_aux.fetchall()
    con.close()
    return res_aux

  def chequeo(self, archivo: str): #Esta función te dice si el pedido realizado figura completo en la db o no
    con = sqlite3.connect(f"{archivo}.db")
    cur = con.cursor()
    cheq_aux = cur.execute(f'''SELECT ticker, date FROM coti WHERE (ticker LIKE {self.ticker!r} 
                           AND date BETWEEN {self.fecha_ini!r} AND {self.fecha_fin!r})
                           ORDER BY date ASC''')
    cheq = cheq_aux.fetchall()
    con.close()
    if len(cheq) == len(self.fechas_para_db()): #Modificado
      return 0
    elif len(cheq) == 0:
      return 1
    else:
      return 2

  def llamado(self, archivo: str):
    if self.chequeo(archivo) == 0:
      print(f"Lo solicitado ya figura en la base de datos {archivo}.db")
    elif self.chequeo(archivo) == 1:
      dato = self.dato()
      valores = self.valores_db(dato)
      escritura = self.escritura_db(valores, archivo)
      print(f"Lo solicitado se guardó en la base de datos {archivo}.db")
    elif self.chequeo(archivo) == 2:
      ticker = self.ticker
      con = sqlite3.connect(f"{archivo}.db")
      cur = con.cursor()
      fechas_aux = cur.execute(f"SELECT date FROM coti WHERE ticker LIKE {self.ticker!r} AND date BETWEEN {self.fecha_ini!r} AND {self.fecha_fin!r} ORDER BY date ASC")
      fechas_re_aux = fechas_aux.fetchall()
      fechas = []
      for i in range(len(fechas_re_aux)):
        fechas.append(fechas_re_aux[i][0])
      rango_fechas = Rango_fechas(self.fecha_ini, self.fecha_fin)
      rango_fechas_para_db = rango_fechas.fechas_para_db()
      diferencias = rango_fechas.fechas_dif(fechas)
      indices = rango_fechas.indices(diferencias)
      vacios = rango_fechas.intervalos_vacios(indices)
      llenos = rango_fechas.intervalos_llenos(vacios)
      for i in (range(0,len(vacios),2)):
        j = vacios[i]
        k = vacios[i+1]
        fecha_ini = rango_fechas_para_db[j]
        fecha_fin = rango_fechas_para_db[k]
        fechas_vacios = Rango_fechas(fecha_ini, fecha_fin)
        coti = Coti(ticker, fecha_ini, fecha_fin)
        print(f'Se esta guardando: {coti.ticker}, {coti.fecha_ini}, {coti.fecha_fin}')
        dato = coti.dato()
        valores = coti.valores_db(dato)
        escritura = coti.escritura_db(valores, archivo)
      con.close()
      print("Los datos indicados se guardaron en la db")
      return 


  def grafico(self, archivo: str, seleccion:str): #Graficamos lo solicitado en función de la fecha
    con = sqlite3.connect(f"{archivo}.db")
    cur = con.cursor()
    elem_aux = Coti(self.ticker, self.fecha_ini, self.fecha_fin)
    escri_aux = cur.execute(f"SELECT date, {seleccion} FROM coti WHERE ticker LIKE {self.ticker!r} AND date BETWEEN {self.fecha_ini!r} AND {self.fecha_fin!r} ORDER BY date ASC")
    res_aux = escri_aux.fetchall()

    xy_aux = []
    x = []
    y = []
    for i in range(len(res_aux)):
      xy_aux.append(res_aux[i])
      y.append(xy_aux[0][1])
      x.append(xy_aux[0][0])
      xy_aux = []
    plt.plot(x,y)
    plt.title(f'Cotizaciones {seleccion!r} de {elem_aux.ticker} entre {elem_aux.fecha_ini} y {elem_aux.fecha_fin}')
    con.close()