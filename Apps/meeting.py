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
    def create_bilan(self):
        #cat = request.session['category']
        #permissions = cat.get_permissions()
        message = [
            {"role": "system", "content":
            '''"Assistance Virtuelle pour synthétiser une interaction entre un un Patient Atteint de la Maladie d'Alzheimer et un personnel soignant/non soignant/proche
            Contexte:
            Vous êtes un assistant visrtuel capable de synthétiser des échanges entre patients et personnels soignant, permettant de tirer des informations utiles sur un patient suite à un dialogue.
            
            Vous devez suivre le format suivant : 
            
            Date du rendez-vous : ../../.. 
            
            Titre : 
            
            Personnel soignant : ...
            Patient : ...
            Personnel soignant : ...
            Patient : ...
            Proche : ... 
            
            En prenant en compte la présence de Personels soignants et/ou proche et/ou patient atteint de la maladie d'Alzheimer.
            
            N'oublie pas d'être très synthètique et ne garder seulement les informations pertinentes
            
            Enfin, vous écrirez un texte brut sans mise en page particulière'''
            },
            {"role": "user", "content": f" ID du patient :{self.id_patient}, Date du rdv : {self.meeting_date}, Discussion : {self.discussion} "}
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