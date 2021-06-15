#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""get_data_for_backtest.py, écrit par Julian Gilquin, le 14/06/2021.
Dernière mise à jour le 14/06/2021.
Ce programme permet de récupérer les données de prix d'une cryptomonnaie souhaitée et de les extraire en csv pour backtester la stratégie des moyennes mobiles.
"""

import requests
import pprint
import json
import time
import datetime
import statistics
import sys
import pandas as pd
import matplotlib.pyplot as plt

#Variables de temps pour récupération des données
ajd = datetime.date.today()
x_days = 1000
dates_list = [ajd - datetime.timedelta(days=i) for i in range(x_days+1)]
hier = dates_list[1]
ajd_moins_x = dates_list[x_days]

#Variable de la crypto que l'utilisateur a renseigné (ou pas)
try:
	asset = sys.argv[1]
except IndexError:
	asset = input("Entrer une devise : ")

#Recupère les autres arguments si plusieurs ont été renseignés
if len(sys.argv) > 2:
	args_de_trop = ", ".join(sys.argv[2:])
	print(f"{args_de_trop} n'ont pas pu êre traités")

#Récupération des données via l'API de messari en csv
restest = requests.get(f"https://data.messari.io/api/v1/assets/{asset}/metrics/price/time-series??start={ajd_moins_x}&end={ajd}&interval=1d&columns=close,volume&format=csv")
the_data = restest.text
#Enregistrement des donnees en csv
out_csv = open(f"raw_data.csv", "w")
out_csv.write(the_data)
out_csv.close()
#Chargement des donnees avec pandas
raw_data = pd.read_csv("raw_data.csv")
raw_data = raw_data.sort_values(["timestamp"], ascending=[False])

#Calcul autres valeurs de moyennes mobiles
mm20_values = [round(statistics.mean(raw_data["close"][i:20+i]), 4) for i in range(len(raw_data["close"])-20)]
for i in range(20):
	mm20_values.append(None)

mm50_values = [round(statistics.mean(raw_data["close"][i:50+i]), 4) for i in range(len(raw_data["close"])-50)]
for i in range(50):
	mm50_values.append(None)

#Insertion donnees dans table
raw_data["mm20_values"] = mm20_values
raw_data["mm50_values"] = mm50_values

#Enregistrement de la table en csv
raw_data = raw_data.sort_values(["timestamp"], ascending=[True])
raw_data.to_csv("raw_data.csv")