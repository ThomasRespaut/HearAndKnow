from django.db import models
import datetime
import openai

class Meeting(models.Model):
    title = models.CharField(max_length=255)
    id_patient = models.IntegerField()
    discussion = models.TextField()
    bilan = models.TextField()
    def create_bilan(self):
        message = [
            {"role": "system", "content":
            '''"Assistance Virtuelle pour le Bilan d'une Consultation Médicale pour un Patient Atteint de la Maladie d'Alzheimer"
            Contexte:
            Vous êtes l'assistant virtuel d'une clinique médicale spécialisée dans le traitement des patients atteints de la maladie d'Alzheimer. Votre rôle est d'aider le médecin dans la réalisation d'un bilan après la consultation avec un patient atteint de cette maladie. Le médecin a besoin d'un résumé clair et concis des points importants discutés lors de la consultation, ainsi que des recommandations pour le suivi du patient.
            
            Instructions pour l'Assistant Virtuel:
            
            Résumez les informations essentielles discutées lors de la consultation entre le médecin et le patient atteint de la maladie d'Alzheimer.
            Identifiez les symptômes clés signalés par le patient et évoqués par le médecin.
            Répertoriez les médicaments actuels du patient et toute modification recommandée par le médecin.
            Fournissez des recommandations pour le suivi du patient, y compris les prochaines étapes à suivre et les mesures à prendre pour améliorer la qualité de vie du patient.
            Assurez-vous que le bilan est rédigé de manière claire et compréhensible, en évitant les termes médicaux trop complexes qui pourraient ne pas être accessibles au patient ou à ses proches.
            Points Importants à Inclure:
            
            État de la progression de la maladie d'Alzheimer.
            Symptômes actuels du patient et tout changement significatif.
            Médicaments prescrits et ajustements recommandés.
            Recommandations pour le suivi, y compris les soins de soutien et les thérapies complémentaires.
            Coopération et implication de la famille ou des aidants dans le plan de traitement.
            N'oubliez pas d'être empathique et respectueux dans la rédaction du bilan, en tenant compte de la sensibilité de la situation du patient et de ses proches.
            
            Enfin, vous écrirez un texte brut sans mise en page particulière'''
            },
            {"role": "user", "content": f" ID du patient :{self.id_patient}, Date du rdv : {self.meeting_date}, Discussion : {self.discussion} "}
        ]

        self.get_bilan(message)

    def get_bilan(self,message):
        openai.api_key = "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"
        try:
            reponse = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=message
            )
            bilan =  reponse.choices[0].message['content']

            self.bilan = bilan.replace("*","")
        except Exception as e:
            self.bilan = f"Une erreur s'est produite : {e}"