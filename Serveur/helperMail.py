#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import sys
import os
 
from smtplib import SMTP
from email import Encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formatdate
 
##############################################################################
class ServeurSMTP(object):
    def __init__(self, adresse="", port=25, login="", mdpasse=""):
        """conserve les paramètres d'un compte mail sur un serveur SMTP"""
        self.adresse = adresse
        self.port = port
        self.login = login
        self.mdpasse = mdpasse
 
##############################################################################
class MessageSMTP(object):
 
    def __init__(self, exped="", to=[], cc=[], bcc=[], sujet="", corps="", pjointes=[], codage='UTF-8', typetexte='plain'):
        """fabrique un mail empaqueté correctement à partir des données détaillées"""
 
        # préparation des données
        self.expediteur = exped
        if type(pjointes)==str or type(pjointes)==unicode:
            pjointes = pjointes.split(';')
        if codage==None or codage=="":
            codage = 'UTF-8'
        if to==[] or to==['']:
            self.destinataires = []
            self.mail = ""
            raise ValueError ("échec: pas de destinataire!")
 
        # construction du mail à envoyer (en-tête + corps)
 
        if pjointes==[]:
            # message sans pièce jointe
            msg = MIMEText(corps.encode(codage), typetexte, _charset=codage)
        else:
            # message "multipart" avec une ou plusieurs pièce(s) jointe(s)
            msg = MIMEMultipart('alternatives')
 
        msg['From'] = exped
        msg['To'] = ', '.join(to)
        msg['Cc'] = ', '.join(cc)
        msg['Bcc'] = ', '.join(bcc)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = sujet.encode(codage)
        msg['Charset'] = codage
        msg['Content-Type'] = 'text/' + typetexte + '; charset=' + codage
 
        if pjointes!=[]:
            msg.attach(MIMEText(corps.encode(codage), typetexte, _charset=codage))
 
            # ajout des pièces jointes
            for fichier in pjointes:
                part = MIMEBase('application', "octet-stream")
                try:
                    f = open(fichier,"rb")
                    part.set_payload(f.read())
                    f.close()
                except:
                    coderr = "%s" % sys.exc_info()[1]
                    raise ValueError ("échec à la lecture d'un fichier joint (" + coderr + ")")
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename="%s" % os.path.basename(fichier))
                msg.attach(part)
 
        # compactage final du message dans les 2 cas (avec ou sans pièce(s) jointe(s))
        self.mail = msg.as_string()
 
        # construction de la liste complète de tous les destinataires (to + cc + bcc)
        self.destinataires = to
        self.destinataires.extend(cc)
        self.destinataires.extend(bcc)
 
##############################################################################
def envoieSMTP(message, serveur):
    """envoie le message correctement compacté au serveur SMTP donné"""
    try:
        smtp = SMTP(serveur.adresse, serveur.port)
    except:
        coderr = "%s" % sys.exc_info()[1]
        return u"échec à la connexion (" + coderr + ")"
 
    # smtp.set_debuglevel(1)  # à décommenter pour avoir tous les échanges du protocole dans la console
    if serveur.login != "":
        try:
            smtp.login(serveur.login, serveur.mdpasse)
        except:
            coderr = "%s" % sys.exc_info()[1]
            smtp.quit()
            return u"échec: mauvais login/mdpasse (" + coderr + ")"
    try:
        rep = smtp.sendmail(message.expediteur, message.destinataires, message.mail)
    except:
        coderr = "%s" % sys.exc_info()[1]
        smtp.quit()
        return u"échec à l'envoi de mail (" + coderr + ")"
    smtp.quit()
    return rep
