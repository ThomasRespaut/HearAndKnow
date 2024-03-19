from django.urls import path
from .views import BilanView, FicheView, QuestionView, HistoriqueView, Login
from . import views

urlpatterns = [
    path('bilan/', BilanView.as_view(), name='bilan'),
    path('fiche/', FicheView.as_view(), name='fiche'),
    path('question/', QuestionView.as_view(), name='question'),
    path('historique/', HistoriqueView.as_view(), name='historique'),
    path('', views.Login.as_view(), name='login'),
]