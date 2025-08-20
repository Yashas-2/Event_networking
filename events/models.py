from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import datetime
from django.contrib.auth import get_user_model

class User(AbstractUser):
    USER_TYPES = (
        ('organizer', 'Organizer'),
        ('participant', 'Participant'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    areas_of_interest = models.ManyToManyField('Category', blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    max_participants = models.IntegerField()
    registration_link = models.URLField(help_text="Google Form registration link")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_time = models.DateTimeField()
    duration = models.IntegerField(default=60)
    image = models.ImageField(upload_to='event_posters/', blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'pk': self.pk})

    @property
    def status(self):
        now = timezone.now()
        # Ensure start_time is timezone-aware and in UTC for consistent comparison
        start_time_utc = self.start_time.astimezone(datetime.timezone.utc) if self.start_time.tzinfo else timezone.make_aware(self.start_time, datetime.timezone.utc)
        end_time_utc = start_time_utc + timedelta(minutes=self.duration)

        if now < start_time_utc:
            return 'upcoming'
        elif start_time_utc <= now <= end_time_utc:
            return 'ongoing'
        else:
            return 'completed'

    @property
    def registered_count(self):
        return self.registrations_real.count()

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('event', 'participant')
    
    def __str__(self):
        return f"{self.participant.username} - {self.event.title}"

class EventFeedback(models.Model):
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='feedback')
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('event', 'participant')
    
    def __str__(self):
        return f"{self.event.title} - {self.rating} stars"

class Certificate(models.Model):
    CERTIFICATE_TYPES = (
        ('technical', 'Technical'),
        ('non_technical', 'Non-Technical'),
    )
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name='certificates_of_event')
    name = models.CharField(max_length=255)
    certificate_file = models.FileField(upload_to='certificates/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    certificate_type = models.CharField(max_length=20, choices=CERTIFICATE_TYPES, default='technical')

    def __str__(self):
        return f"{self.participant.username} - {self.name}"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}"

class EventSuggestion(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='suggestions')
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    suggestion = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Suggestion for {self.event.title}"

User = get_user_model()

class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations_real')
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)

    class Meta:
        unique_together = ('event', 'user')