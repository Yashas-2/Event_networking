from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import cancel_registration
from .views import EventDetailView
from .views import profile_view, delete_certificate




urlpatterns = [
    # Authentication
    path('', views.user_type_selection, name='user_type_selection'),
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Main pages
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('generate-cv/', views.generate_cv, name='generate_cv'),
    
    # Events
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/category/<int:category_id>/', views.EventListView.as_view(), name='events_by_category'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('register-event/<int:event_id>/', views.register_for_event, name='register_for_event'),
    path('events/<int:event_id>/register/', views.register_for_event, name='register_for_event'),
    path('cancel-registration/<int:registration_id>/', cancel_registration, name='cancel_registration'),
    path('events/<int:event_id>/cancel/', cancel_registration, name='cancel_registration'),
    path('events/<int:event_id>/cancel/', cancel_registration, name='cancel_registration'),
    path('event/<int:pk>/', EventDetailView.as_view(), name='event_detail'),


    
    
    # Feedback and Suggestions
    path('event/<int:event_id>/feedback/', views.add_feedback, name='add_feedback'),
    path('event/<int:event_id>/suggestion/', views.add_suggestion, name='add_suggestion'),
    
    # Certificates
    path('upload-certificate/', views.upload_certificate, name='upload_certificate'),
    path('profile/', profile_view, name='profile'),
    path('delete-certificate/<int:cert_id>/', delete_certificate, name='delete_certificate'),
    
    # Messaging
    path('messages/', views.messaging_inbox, name='messaging_inbox'),
    path('send-message/', views.send_message, name='send_message'),
    path('conversation/<int:user_id>/', views.conversation_view, name='conversation'),
    
    # Organizer features
    path('organizer-dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('event/<int:event_id>/registrations/', views.event_registrations, name='event_registrations'),
    path('event/new/', views.event_create, name='event_create'),
    path('event/<int:pk>/edit/', views.event_update, name='event_update'),
    path('event/<int:pk>/delete/', views.event_delete, name='event_delete'),

]