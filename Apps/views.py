from django.views.generic import TemplateView
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from .models import get_patient_name, get_patient_list
from django.views.decorators.csrf import csrf_protect
from io import BytesIO
from .fiche import Fiche, verifier_creer_fiche
from .questions import Generer_reponse
from .meeting import Meeting
from gtts import gTTS
import speech_recognition as sr
from django.shortcuts import render
from pydub import AudioSegment

class BilanView(TemplateView):
    template_name = "Apps/bilan.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patients'] = get_patient_list()

        if 'selected_patient_id' in self.request.session:
            context['selected_patient_id'] = self.request.session['selected_patient_id']

            if 'name_patient' in self.request.session:
                context['name_patient'] = self.request.session['name_patient']

        return context
    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        selected_patient_id = request.POST.get("patientSelect")
        if selected_patient_id is not None:
            request.session['selected_patient_id'] = selected_patient_id
            context['selected_patient_id'] = selected_patient_id
            name_patient = get_patient_name(selected_patient_id)
            request.session['name_patient'] = name_patient
            context['name_patient'] = name_patient

        if "start_recording" in request.POST:
            title = request.POST['title']
            context['title'] = title
            request.session['title'] =title

            # Code pour enregistrer la voix
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("Dites quelque chose...")
                audio_data = recognizer.listen(source, timeout=30)
            try:
                # Reconnaître le texte à partir de l'audio enregistré
                discussion = recognizer.recognize_google(audio_data, language="fr-FR")
                #discussion = "imagine une discussion entre un patient et un docteur"
                context['discussion'] = discussion

                id_patient = request.session['selected_patient_id']
                meetingInstance = Meeting(title=title,discussion=discussion, id_patient=id_patient)
                meetingInstance.create_bilan()
                bilan = meetingInstance.bilan

                context['bilan'] = bilan
                request.session['bilan'] = bilan

            except sr.UnknownValueError:
                print("Impossible de reconnaître l'audio")

            except sr.RequestError as e:
                print(f"Erreur lors de la requête à l'API Google : {e}")

        if "save" in request.POST:
            title = request.POST['title']
            bilan = request.POST['bilan']
            id_patient = request.session['selected_patient_id']
            meetingInstance = Meeting(title=title, id_patient=id_patient, bilan=bilan)
            meetingInstance.save()

        if request.method == 'POST':
            if 'import_audio' in request.FILES:
                uploaded_file = request.FILES['import_audio']
                text = convert_audio_to_text(uploaded_file)
                if text:
                    # Faire quelque chose avec le texte, comme l'afficher dans le template ou le sauvegarder dans la base de données
                    print(text)
                else:
                    # Gérer les cas où la conversion échoue
                    print("La conversion audio en texte a échoué.")



        return render(request, self.template_name, context)

class FicheView(TemplateView):
    template_name = "Apps/fiche.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patients'] = get_patient_list()

        if 'selected_patient_id' in self.request.session:
            context['selected_patient_id'] = self.request.session['selected_patient_id']
            id_patient = context['selected_patient_id']

            if 'name_patient' in self.request.session:
                context['name_patient'] = self.request.session['name_patient']

            fiche = verifier_creer_fiche(id_patient)
            print(fiche)
            context['fiche'] = fiche

        return context

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        selected_patient_id = request.POST.get("patientSelect")
        if selected_patient_id is not None:
            request.session['selected_patient_id'] = selected_patient_id
            context['selected_patient_id'] = selected_patient_id

            name_patient = get_patient_name(selected_patient_id)
            print(name_patient)
            request.session['name_patient'] = name_patient
            context['name_patient'] = name_patient

            fiche = verifier_creer_fiche(selected_patient_id)
            context['fiche'] = fiche

        if 'selected_patient_id' in request.session:
            context['selected_patient_id'] = request.session['selected_patient_id']

        return render(request, self.template_name, context)

class QuestionView(TemplateView):
    template_name = "Apps/question.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patients'] = get_patient_list()

        if 'selected_patient_id' in self.request.session:
            context['selected_patient_id'] = self.request.session['selected_patient_id']
            print(context['selected_patient_id'])

            if 'name_patient' in self.request.session:
                context['name_patient'] = self.request.session['name_patient']


        return context

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        selected_patient_id = request.POST.get("patientSelect")

        if selected_patient_id is not None:
            request.session['selected_patient_id'] = selected_patient_id
            context['selected_patient_id'] = selected_patient_id
            name_patient = get_patient_name(selected_patient_id)
            print(name_patient)
            request.session['name_patient'] = name_patient
            context['name_patient'] = name_patient

        question = None

        if 'record_button' in request.POST:
            # Code pour enregistrer la voix
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("Dites quelque chose...")
                audio_data = recognizer.listen(source, timeout=30)
            try:
                # Reconnaître le texte à partir de l'audio enregistré
                question = recognizer.recognize_google(audio_data, language="fr-FR")

            except sr.UnknownValueError:
                question = "La question n'a pas été comprise, nous allons réaliser une description générale du patient"
                print("Impossible de reconnaître l'audio")

            except sr.RequestError as e:
                print(f"Erreur lors de la requête à l'API Google : {e}")

            # Si le bouton pour poser une question est soumis
        elif 'ask_question' in request.POST:
            question = request.POST.get("question_text")

        #Utiliser GPT pour répondre à la question de l'utilisateur
        if question:
            id_patient = request.session['selected_patient_id'] if 'selected_patient_id' in request.session else "141"
            generer_reponse = Generer_reponse(question=question, id_patient=id_patient)
            generer_reponse.information_user()
            generer_reponse.question_user()
            generer_reponse.save()
            reponse = generer_reponse.reponse
            request.session['reponse'] = reponse
            context['reponse'] = reponse

        #Conversion audio:
        if 'convert_audio' in request.POST:
            if request.session['reponse'] :
                reponse = request.session['reponse']
                print(reponse)
                tts = gTTS(text=reponse, lang='fr')
                audio_bytes = BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)
                context['audio'] = True
                response = HttpResponse(audio_bytes, content_type='audio/mpeg')
                response['Content-Disposition'] = 'attachment; filename="audio.mp3"'
                return response

            else :
                print("Aucune réponse fournie")

            pass

        context['selected'] = selected_patient_id
        context['question'] = question

        return render(request, self.template_name, context)

class HistoriqueView(TemplateView):
    template_name = "Apps/historique.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patients'] = get_patient_list()

        if 'selected_patient_id' in self.request.session:
            context['selected_patient_id'] = self.request.session['selected_patient_id']
            id_patient = context['selected_patient_id']
            if 'name_patient' in self.request.session:
                context['name_patient'] = self.request.session['name_patient']

            try:
                meetings = Meeting.objects.filter(id_patient=id_patient)
                context['meetings'] = meetings
            except Meeting.DoesNotExist:
                # Gérer le cas où aucun objet Meeting correspondant n'est trouvé
                context['meetings'] = None

        return context

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        selected_patient_id = request.POST.get("patientSelect")
        if selected_patient_id is not None:
            request.session['selected_patient_id'] = selected_patient_id
            context['selected_patient_id'] = selected_patient_id

            name_patient = get_patient_name(selected_patient_id)
            print(name_patient)
            request.session['name_patient'] = name_patient
            context['name_patient'] = name_patient

            meetings = Meeting.objects.filter(id_patient=selected_patient_id)
            context['meetings'] = meetings

        if 'selected_patient_id' in request.session:
            context['selected_patient_id'] = request.session['selected_patient_id']
        return render(request, self.template_name, context)
def speech_to_text(request):
    if request.method == 'POST':
        # Utiliser SpeechRecognition pour reconnaître l'audio en temps réel
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Dites quelque chose...")
            # Définir un timeout plus long (par exemple, 60 secondes)
            audio_data = recognizer.listen(source, timeout=60)

        try:
            # Reconnaître le texte à partir de l'audio enregistré
            text = recognizer.recognize_google(audio_data, language="fr-FR")
            return render(request, 'Apps/result.html', {'text': text})
        except sr.UnknownValueError:
            text = "Impossible de reconnaître l'audio"
            return render(request, 'Apps/result.html', {'text': text})
        except sr.RequestError as e:
            text = f"Erreur lors de la requête à l'API Google : {e}"
            return render(request, 'Apps/result.html', {'text': text})
    else:
        return render(request, 'Apps/speech_to_text.html')
def text_to_speech(text, language='fr'):
    tts = gTTS(text=text, lang=language)
    return tts

class Login(TemplateView):
    template_name = "Apps/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        # Rediriger vers Apps/base.html
        return render(request, 'Apps/bilan.html', context)


import speech_recognition as sr
import tempfile

def convert_audio_to_text(uploaded_file):
    print(type(uploaded_file))  # Affiche le type de l'objet uploaded_file
    try:
        # Créer un recognizer
        recognizer = sr.Recognizer()

        # Sauvegarder les données audio dans un fichier temporaire
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio_file:
            temp_audio_file.write(uploaded_file.read())

        # Transcrire le contenu audio en texte
        with sr.AudioFile(temp_audio_file.name) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="fr-FR")

        return text

    except Exception as e:
        print(f"Erreur lors de la conversion audio en texte : {e}")
        return None
