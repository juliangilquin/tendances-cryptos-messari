#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""gamescript.py, écrit par Julian Gilquin, le 28/04/2021.
Dernière mise à jour le 31/05/2021.
Ce programme permet de récupérer les données de prix d'une cryptomonnaie souhaitée et d'analyser les tendances des moyennes mobiles à 20 et 50 jours, afin de pouvoir sortir un signal d'achat ou de vente.
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

ajd = datetime.date.today()
dates_list = [ajd - datetime.timedelta(days=i) for i in range(101)]
hier = dates_list[1]
ajd_moins_100 = dates_list[100]

try:
	asset = sys.argv[1]
except IndexError:
	asset = input("Entrer une devise : ")

restest = requests.get(f"https://data.messari.io/api/v1/assets/{asset}/metrics/price/time-series?after={ajd_moins_100}&interval=1d")

try:
	data = json.loads(restest.text)
except (ConnectionError, Timeout, TooManyRedirects) as e:
	print(e)

closes_data = [round(data["data"]["values"][i][4], 4) for i in range(len(data["data"]["values"]))]
closes = closes_data[::-1]

def mm_list(x):
	return [round(statistics.mean(closes[i:x+i]), 4) for i in range(x)]

mm_20 = mm_list(20)
mm_50 = mm_list(50)

diff_mm20 = [(closes[i] - mm_20[i]) for i in range(20)]

def get_trend(val):
	trend = "SAME"
	if val > 0:
		trend = "UP"
	elif val < 0:
		trend = "DOWN"
	return trend

trend_list = [get_trend(diff_mm20[i]) for i in range(20)]

ecart_mms = [mm_20[i]-mm_50[i] for i in range(20)]

db_final = pd.DataFrame(
	{"Date": dates_list[:20],
	"Trend": trend_list[:20],
	"Close": closes[:20],
	"MM20": mm_20[:20],
	"MM50": mm_50[:20], 
	"DIFF MM20-50": ecart_mms[:20]
	})

reco = f"Pas de changement de tendance sur dernier close : {trend_list[1]}"
if trend_list[1] == "UP" and trend_list[2] == "DOWN":
	reco = "Signal d'achat. Changement de tendance de DOWN vers UP. Observer le marché pour tendance haussière éventuelle"
	confirmation_mms = "Confirmation éventuelle pour achat : MM20 supérieur à MM50" if ecart_mms[1] >= 0 else "Attention, MM20 inférieur à MM50"
if trend_list[1] == "DOWN" and trend_list[2] == "UP":
	reco = "Signal de vente. Changement de tendance de UP vers DOWN. Observer le marché pour tendance baissière éventuelle"

evo = round(((closes[0]-closes[1])/closes[1])*100, 2)

print("\n", db_final.sort_values(["Date"], ascending=[True])[0:19].to_string(index=False))
#print("\n"f"CLOSE AU {hier}:", closes[1])
print("\nCURRENT:", closes[0], f"({get_trend(evo)} DEPUIS HIER : {evo}%)", "\n")
print(reco, "\n")
try:
	print(confirmation_mms, "\n")
except:
	pass

plt.plot(db_final["Date"], db_final["Close"], label="Closes")
plt.plot(db_final["Date"], db_final["MM20"], label="MM20")
plt.plot(db_final["Date"], db_final["MM50"], label="MM50")
plt.xlabel("Date")
plt.ylabel("Prix en USD")
plt.title("Visuel")
plt.legend()
plt.show()