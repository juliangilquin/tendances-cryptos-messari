# tendances-cryptos-messari

Ce programme se connecte à l'API de https://messari.io/ pour traiter et analyser le prix de 15 crypto-actifs pré-sélectionnés de facon presque aléatoire.
Après le calcul et la modélisation des courbes de moyennes mobiles à 20 et 50 jours, des rapports pdf sont automatiquement générés avec un éventuel signal d'achat ou de vente. 
Ces rapports sont ensuite envoyés par e-mail. L'utilisateur devra simplement rentrer le mot de passe d'accès à sa boite mail en ligne de commande.

Les fichiers backtest.py et le fichier Excel du même nom permettent de récupérer les informations depuis l'API au format csv, et d'effectuer des calculs statistiques non-savants sur les données récupérées pour déterminer si la stratégie est rentable ou non. Ces calculs sont mis à jour automatiquement à chaque fois que le script est lancé.

Les informations traités et les conclusions des rapports ne constituent EN AUCUN CAS des conseils d'investissements avisés. 
Cette analyse est réalisé par pur intérêt de découverte et de manipulation des outils techniques, et ne se base sur aucune expertise financière. 
Il est donc recommandé à l'utilisateur d'utiliser ces informations avec tout le discernement nécessaire.

Au travers de ce programme, voici les skills/outils développés/utilisés:
-Connexion à une API en ligne
-Création de base de données avec le module Pandas
-Calcul de variables sur les informations récupérées dans le call d'API
-Mise en graphique des résultats avec le module matplotlib
-Sauvegarde des graphiques au format png
-Sauvegarde des données au format csv
-Création automatisée de rapports au format pdf
-Connexion à une boite mail et envoi de message avec pièce jointe

Mais également avec les fichiers de backtest:
-Récupération des données au format csv via l'API
-Intégration des données dans un fichier Excel avec Power Query pour faciliter la mise à jour
-Mise en graphique des données dans Excel
-Calculs sur les données récupérées à chaque mise à jour
