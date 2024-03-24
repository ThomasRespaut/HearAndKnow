from django.db import models
import datetime
import openai
from .secrets import API_KEY

class Meeting(models.Model):
    title = models.CharField(max_length=255)
    id_patient = models.IntegerField()
    discussion = models.TextField()
    meeting_date = models.DateField(default=datetime.date.today)
    bilan = models.TextField()
    def create_bilan(self,cat,permission):
        if(cat=='proche'):
            message = [
                {"role": "system", "content":
                f'''"Assistance Virtuelle pour synthétiser une interaction entre un un Patient Atteint de la Maladie d'Alzheimer et un(e) proche
                Contexte:
                Vous êtes un assistant visrtuel capable de synthétiser des échanges entre patients et un proche permettant de tirer des informations personnelles et pertinentes sur un patient suite à un dialogue.
                
                Vous devez suivre le format suivant : 
                
                Date du rendez-vous : ../../.. 
                
                Catégorie de l'utilisateur : Proche
                
                Titre : 
                
                Proche : ...
                Patient : ...
                Proche : ...
                Patient : ...
                Proche : ... 
                
                En prenant en compte la présence d'un proche et d'un patient atteint de la maladie d'Alzheimer.
                
                N'oublie pas d'être très synthètique et ne garder seulement les informations pertinentes
                
                Ensuite tu écriras un court résumé de la discussion afin de garder seulement les informations pertinentes dans l'interaction du proche et du patient.
                
                Ecrire un text brut'''
                },
                {"role": "user", "content": f" ID du patient :{self.id_patient}, Date du rdv : {self.meeting_date}, Discussion : {self.discussion} "}
            ]
        if (cat=='famille'):
            message = [
                {"role": "system", "content":
                    f'''"Assistance Virtuelle pour synthétiser une interaction entre un un Patient Atteint de la Maladie d'Alzheimer et un membre de sa famille
                Contexte:
                Vous êtes un assistant visrtuel capable de synthétiser des échanges entre patients et une personne de sa famille permettant de tirer des informations personnelles et pertinentes sur un patient suite à un dialogue.

                Vous devez suivre le format suivant : 

                Date du rendez-vous : ../../.. 

                Catégorie de l'utilisateur : famille

                Titre : 

                Famille : ...
                Patient : ...
                Famille : ...
                Patient : ...
                Famille : ... 

                En prenant en compte la présence d'un membre de la Famille et du patient atteint de la maladie d'Alzheimer.

                N'oublie pas d'être très synthètique et ne garder seulement les informations pertinentes
                
                Ensuite tu écriras un court résumé de la discussion afin de garder seulement les informations pertinentes dans l'interaction d'un membre de sa famille et du patient.
                
                Ecrire un text brut'''
                 },
                {"role": "user",
                 "content": f" ID du patient :{self.id_patient}, Date du rdv : {self.meeting_date}, Discussion : {self.discussion} "}
            ]
        if (cat=='personnel non medical'):
            message = [
                {"role": "system", "content":
                    f'''"Assistance Virtuelle pour synthétiser une interaction entre un un Patient Atteint de la Maladie d'Alzheimer et un personnel non medical
                Contexte:
                Vous êtes un assistant visrtuel capable de synthétiser des échanges entre patients et un personnel non medical de tirer des informations utiles et pertinentes pour aider le patient dans sa vie quotidienne.

                Vous devez suivre le format suivant : 

                Date du rendez-vous : ../../.. 

                Catégorie de l'utilisateur : personnel non medical

                Titre : 

                Personnel Non Medical : ...
                Patient : ...
                Personnel Non Medical : ...
                Patient : ...
                Personnel Non Medical : ... 

                En prenant en compte la présence de Personnel Non Medical et un patient atteint de la maladie d'Alzheimer.
                
                Ensuite tu écriras un court résumé de la discussion afin de garder seulement les informations pertinentes dans l'interaction d'un personnel non soignant et du patient.

                N'oublie pas d'être très synthètique et ne garder seulement les informations pertinentes

                Ecrire un text brut'''
                 },
                {"role": "user",
                 "content": f" ID du patient :{self.id_patient}, Date du rdv : {self.meeting_date}, Discussion : {self.discussion} "}
            ]
        if (cat=='personnel medical'):
            message = [
                {"role": "system", "content":
                    f'''"Assistance Virtuelle pour synthétiser une interaction entre un un Patient Atteint de la Maladie d'Alzheimer et un personnel medical
                Contexte:
                Vous êtes un assistant visrtuel capable de synthétiser des échanges entre patients et un personnel medical permettant de tirer des informations médicales et pertinentes sur un patient suite à un dialogue.

                Vous devez suivre le format suivant : 

                Date du rendez-vous : ../../.. 

                Catégorie de l'utilisateur : Personnel Medical

                Titre : 

                Personnel Medical : ...
                Patient : ...
                Personnel Medical : ...
                Patient : ...
                Personnel Medical : ... 

                En prenant en compte la présence de Personels soignants et patient atteint de la maladie d'Alzheimer.

                N'oublie pas d'être très synthètique et ne garder seulement les informations pertinentes
                
                Ensuite tu écriras un court résumé de la discussion afin de garder seulement les informations pertinentes dans l'interaction d'un personnel soignant et du patient.                

                Ecrire un text brut'''
                 },
                {"role": "user",
                 "content": f" ID du patient :{self.id_patient}, Date du rdv : {self.meeting_date}, Discussion : {self.discussion} "}
            ]
        if (cat=='admin'):
            message = [
                {"role": "system", "content":
                    f'''"Assistance Virtuelle pour synthétiser une interaction entre un un Patient Atteint de la Maladie d'Alzheimer et une personne qui peut etre un proche, un membre de sa famille, un personnel non médical ou un personnel médical. 
                Contexte:
                Vous êtes un assistant visrtuel capable de synthétiser des échanges entre patients et un personnel medical permettant de tirer des informations pertinentes (médicale, personnelle, d'habitude, de comportement) sur un patient suite à un dialogue.

                Vous devez suivre le format suivant : 

                Date du rendez-vous : ../../.. 

                Catégorie de l'utilisateur : admin

                Titre : 

                Proche : ...
                Patient : ...
                Proche : ...
                Patient : ...
                Personnel Médical : ... 

                En prenant en compte la présence de Personels soignants et/ou proche et/ou patient atteint de la maladie d'Alzheimer. Tu devras trouver le rôle de l'interlocuteur.

                N'oublie pas d'être très synthètique et ne garder seulement les informations pertinentes

                Ensuite tu écriras un court résumé de la discussion afin de garder seulement les informations pertinentes dans l'interaction du proche/personnel non soignant/personnel soignant et du patient.

                Ecrire un text brut'''
                 },
                {"role": "user",
                 "content": f" ID du patient :{self.id_patient}, Date du rdv : {self.meeting_date}, Discussion : {self.discussion} "}
            ]
        self.get_bilan(message)

    def get_bilan(self,message):
        openai.api_key = API_KEY
        try:
            reponse = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=message
            )
            bilan =  reponse.choices[0].message['content']

            self.bilan = bilan.replace("*","")
        except Exception as e:
            self.bilan = f"Une erreur s'est produite : {e}"