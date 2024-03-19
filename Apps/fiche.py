from django.db import models
from django.db import connection, OperationalError
import openai

class Fiche(models.Model):
    id_patient = models.IntegerField()
    habitudes_alimentaires = models.TextField(blank=True)
    habitudes_de_sommeil = models.TextField(blank=True)
    autres = models.TextField(blank=True)
    situation_medicale = models.TextField(blank=True)

    def information_user(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT categorie_information, contenu_information FROM Information WHERE id_user = '{self.id_patient}';")
                return str(cursor.fetchall())
        except OperationalError as e:
            print("Erreur lors de l'exécution de la requête SQL:", e)
            return None


    def CreerFiche(self):

        informations = self.information_user()

        message = [
            {"role": "system", "content":
                '''Un utilisateur demande à une IA de générer une très très courte fiche en points sur les habitudes alimentaires d'un patient atteint de la maladie d'Alzheimer. L'IA doit identifier les informations pertinentes transmises par l'utilisateur pour inclure dans la fiche. Il est important que la fiche soit un résumé donc très courte

                Exemple d'informations utilisateur :
                
                Âge du patient : 72 ans
                Stade de la maladie d'Alzheimer : Modéré
                Allergies alimentaires : Aucune
                Préférences alimentaires : Traditionnelles, a une aversion pour les aliments épicés
                Difficultés alimentaires : Oubli fréquent des repas, confusion pendant les repas, difficulté à utiliser les couverts
                Sortie attendue :
                
                Âge : 72 ans
                Stade de la maladie : Modéré
                Allergies alimentaires : Aucune
                Préférences : Aliments traditionnels, éviter les épices
                Difficultés : Oubli des repas, confusion pendant les repas, difficulté avec les couverts'''
             },
            {"role": "user",
             "content": f" ID du patient :{self.id_patient}, Information de l'utilisateur : {informations}"}
        ]

        self.habitudes_alimentaires = self.get_resume(message)

        message = [
            {"role": "system", "content":
                '''Un utilisateur demande à une IA de générer une courte très très fiche en points sur les habitudes de sommeil d'un patient atteint de la maladie d'Alzheimer. L'IA doit identifier les informations pertinentes transmises par l'utilisateur pour inclure dans la fiche.Il est important que la fiche soit un résumé donc très courte.

                Exemple d'informations utilisateur :

                Âge du patient : 72 ans
                Stade de la maladie d'Alzheimer : Modéré
                Routine de sommeil : Se couche tôt, se réveille plusieurs fois dans la nuit
                Facteurs perturbateurs du sommeil : Confusion nocturne, anxiété
                Autres informations pertinentes : Évite la caféine après 16h, utilise des techniques de relaxation avant le coucher
                Sortie attendue :

                Âge : 72 ans
                Stade de la maladie : Modéré
                Routine de sommeil : Se couche tôt, réveils fréquents dans la nuit
                Facteurs perturbateurs : Confusion nocturne, anxiété
                Précautions : Éviter la caféine après 16h, utiliser des techniques de relaxation avant le coucher'''
             },
            {"role": "user",
             "content": f" ID du patient : {self.id_patient}, Informations utilisateur : {informations}"}
        ]

        self.habitudes_de_sommeil = self.get_resume(message)

        message = [
            {"role": "system", "content":
                '''Un utilisateur demande à une IA de générer une très très courte fiche en points sur la situation administrative d'un patient atteint de la maladie d'Alzheimer. L'IA doit identifier les informations pertinentes transmises par l'utilisateur pour inclure dans la fiche. Il est important que la fiche soit un résumé donc très courte, à peine quelques lignes.

                Exemple d'informations utilisateur :

                Âge du patient : 72 ans
                Stade de la maladie d'Alzheimer : Modéré
                Statut de l'assurance médicale : Couvert par Medicare
                Personne de contact en cas d'urgence : Fils, numéro de téléphone : +123456789
                Autres informations administratives : Résidence en maison de retraite, dossier médical partagé avec le médecin traitant
                Sortie attendue :

                Âge : 72 ans
                Stade de la maladie : Modéré
                Assurance médicale : Couvert par Medicare
                Personne de contact : Fils, numéro de téléphone : +123456789
                Autres informations : Résidence en maison de retraite, dossier médical partagé avec le médecin traitant'''
             },
            {"role": "user",
             "content": f" ID du patient : {self.id_patient}, Informations utilisateur : {informations}"}
        ]

        self.autres = self.get_resume(message)

        message = [
            {"role": "system", "content":
                '''Un utilisateur demande à une IA de générer une très très courte fiche en points sur la situation médicale d'un patient atteint de la maladie d'Alzheimer. L'IA doit identifier les informations pertinentes transmises par l'utilisateur pour inclure dans la fiche. Il est important que la fiche soit un résumé donc très courte, , à peine quelques lignes.

                Exemple d'informations utilisateur :

                Âge du patient : 72 ans
                Stade de la maladie d'Alzheimer : Modéré
                Médicaments actuels : Donepezil, Memantine
                Conditions médicales préexistantes : Hypertension artérielle, Diabète de type 2
                Historique des chirurgies : Aucune
                Sortie attendue :

                Âge : 72 ans
                Stade de la maladie : Modéré
                Médicaments : Donepezil, Memantine
                Conditions médicales : Hypertension artérielle, Diabète de type 2
                Chirurgies antérieures : Aucune'''
             },
            {"role": "user",
             "content": f" ID du patient : {self.id_patient}, Informations utilisateur : {informations}"}
        ]

        self.situation_medicale = self.get_resume(message)

    def get_resume(self, message):
        openai.api_key = "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"
        try:
            reponse =  openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=message
            )
            return reponse.choices[0].message['content']
        except Exception as e:
            return  f"Une erreur s'est produite : {e}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

def verifier_creer_fiche(id_patient):
    fiche = Fiche.objects.filter(id_patient=id_patient).first()

    print(fiche)

    if fiche:
        return fiche
    else:
        nouvelle_fiche = Fiche.objects.create(id_patient=id_patient)
        nouvelle_fiche.CreerFiche()
        nouvelle_fiche.save()
        return nouvelle_fiche