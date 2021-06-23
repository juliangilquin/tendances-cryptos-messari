#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""script_crypto_messari.py, écrit par Julian Gilquin, le 28/04/2021.
Dernière mise à jour le 23/06/2021.
Ce programme permet de récupérer les données de prix de cryptomonnaies sélectionnées et d'analyser les tendances des moyennes mobiles à 20 et 50 jours, afin de pouvoir sortir un signal d'achat ou de vente.
Un report pdf est créé pour chaque analyse
"""

import requests
import pprint
import json
import time
import datetime
import statistics
import sys
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

#Liste des cryptos sélectionnées
assets = ["bitcoin", "ethereum", "cardano", "dogecoin", "ripple", "polkadot", "uniswap", "litecoin", "solana", "chainlink"]

#Fait le nettoyage des anciens fichiers
subprocess.call(["sh", "./clean_report_elements.sh"])

#Variables de temps pour récupération des données
ajd = datetime.date.today()
dates_list = [ajd - datetime.timedelta(days=i) for i in range(101)]
hier = dates_list[1]
ajd_moins_100 = dates_list[100]

#Listes des assets Up et Down
up_assets = []
down_assets = []

#Fonction pour calculer les moyennes mobiles à partir des données de prix
def mm_list(serie, x):
	return [round(statistics.mean(serie[i:x+i]), 4) for i in range(x)]

#Fonction pour visualiser rapidement la direction de tendance
def get_trend(val):
	trend = "SAME"
	if val > 0:
		trend = "UP"
	elif val < 0:
		trend = "DOWN"
	return trend

for asset in assets:
	try:
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

		#Calcul des MM 20 et 50
		mm_20 = mm_list(closes, 20)
		mm_50 = mm_list(closes, 50)

		#Comparaison prix du close à MM 20
		diff_mm20 = [(closes[i] - mm_20[i]) for i in range(20)]
		#print("DIFF_MM20")
		#pprint.pprint(diff_mm20)

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
			up_assets.append(asset)
			if var_mm20[1] == "UP":
				reco = reco + "\n\nConfirmation éventuelle pour achat : MM20 à tendance haussière"  
			else: 
				reco = reco + "\n\nAttention, tendance baissière de MM20"
		if trend_list[1] == "DOWN" and trend_list[2] == "UP":
			reco = "Signal de vente. Changement de tendance de UP vers DOWN. Observer le marché pour tendance baissière éventuelle"
			down_assets.append(asset)
		print(reco)

		#Calcule l'évolution du prix actuel vs dernier close
		evo = round(((closes[0]-closes[1])/closes[1])*100, 2)

		#Titre recap
		recap_title = str(f"Analyse de {asset}\ndate : {ajd}\n\n")
		#print(recap_title)
		#Close de la veille
		close_veille = f"\nCLOSE AU {hier}: {closes[1]}"
		
		#Prix actuel
		current_price = str(f"\n\nCURRENT: {closes[0]}, ({get_trend(evo)} DEPUIS HIER : {evo}%) \n")
		#print(current_price)

		#Texte de recommandation
		printed_reco = str(f"\n{reco} \n")
		#print(printed_reco)


		#Sauvegarde la table dans un fichier csv
		table_name = f"table_{asset}_{ajd}.csv"
		outT = open(table_name, "w")
		outT.write(db_final.sort_values(["Date"], ascending=[True])[0:19].to_csv(index=False))
		outT.close()

		#Sauvegarde la reco dans un fichier texte
		reco_name = f"reco_{asset}_{ajd}.txt"
		outR = open(reco_name, "w")
		outR.write(recap_title)
		outR.write(current_price)
		outR.write(printed_reco)
		outR.close()

		#Prépare et sauvegarde le graph
		graph_name = f"graph_{asset}_{ajd}.png"
		plt.plot(db_final["Date"][1:20], db_final["Close"][1:20], label="Closes")
		plt.plot(db_final["Date"][1:20], db_final["MM20"][1:20], label="MM20")
		plt.plot(db_final["Date"][1:20], db_final["MM50"][1:20], label="MM50")
		plt.xlabel("Date")
		plt.xticks(rotation=90)
		plt.ylabel("Prix en USD")
		plt.title(f"Visuel pour {asset}")
		plt.legend()
		plt.savefig(graph_name)
		plt.clf()

		#Creation du doc pdf
		pdf_doc_name = f"Report_{asset}_{ajd}.pdf"
		doc = SimpleDocTemplate(pdf_doc_name, rightMargin=72,leftMargin=72, topMargin=72,bottomMargin=18)

		#Definition des elements
		Story = []
		with open(f"table_{asset}_{ajd}.csv", "r") as ta:
			table = ta.readlines()
		with open(f"reco_{asset}_{ajd}.txt", "r") as te:
			texte = te.readlines()
		graph = f"graph_{asset}_{ajd}.png"

		#Definition style paragraphe
		styles = getSampleStyleSheet()
		style = styles["Normal"]

		#Rajout du texte reco
		for line in texte:
			bigger_line = """<font size="15">%s</font>""" % line
			reco = Paragraph(line, style)
			Story.append(reco)
			Story.append(Spacer(1, 5))

		Story.append(Spacer(1, 25))

		#Rajout du graphe
		im = Image(graph, 8*inch, 6*inch)
		Story.append(im)
		Story.append(Spacer(1, 25))

		#Saut de page
		Story.append(PageBreak())

		#Rajout table
		reworked_table = [line.split(",") for line in table]
		table_dans_pdf = Table(reworked_table)
		Story.append(table_dans_pdf)

		#Construction finale du doc
		doc.build(Story)

		print(f"Reporting pour {asset} créé avec succès")
	except:
		print(f"Erreur lors de la création du reporting de {asset}")

	time.sleep(0.5)

print("ALERTES CRYPTOS TREND UP")
print(up_assets)

print("ALERTES CRYPTOS TREND DOWN")
print(down_assets)