from django.db import models

class Users(models.Model):
    id_user = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    category = models.CharField(max_length=255)

    def get_permissions(self):

        if self.category == 'proche':
            permission = 10

        elif self.category == 'famille':
            permission = 20

        elif self.category == 'personnel non medical':
            permission = 30

        elif self.category == 'personnel medical':
            permission = 40

        elif self.category == 'admin':
            permission = 50

        else: permission = 0

        return permission

def check_login(username, password):
    user = Users.objects.filter(username=username, password=password).first()
    if user:
        return user
    else:
        return None




