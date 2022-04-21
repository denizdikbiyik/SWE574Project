from django.db import models


# Create your models here.
class WikiDescription(models.Model):
    keyword = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
