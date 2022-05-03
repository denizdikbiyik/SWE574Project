from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from location_field.models.plain import PlainLocationField
from django.urls import reverse


def validate_date(date):
    if date < timezone.now():
        raise ValidationError("Date cannot be in the past.")


class Tag(models.Model):
    tag = models.TextField(default='', blank=False, null=False)
    requester = models.ForeignKey(User, verbose_name='user', related_name='requester', blank=True, null=True,
                                  on_delete=models.SET_NULL)
    toPerson = models.ForeignKey(User, verbose_name='user', related_name='toPerson', blank=True, null=True,
                                 on_delete=models.SET_NULL)

    def __str__(self):
        return self.tag


class Service(models.Model):
    creater = models.ForeignKey(User, on_delete=models.CASCADE)
    createddate = models.DateTimeField(default=timezone.now)
    name = models.TextField(default="Service Name", blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    wiki_description = models.TextField(blank=True, null=True)
    picture = models.ImageField(upload_to='uploads/service_pictures/', default='uploads/service_pictures/default.png')
    location = PlainLocationField(default='41.0255493,28.9742571', zoom=7, blank=False, null=False)
    address = models.TextField(blank=True, null=True)
    servicedate = models.DateTimeField(default=timezone.now)
    capacity = models.IntegerField(default=1)
    duration = models.IntegerField(default=1)
    is_given = models.BooleanField(default=False)
    is_taken = models.BooleanField(default=False)
    category = models.ForeignKey(Tag, verbose_name='category', related_name='category', blank=True, null=True,
                                 on_delete=models.SET_NULL)
    isDeleted = models.BooleanField(default=False)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dashboard-service-detail', args=[str(self.pk)])


class ServiceApplication(models.Model):
    date = models.DateTimeField(default=timezone.now)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name="rel_services")
    approved = models.BooleanField(default=False)
    isDeleted = models.BooleanField(default=False)
    deletionInfo = models.TextField(blank=True, null=True)
    isActive = models.BooleanField(default=True)


class Event(models.Model):
    eventcreater = models.ForeignKey(User, on_delete=models.CASCADE)
    eventcreateddate = models.DateTimeField(default=timezone.now)
    eventname = models.TextField(default="Event Name", blank=False, null=False)
    eventdescription = models.TextField(blank=True, null=True)
    event_wiki_description = models.TextField(blank=True, null=True)
    eventpicture = models.ImageField(upload_to='uploads/event_pictures/', default='uploads/event_pictures/default.png')
    eventlocation = PlainLocationField(default='41.0255493,28.9742571', zoom=7, blank=False, null=False)
    event_address = models.TextField(blank=True, null=True)
    eventdate = models.DateTimeField(default=timezone.now)
    eventcapacity = models.IntegerField(default=1)
    eventduration = models.IntegerField(default=1)
    isDeleted = models.BooleanField(default=False)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return self.eventname

    def get_absolute_url(self):
        return reverse('dashboard-event-detail', args=[str(self.pk)])


class EventApplication(models.Model):
    date = models.DateTimeField(default=timezone.now)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name="rel_events")
    approved = models.BooleanField(default=False)
    isDeleted = models.BooleanField(default=False)
    deletionInfo = models.TextField(blank=True, null=True)
    isActive = models.BooleanField(default=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, verbose_name='user', related_name='profile',
                                on_delete=models.CASCADE)
    name = models.CharField(max_length=30, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    birth_date = models.DateTimeField(null=True, blank=True)
    location = PlainLocationField(default='41.0255493,28.9742571', zoom=7, blank=False, null=False)
    picture = models.ImageField(upload_to='uploads/profile_pictures/', default='uploads/profile_pictures/default.png')
    followers = models.ManyToManyField(User, blank=True, related_name='followers')
    credithour = models.IntegerField(default=5)
    reservehour = models.IntegerField(default=0)
    unreadcount = models.IntegerField(default=0)
    isAdmin = models.BooleanField(default=False)
    isSuperAdmin = models.BooleanField(default=False)
    isActive = models.BooleanField(default=True)


class UserRatings(models.Model):
    rated = models.ForeignKey(User, verbose_name='user', related_name='rated', on_delete=models.CASCADE)
    rater = models.ForeignKey(User, verbose_name='user', related_name='rater', on_delete=models.SET_NULL, null=True)
    rating = models.IntegerField(blank=False, null=True)
    service = models.ForeignKey('Service', on_delete=models.SET_NULL, null=True)
    feedback = models.TextField(blank=True, null=True)


class UserComplaints(models.Model):
    complainted = models.ForeignKey(User, verbose_name='user', related_name='complainted', on_delete=models.CASCADE)
    complainter = models.ForeignKey(User, verbose_name='user', related_name='complainter', on_delete=models.SET_NULL,
                                    null=True)
    feedback = models.TextField(blank=True, null=True)
    isDeleted = models.BooleanField(default=False)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class NotifyUser(models.Model):
    notify = models.ForeignKey(User, verbose_name='user', related_name='notify', on_delete=models.CASCADE)
    notification = models.TextField(blank=True, null=True)
    hasRead = models.BooleanField(default=False)
    offerType = models.TextField(blank=True, null=True)
    offerPk = models.IntegerField(default=0)


class Log(models.Model):
    date = models.DateTimeField(default=timezone.now)
    operation = models.TextField(blank=True, null=True)
    itemType = models.TextField(blank=True, null=True)
    itemId = models.IntegerField(default=0)
    userId = models.ForeignKey(User, verbose_name='user', related_name='userId', on_delete=models.CASCADE)
    affectedItemType = models.TextField(blank=True, null=True)
    affectedItemId = models.IntegerField(default=0)


class Communication(models.Model):
    date = models.DateTimeField(default=timezone.now)
    itemType = models.TextField(blank=True, null=True)
    itemId = models.IntegerField(default=0)
    communicated = models.ForeignKey(User, verbose_name='user', related_name='communicated', on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)


class Like(models.Model):
    date = models.DateTimeField(default=timezone.now)
    itemType = models.TextField(blank=True, null=True)
    itemId = models.IntegerField(default=0)
    liked = models.ForeignKey(User, verbose_name='user', related_name='liked', on_delete=models.CASCADE)


class Featured(models.Model):
    date = models.DateTimeField(default=timezone.now)
    operation = models.TextField(blank=True, null=True)
    itemType = models.TextField(blank=True, null=True)
    itemId = models.IntegerField(default=0)

class Interest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField(blank=False, null=False)
    wiki_description = models.TextField(blank=False, null=False)