from django.db import models
from django.db import connection, OperationalError
import openai

class Images(models.Model):
    name=models.CharField(max_length=150)
    image=models.ImageField(upload_to='images',blank=True)
    def __str__(self):
        return self.name

def get_patient_list():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_user, CONCAT(prenom_user, ' ', nom_user) as name FROM patient;")
            patients = cursor.fetchall()
            return patients
    except OperationalError as e:
        print("Erreur lors de l'exécution de la requête SQL:", e)
        return None

def get_patient_name(id_patient):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT CONCAT(prenom_user,' ', nom_user)  as name FROM patient WHERE id_user = %s;", [id_patient])
            result = cursor.fetchone()  # Modification ici pour récupérer seulement le premier résultat
        return result[0]
    except OperationalError as e:
        print("Erreur lors de l'exécution de la requête SQL:", e)
        return None