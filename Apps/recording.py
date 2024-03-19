# views.py
from django.shortcuts import render
import speech_recognition as sr

def speech_to_text(request):
    if request.method == 'POST':
        # Récupérer le fichier audio depuis la requête POST
        audio_file = request.FILES.get('audio_file')

        if audio_file:
            # Utiliser SpeechRecognition pour reconnaître le texte
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                return render(request, 'result.html', {'text': text})
            except sr.UnknownValueError:
                text = "Impossible de reconnaître l'audio"
                return render(request, 'result.html', {'text': text})
            except sr.RequestError as e:
                text = f"Erreur lors de la requête à l'API Google : {e}"
                return render(request, 'result.html', {'text': text})
        else:
            error_message = "Aucun fichier audio n'a été fourni."
            return render(request, 'result.html', {'text': error_message})
    else:
        return render(request, 'speech_to_text.html')
