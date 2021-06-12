#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""script_crypto_messari.py, écrit par Julian Gilquin, le 28/04/2021.
Dernière mise à jour le 02/06/2021.
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

#Variables de temps pour récupération des données
ajd = datetime.date.today()
dates_list = [ajd - datetime.timedelta(days=i) for i in range(101)]
hier = dates_list[1]
ajd_moins_100 = dates_list[100]

#Variable de la crypto que l'utilisateur a renseigné (ou pas)
try:
	asset = sys.argv[1]
except IndexError:
	asset = input("Entrer une devise : ")

#Récupération des données via l'API de messari
restest = requests.get(f"https://data.messari.io/api/v1/assets/{asset}/metrics/price/time-series?after={ajd_moins_100}&interval=1d")

#Chargement des données dans une variable json ou information erreur
try:
	data = json.loads(restest.text)
except (ConnectionError, Timeout, TooManyRedirects) as e:
	print(e)

#Tri des données pour récupérer les prix des closes
closes_data = [round(data["data"]["values"][i][4], 4) for i in range(len(data["data"]["values"]))]
#print("CLOSES_DATA")
#pprint.pprint(closes_data)
closes = closes_data[::-1]
#print("CLOSES")
#pprint.pprint(closes)

#Fonction pour calculer les moyennes mobiles à partir des données de prix
def mm_list(x):
	return [round(statistics.mean(closes[i:x+i]), 4) for i in range(x)]

#Calcul des MM 20 et 50
mm_20 = mm_list(20)
mm_50 = mm_list(50)

#Comparaison prix du close à MM 20
diff_mm20 = [(closes[i] - mm_20[i]) for i in range(20)]
#print("DIFF_MM20")
#pprint.pprint(diff_mm20)

#Fonction pour visualiser rapidement la direction de tendance
def get_trend(val):
	trend = "SAME"
	if val > 0:
		trend = "UP"
	elif val < 0:
		trend = "DOWN"
	return trend

#Calculer la variation du MM20 pour avoir le sens de la tendance de fond
var_mm20 = [get_trend(mm_20[i]-mm_20[i+1]) for i in range(19)]
#Rajoute le 20eme element de la liste var_mm20
var_mm20.append("N/A")
#print("VAR_MM20")
#pprint.pprint(var_mm20)

#Preparer la liste de tendance ave comparaison cours de cloture vs mm20
trend_list = [get_trend(diff_mm20[i]) for i in range(20)]

#Calcule les ecarts entre mm20 et mm50
ecart_mms = [mm_20[i]-mm_50[i] for i in range(20)]

#Compile la bdd finale
db_final = pd.DataFrame(
	{"Date": dates_list[:20],
	"Close": closes[:20],
	"Trend": trend_list[:20],
	"MM20": mm_20[:20],
	"Var. MM20": var_mm20[:20],
	"MM50": mm_50[:20], 
	"DIFF MM20-50": ecart_mms[:20]
	})

#Prepare le texte de recommandation selon le contexte final
reco = f"Pas de changement de tendance sur dernier close : {trend_list[1]}"
if trend_list[1] == "UP" and trend_list[2] == "DOWN":
	reco = "Signal d'achat. Changement de tendance de DOWN vers UP. Observer le marché pour tendance haussière éventuelle"
	confirmation_mms = "Confirmation éventuelle pour achat : MM20 à tendance haussière" if var_mm20[1] == "UP" else "Attention, tendance baissière de MM20"
if trend_list[1] == "DOWN" and trend_list[2] == "UP":
	reco = "Signal de vente. Changement de tendance de UP vers DOWN. Observer le marché pour tendance baissière éventuelle"

#Calcule l'évolution du prix actuel vs dernier close
evo = round(((closes[0]-closes[1])/closes[1])*100, 2)

#Imprime le taleau recap
print("\n", db_final.sort_values(["Date"], ascending=[True])[0:19].to_string(index=False))
#print("\n"f"CLOSE AU {hier}:", closes[1])
#Imprime le prix actuel
print("\nCURRENT:", closes[0], f"({get_trend(evo)} DEPUIS HIER : {evo}%)", "\n")
#Imprime le texte de recommandation et si jamais le texte de confirmation
print(reco, "\n")
try:
	print(confirmation_mms, "\n")
except:
	pass

#Prépare et imprime le graph
plt.plot(db_final["Date"], db_final["Close"], label="Closes")
plt.plot(db_final["Date"], db_final["MM20"], label="MM20")
plt.plot(db_final["Date"], db_final["MM50"], label="MM50")
plt.xlabel("Date")
plt.ylabel("Prix en USD")
plt.title("Visuel")
plt.legend()
plt.show()