from django.db import models
import openai
from django.db import connection, OperationalError


class Generer_reponse(models.Model):
    question = models.CharField(max_length=255)
    id_patient = models.IntegerField()
    information = models.TextField()
    message = models.TextField()
    reponse = models.TextField()

    def __str__(self):
        return f"{self.question}, {self.reponse}"

    def information_user(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT categorie_information, contenu_information FROM Information WHERE id_user = '{self.id_patient}';")
                self.information = str(cursor.fetchall())
        except OperationalError as e:
            print("Erreur lors de l'exécution de la requête SQL:", e)
            return None

    def question_user(self):
        self.message = [
            {"role": "system", "content":
                "Vous êtes un assistant virtuel intelligent conçu pour répondre à toutes sortes de questions. L'utilisateur vous fournit des informations sur un sujet spécifique, puis pose une question à laquelle il souhaite une réponse détaillée. Veuillez utiliser les données fournies pour formuler une réponse informative et cohérente. N'oubliez pas d'ajouter des détails pertinents pour rendre la réponse aussi complète que possible."},
            {"role": "user", "content": f"{self.information} {self.question}"}
        ]

        self.obtenir_reponse_chat()

    def obtenir_reponse_chat(self):
        openai.api_key = "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"
        try:
            reponse = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.message
            )

            self.reponse  = reponse.choices[0].message['content']

        except Exception as e:
            self.reponse = f"Une erreur s'est produite : {e}"
