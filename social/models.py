from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError
from location_field.models.plain import PlainLocationField

def validate_date(date):
    if date < timezone.now():
        raise ValidationError("Date cannot be in the past.")

class Service(models.Model):
    creater = models.ForeignKey(User, on_delete=models.CASCADE)
    createddate = models.DateTimeField(default=timezone.now)
    name = models.TextField(default="Service Name", blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    picture = models.ImageField(upload_to='uploads/service_pictures/', default='uploads/service_pictures/default.png')
    location = PlainLocationField(default='41.0255493,28.9742571', zoom=7, blank=False, null=False)
    servicedate = models.DateTimeField(default=timezone.now)
    capacity = models.IntegerField(default=1)
    duration = models.IntegerField(default=1)
    is_given = models.BooleanField(default=False)
    is_taken = models.BooleanField(default=False)

class ServiceApplication(models.Model):
    date = models.DateTimeField(default=timezone.now)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)

class Event(models.Model):
    eventcreater = models.ForeignKey(User, on_delete=models.CASCADE)
    eventcreateddate = models.DateTimeField(default=timezone.now)
    eventname = models.TextField(default="Event Name", blank=False, null=False)
    eventdescription = models.TextField(blank=True, null=True)
    eventpicture = models.ImageField(upload_to='uploads/event_pictures/', default='uploads/event_pictures/default.png')
    eventlocation = PlainLocationField(default='41.0255493,28.9742571', zoom=7, blank=False, null=False)
    eventdate = models.DateTimeField(default=timezone.now)
    eventcapacity = models.IntegerField(default=1)
    eventduration = models.IntegerField(default=1)

class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, verbose_name='user', related_name='profile', on_delete=models.CASCADE)
    name = models.CharField(max_length=30, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    picture = models.ImageField(upload_to='uploads/profile_pictures/', default='uploads/profile_pictures/default.png')
    followers = models.ManyToManyField(User, blank=True, related_name='followers')
    credithour = models.IntegerField(default=5)
    reservehour = models.IntegerField(default=0)

class UserRatings(models.Model):
    rated = models.ForeignKey(User, verbose_name='user', related_name='rated', on_delete=models.CASCADE)
    rater = models.ForeignKey(User, verbose_name='user', related_name='rater', on_delete=models.SET_NULL, null=True)
    rating = models.IntegerField(blank=False, null=True)
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    feedback = models.TextField(blank=True, null=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
