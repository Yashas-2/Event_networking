from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Event, EventRegistration, EventFeedback, Certificate, Message, EventSuggestion

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone', 'bio', 'profile_picture')}),
    )
    list_display = ['username', 'email', 'user_type', 'is_staff']
    list_filter = ['user_type', 'is_staff', 'is_superuser']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'category', 'date']
    list_filter = ['category', 'date']
    search_fields = ['title', 'description']

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['participant', 'event', 'registered_at', 'attended']
    list_filter = ['attended', 'registered_at']

@admin.register(EventFeedback)
class EventFeedbackAdmin(admin.ModelAdmin):
    list_display = ['event', 'participant', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['participant', 'name', 'uploaded_at']
    list_filter = ['uploaded_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'timestamp', 'is_read']
    list_filter = ['is_read', 'timestamp']

@admin.register(EventSuggestion)
class EventSuggestionAdmin(admin.ModelAdmin):
    list_display = ['event', 'participant', 'created_at']
    list_filter = ['created_at']

admin.site.register(User, CustomUserAdmin)