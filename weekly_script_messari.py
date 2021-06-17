#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""weekly_script_messari.py, écrit par Julian Gilquin, le 17/06/2021.
Dernière mise à jour le 17/06/2021.
Inspiration des programmes script_crypto_messari.py et get_data_for_backtest.py.
Ce programme permet de récupérer les données de prix à la semaine d'une cryptomonnaie souhaitée et d'analyser les tendances des moyennes mobiles à 20 et 50 jours, afin de pouvoir sortir un signal d'achat ou de vente.
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
start_date = "2015-01-01"
#x_days = 1000
#dates_list = [ajd - datetime.timedelta(days=i) for i in range(x_days+1)]
#hier = dates_list[1]
#ajd_moins_x = dates_list[x_days]

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
restest = requests.get(f"https://data.messari.io/api/v1/assets/{asset}/metrics/price/time-series??start={start_date}&end={ajd}&interval=1w&columns=close,volume&format=csv")
the_data = restest.text
#Enregistrement des donnees en csv
out_csv = open(f"weekly_data.csv", "w")
out_csv.write(the_data)
out_csv.close()

#Chargement des donnees avec pandas et recup nb lignes
raw_data = pd.read_csv("weekly_data.csv")
#print(raw_data)
raw_data["close"] = round(raw_data["close"], 4)
lrd = len(raw_data)

#Calcul valeurs de moyennes mobiles
mm20_values = []
for i in range(20):
	mm20_values.append(None)
for i in range(20, lrd):
	mm20_values.append(round(statistics.mean(raw_data["close"][i-20:i]), 4))


mm50_values = []
for i in range(50):
	mm50_values.append(None)
for i in range(50, lrd):
	mm50_values.append(round(statistics.mean(raw_data["close"][i-50:i]), 4))

#Calcul autres colonnes
close_vs_mm20 = []
for i in range(20):
	close_vs_mm20.append(None)
for i in range(20, lrd):
	close_vs_mm20.append((raw_data["close"][i] - mm20_values[i]))

trend_close_mm20 =[]
for i in range(20):
	trend_close_mm20.append(None)
for i in range(20, lrd):
	if close_vs_mm20[i] >= 0:
		trend_close_mm20.append("UP")
	else:
		trend_close_mm20.append("DOWN")

trend_mm20 = []
for i in range(21):
	trend_mm20.append(None)
for i in range(21, lrd):
	if mm20_values[i] - mm20_values[i-1] > 0:
		trend_mm20.append("UP")
	else:
		trend_mm20.append("DOWN")

close_crossed_mm20 = []
for i in range(21):
	close_crossed_mm20.append(None)
for i in range(21, lrd):
	if trend_close_mm20[i] == trend_close_mm20[i-1]:
		close_crossed_mm20.append("NO")
	else:
		close_crossed_mm20.append("YES")

#Insertion donnees dans table
raw_data["close_vs_mm20"] = close_vs_mm20
raw_data["trend_close_mm20"] = trend_close_mm20
raw_data["trend_mm20"] = trend_mm20
raw_data["mm20_values"] = mm20_values
raw_data["mm50_values"] = mm50_values
raw_data["close_crossed_mm20"] = close_crossed_mm20

#Affichage table
recap_title = str(f"Analyse weekly de {asset}\ndate : {ajd}\n\n")
print(recap_title)
table = raw_data.sort_values(["timestamp"], ascending=[True])[(lrd-20):lrd].to_string(index=False)
print(table)

#Prépare et sauvegarde le graph
plt.plot(raw_data["timestamp"], raw_data["close"], label="weekly closes")
plt.plot(raw_data["timestamp"], raw_data["mm20_values"], label="MM20")
plt.plot(raw_data["timestamp"], raw_data["mm50_values"], label="MM50")
plt.xlabel("Date")
plt.xticks(rotation=90)
plt.ylabel("Prix en USD")
plt.title(f"Visuel pour {asset}")
plt.legend()
#plt.savefig(f"weekly_graph_{asset}_{ajd}.png")
plt.show()