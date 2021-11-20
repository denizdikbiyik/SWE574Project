from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Service(models.Model):
    creater = models.ForeignKey(User, on_delete=models.CASCADE)
    createddate = models.DateTimeField(default=timezone.now)
    description = models.TextField()
    servicedate = models.DateTimeField()