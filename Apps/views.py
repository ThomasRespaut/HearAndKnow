from django.views.generic import TemplateView
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect

from io import BytesIO
from gtts import gTTS
import speech_recognition as sr
import openai

from .models import get_patient_name, get_patient_list
from .fiche import Fiche, verifier_creer_fiche
from .questions import Generer_reponse
from .meeting import Meeting
from .secrets import API_KEY
from .login import Users, check_login

class BilanView(TemplateView):
    template_name = "Apps/bilan.html"

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        if 'username' not in request.session:
            # Redirigez vers la page de connexion si l'utilisateur n'est pas connecté
            return redirect('login')  # Assurez-vous que 'login' est le nom de votre vue de connexion
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patients'] = get_patient_list()

        if 'selected_patient_id' in self.request.session:
            context['selected_patient_id'] = self.request.session['selected_patient_id']

            if 'name_patient' in self.request.session:
                context['name_patient'] = self.request.session['name_patient']

        if 'username' in self.request.session:
            context['username'] = self.request.session['username']

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        print('toto')
        print(request.session)
        if(request.session['category']) :
            cat = request.session['category']
            permission = request.session['permission']
        else :
            cat =''
            permission = 0

        if "log_out" in request.POST:
            # Supprimer toutes les variables de session
            request.session.flush()
            return redirect('login')

        if 'username' in self.request.session:
            context['username'] = self.request.session['username']

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
            request.session['title'] = title

            # Code pour enregistrer la voix
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("Dites quelque chose...")
                audio_data = recognizer.listen(source, timeout=30)
            try:
                # Reconnaître le texte à partir de l'audio enregistré
                discussion = recognizer.recognize_google(audio_data, language="fr-FR")
                context['discussion'] = discussion
                request.session['discussion'] = discussion
                id_patient = request.session['selected_patient_id']
                meetingInstance = Meeting(title=title, discussion=discussion, id_patient=id_patient)
                meetingInstance.create_bilan(cat,permission)
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

        if 'import_audio' in request.FILES:
            uploaded_file = request.FILES['import_audio']
            text = convert_audio_to_text(uploaded_file)
            if text != "":
                request.session['discussion'] = text
                id_patient = request.session['selected_patient_id']
                title = request.POST['title']
                context["title"] = title

                meetingInstance = Meeting(title=title, discussion=text, id_patient=id_patient)
                meetingInstance.create_bilan(cat,permission)
                bilan = meetingInstance.bilan
                context['bilan'] = bilan
                request.session['bilan'] = bilan
                print(text)
                print('-'*50)
                print(bilan)
            else:
                # Gérer les cas où la conversion échoue
                print("La conversion audio en texte a échoué.")

        if 'reload' in request.POST:
            discussion = request.session['discussion']
            id_patient = request.session['selected_patient_id']
            title = request.POST['title']
            context['title'] = title
            meetingInstance = Meeting(title=title, discussion=discussion, id_patient=id_patient)
            meetingInstance.create_bilan(cat,permission)
            bilan = meetingInstance.bilan
            context['bilan'] = bilan
            request.session['bilan'] = bilan

        else:
            # Gérer les cas où la conversion échoue
            print("La conversion audio en texte a échoué.")

        return render(request, self.template_name, context)

class FicheView(TemplateView):
    template_name = "Apps/fiche.html"
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        if 'username' not in request.session:
            # Redirigez vers la page de connexion si l'utilisateur n'est pas connecté
            return redirect('login')  # Assurez-vous que 'login' est le nom de votre vue de connexion

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patients'] = get_patient_list()

        if 'username' in self.request.session:
            context['username'] = self.request.session['username']

        if 'selected_patient_id' in self.request.session:
            context['selected_patient_id'] = self.request.session['selected_patient_id']
            id_patient = context['selected_patient_id']

            if 'name_patient' in self.request.session:
                context['name_patient'] = self.request.session['name_patient']

            fiche = verifier_creer_fiche(id_patient)
            print(fiche)
            context['fiche'] = fiche

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if "log_out" in request.POST:
            # Supprimer toutes les variables de session
            request.session.flush()
            return redirect('login')

        if 'username' in self.request.session:
            context['username'] = self.request.session['username']

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
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        if 'username' not in request.session:
            # Redirigez vers la page de connexion si l'utilisateur n'est pas connecté
            return redirect('login')  # Assurez-vous que 'login' est le nom de votre vue de connexion

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patients'] = get_patient_list()

        if 'selected_patient_id' in self.request.session:
            context['selected_patient_id'] = self.request.session['selected_patient_id']
            print(context['selected_patient_id'])

            if 'name_patient' in self.request.session:
                context['name_patient'] = self.request.session['name_patient']

        if 'username' in self.request.session:
            context['username'] = self.request.session['username']

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if "log_out" in request.POST:
            # Supprimer toutes les variables de session
            request.session.flush()
            return redirect('login')

        if 'username' in self.request.session:
            context['username'] = self.request.session['username']

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
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        if 'username' not in request.session:
            # Redirigez vers la page de connexion si l'utilisateur n'est pas connecté
            return redirect('login')  # Assurez-vous que 'login' est le nom de votre vue de connexion

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patients'] = get_patient_list()

        if 'username' in self.request.session:
            context['username'] = self.request.session['username']

        if 'selected_patient_id' in self.request.session:
            context['selected_patient_id'] = self.request.session['selected_patient_id']
            id_patient = context['selected_patient_id']
            if 'name_patient' in self.request.session:
                context['name_patient'] = self.request.session['name_patient']

            try:
                meetings = Meeting.objects.filter(id_patient=id_patient).order_by('-id')
                context['meetings'] = meetings
            except Meeting.DoesNotExist:
                # Gérer le cas où aucun objet Meeting correspondant n'est trouvé
                context['meetings'] = None

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if "log_out" in request.POST:
            # Supprimer toutes les variables de session
            request.session.flush()
            return redirect('login')

        if 'username' in self.request.session:
            context['username'] = self.request.session['username']

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

class AdminView(TemplateView):

    template_name = "Apps/espace_Admin.html"
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        if 'username' not in request.session:
            # Redirigez vers la page de connexion si l'utilisateur n'est pas connecté
            return redirect('login')  # Assurez-vous que 'login' est le nom de votre vue de connexion

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if "log_out" in request.POST:
            # Supprimer toutes les variables de session
            request.session.flush()
            return redirect('login')

        if 'username' in self.request.session:
            context['username'] = self.request.session['username']

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

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Capturez les valeurs username et password à partir de la requête POST
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Vérifiez si les champs sont vides
        if not username or not password:
            return render(request, self.template_name, {"message": "Veuillez remplir tous les champs."})

        # Vérifiez les informations d'identification
        user = Users.objects.filter(username=username, password=password).first()
        if user:
            # Stockez les informations utilisateur dans la session
            request.session["id_user"] = user.id_user
            request.session["username"] = user.username
            request.session["category"] = user.category
            request.session["permission"] = user.get_permissions()

            # Redirigez vers une page de réussite de connexion
            return render(request, 'Apps/bilan.html',
                          {"username": user.username, "category": user.category, "id_user": user.id_user})
        else:
            # Affichez un message d'erreur si les informations d'identification sont incorrectes
            return render(request, self.template_name, {"message": "Identifiant ou mot de passe incorrect."})


def convert_audio_to_text(uploaded_file):
    try:
        # Créer un recognizer
        openai.api_key = API_KEY
        transcription = openai.Audio.transcribe("whisper-1", uploaded_file)

        texte_corrigé = transcription["text"].encode().decode('utf-8')


        '''
        recognizer = sr.Recognizer()
        # Sauvegarder les données audio dans un fichier temporaire
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio_file:
            temp_audio_file.write(uploaded_file.read())

        # Transcrire le contenu audio en texte
        with sr.AudioFile(temp_audio_file.name) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="fr-FR")
        '''
        return texte_corrigé

    except Exception as e:
        print(f"Erreur lors de la conversion audio en texte : {e}")
        return None

