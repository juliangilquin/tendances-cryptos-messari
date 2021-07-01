#!/usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib, ssl
import getpass
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender_mail = "caso.alerts@gmail.com"
receiver_mail = "caso.alerts@gmail.com"

subject = "VOICI LE SUBJECT"
body = """\


Coucou depuis Python !!!"""

port = 465 #SSL
password = getpass.getpass(prompt="MDP de boite mail pour envoi du mail: \n")

#Creation du mail et headers
message = MIMEMultipart()
message["From"] = sender_mail
message["To"] = receiver_mail
message["Subject"] = subject
message["Bcc"] = receiver_mail

#Corps du mail
message.attach(MIMEText(body, "plain"))

#Gestion de la pj
filename = "Report_bitcoin_2021-06-23.pdf"
with open(filename, "rb") as attachment:
	part = MIMEBase("application", "octet-stream")
	part.set_payload(attachment.read())

#Encodage pj et ajout info dans headers du mail
encoders.encode_base64(part)
part.add_header("Content-Disposition", f"attachment; filename= {filename}")

#Ajout pj au mail et conversion en caractere
message.attach(part)
text = message.as_string()


#Creation context SSL secure
context = ssl.create_default_context()

with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
	server.login(sender_mail, password)
	server.sendmail(sender_mail, receiver_mail, text)