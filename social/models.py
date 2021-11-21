from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Service(models.Model):
    creater = models.ForeignKey(User, on_delete=models.CASCADE)
    createddate = models.DateTimeField(default=timezone.now)
    description = models.TextField()
    servicedate = models.DateTimeField(default=timezone.now)

class Feedback(models.Model):
    feedback = models.TextField()
    createddate = models.DateTimeField(default=timezone.now)
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    creater = models.ForeignKey(User, on_delete=models.CASCADE)
