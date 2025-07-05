from django.contrib.auth.models import AbstractUser
from django.db import models

class UserInfo(AbstractUser):
    phone = models.CharField(max_length=200,)


