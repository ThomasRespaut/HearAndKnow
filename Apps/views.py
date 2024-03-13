from django.views.generic import ListView
from .models import ToDoItem
from datetime import date

class AllToDos(ListView):
    model = ToDoItem
    template_name = "Apps/index.html"

class TodayToDos(ListView):
    model = ToDoItem
    template_name = "Apps/today.html"

    def get_queryset(self):
        return ToDoItem.objects.filter(due_date=date.today())