from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.views import LoginView
import json
from django.contrib import messages
from django.core.mail import send_mail
from .models import Event, EventRegistration
from .forms import RegistrationForm 
from django.urls import reverse

from .models import User, Event, Category, EventRegistration, EventFeedback, Message, EventSuggestion, Certificate,  Registration
from .forms import UserRegistrationForm, UserProfileForm, EventFeedbackForm, MessageForm, EventSuggestionForm, CertificateUploadForm, EventForm
# Install: pip install openai
# Add this function to views.py for real AI integration:

import openai
from django.conf import settings

def generate_ai_summary_real(event, feedback):
    openai.api_key = settings.OPENAI_API_KEY
    
    feedback_text = " ".join([f.comment for f in feedback])
    
    prompt = f"""
    Generate a brief summary of the event "{event.title}" based on participant feedback:
    
    Event Description: {event.description}
    Category: {event.category.name}
    Participant Feedback: {feedback_text}
    
    Provide a 2-3 sentence summary highlighting key strengths and areas mentioned by participants.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI summary temporarily unavailable. Event focuses on {event.category.name}."

class CustomLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        if user.user_type == 'organizer':
            return reverse('organizer_dashboard')
        return reverse('home')

    def form_valid(self, form):
        user = form.get_user()
        password = self.request.POST.get('password')
        user_type_param = self.request.GET.get('user_type')

        if user_type_param and user.user_type != user_type_param:
            messages.error(self.request, "You are registered as a different user type.")
            return self.form_invalid(form)

        if user.user_type == 'organizer' and not password.startswith('admin'):
            messages.error(self.request, "Invalid Password.")
            return self.form_invalid(form)

        login(self.request, user)
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)
    
from django.contrib import messages

def clear_old_messages(request):
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # This clears them




def user_type_selection(request):
    """View for selecting user type (organizer or participant)"""
    return render(request, 'events/user_type_selection.html')

def register(request):
    user_type = request.GET.get('type', 'participant')

    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['user_type'] = user_type

        form = UserRegistrationForm(post_data)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = form.cleaned_data['user_type']
            user.save()
            messages.success(request, f'Account created for {user.username}!')
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm(initial={'user_type': user_type})

    return render(request, 'registration/register.html', {
        'form': form,
        'user_type': user_type
    })


@login_required
def home(request):
    """Home page showing featured events"""
    all_events = Event.objects.order_by('date')
    events = [event for event in all_events if event.status == 'upcoming'][:6]
    categories = Category.objects.all()
    return render(request, 'events/home.html', {'events': events, 'categories': categories})

class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10
    
    def get_queryset(self):
        all_events = Event.objects.order_by('date')
        queryset = [event for event in all_events if event.status == 'upcoming']
        category_id = self.kwargs.get('category_id')
        if category_id:
            queryset = [event for event in queryset if event.category.id == category_id]

        # Add search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = [event for event in queryset if query.lower() in event.title.lower() or query.lower() in event.description.lower()]
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('category_id')
        if category_id:
            context['category'] = get_object_or_404(Category, id=category_id)
        return context

class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()

        # ✅ Pass start_time for countdown
        context['start_time'] = event.start_time

        # ✅ Check if user is registered
        is_registered = Registration.objects.filter(
            event=event, user=self.request.user
        ).exists()

        # ✅ Get feedback and suggestions
        feedback = EventFeedback.objects.filter(event=event).order_by('-created_at')
        suggestions = EventSuggestion.objects.filter(event=event).order_by('-created_at')

        # ✅ AI Summary placeholder
        ai_summary = self.generate_ai_summary(event, feedback)

        # ✅ Update context
        context.update({
            'is_registered': is_registered,
            'feedback': feedback,
            'suggestions': suggestions,
            'ai_summary': ai_summary,
            'feedback_form': EventFeedbackForm(),
            'suggestion_form': EventSuggestionForm(),
        })

        return context
    
    def generate_ai_summary(self, event, feedback):
        """Placeholder for AI summary generation"""
        return f"This is an AI-generated summary for {event.title}. Based on participant feedback, this event focuses on {event.category.name} and has received positive reviews for its comprehensive content and engaging format."

@login_required
def register_for_event(request, event_id):
    """Register user for an event with name and email input"""
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            registration.user = request.user  # ✅ This line links the registration to the logged-in user
            registration.save()

            # Send confirmation email
            send_mail(
                subject=f'Registration Confirmation for {event.title}',
                message=f"""
Hi {registration.name},

Thank you for registering for {event.title}!

📅 Date: {event.date.strftime('%A, %d %B %Y at %I:%M %p')}
📍 Location: {event.location}

We look forward to seeing you!

Best regards,
Event Team
""",
                from_email='yashashassan271125@gmail.com',
                recipient_list=[registration.email],
                fail_silently=False,
            )

            messages.success(request, f'Registration successful! Confirmation sent to {registration.email}')
            return redirect('event_detail', pk=event.id)
    else:
        form = RegistrationForm()

    return render(request, 'events/event_register_form.html', {'form': form, 'event': event})

@login_required
def profile_view(request):
    user = request.user
    
    # Initialize context with data common to all users
    context = {
        'user': user,
        'profile_form': UserProfileForm(instance=user),
    }

    if user.user_type == 'organizer':
        # For organizers, get the events they have organized
        organized_events = Event.objects.filter(organizer=user).order_by('-created_at')
        context['organized_events'] = organized_events
    else:
        # For participants, get their registrations and certificates
        registrations = Registration.objects.filter(user=user).order_by('-registered_at')
        certificates = Certificate.objects.filter(participant=user).order_by('-uploaded_at')
        
        form = CertificateUploadForm(user=user)
        
        context['registrations'] = registrations
        context['certificates'] = certificates
        context['certificate_form'] = form

    return render(request, 'events/profile.html', context)

@login_required
def delete_certificate(request, cert_id):
    certificate = get_object_or_404(Certificate, id=cert_id, participant=request.user)
    certificate.delete()
    messages.success(request, "Certificate deleted.")
    return redirect('profile')

@login_required
def update_profile(request):
    """Update user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    return redirect('profile')

@login_required
def upload_certificate(request):
    """Upload certificate"""
    if request.method == 'POST':
        form = CertificateUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.participant = request.user
            certificate.save()
            messages.success(request, 'Certificate uploaded successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    return redirect('profile')

@login_required
def delete_certificate(request, cert_id):
    certificate = get_object_or_404(Certificate, id=cert_id, participant=request.user)
    certificate.delete()
    messages.success(request, "Certificate deleted successfully.")
    return redirect('profile')


@login_required
def generate_cv(request):
    """Generate CV based on user's certificates and events"""
    user = request.user
    certificates = Certificate.objects.filter(participant=user)
    attended_events = EventRegistration.objects.filter(participant=user, attended=True)
    
    context = {
        'user': user,
        'certificates': certificates,
        'attended_events': attended_events,
    }
    return render(request, 'events/cv_template.html', context)

@login_required
def messaging_inbox(request):
    """Messaging inbox"""
    received_messages = Message.objects.filter(receiver=request.user)
    sent_messages = Message.objects.filter(sender=request.user)
    users = User.objects.exclude(id=request.user.id)
    
    context = {
        'received_messages': received_messages,
        'sent_messages': sent_messages,
        'users': users,
        'message_form': MessageForm(sender=request.user),
    }
    return render(request, 'events/messaging.html', context)

@login_required
def send_message(request):
    """Send a message"""
    if request.method == 'POST':
        form = MessageForm(request.POST, sender=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            messages.success(request, 'Message sent successfully!')
        else:
            messages.error(request, 'Error sending message.')
    
    return redirect('messaging_inbox')

@login_required
def conversation_view(request, user_id):
    """View conversation with specific user"""
    other_user = get_object_or_404(User, id=user_id)
    
    conversation = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')
    
    # Mark messages as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)
    
    context = {
        'other_user': other_user,
        'conversation': conversation,
    }
    return render(request, 'events/conversation.html', context)

@login_required
def add_feedback(request, event_id):
    """Add feedback for an event"""
    event = get_object_or_404(Event, id=event_id)
    
    # Check if user attended the event
    if not EventRegistration.objects.filter(event=event, participant=request.user, attended=True).exists():
        messages.error(request, 'You can only provide feedback for events you attended.')
        return redirect('event_detail', pk=event_id)
    
    if request.method == 'POST':
        form = EventFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.event = event
            feedback.participant = request.user
            feedback.save()
            messages.success(request, 'Feedback submitted successfully!')
        else:
            messages.error(request, 'Error submitting feedback.')
    
    return redirect('event_detail', pk=event_id)

@login_required
def add_suggestion(request, event_id):
    """Add suggestion for an event"""
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = EventSuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.event = event
            suggestion.participant = request.user
            suggestion.save()
            messages.success(request, 'Suggestion submitted successfully!')
        else:
            messages.error(request, 'Error submitting suggestion.')
    
    return redirect('event_detail', pk=event.id)

@login_required
def organizer_dashboard(request):
    """Dashboard for organizers"""
    if request.user.user_type != 'organizer':
        messages.error(request, 'Access denied. Organizers only.')
        return redirect('home')
    
    events = Event.objects.filter(organizer=request.user).order_by('-created_at')
    upcoming_events_count = len([event for event in events if event.status == 'upcoming'])
    completed_events_count = len([event for event in events if event.status == 'completed'])
    total_registrations = sum(event.registered_count for event in events)
    
    context = {
        'events': events,
        'upcoming_events_count': upcoming_events_count,
        'completed_events_count': completed_events_count,
        'total_registrations': total_registrations,
    }
    return render(request, 'events/organizer_dashboard.html', context)

@login_required
def event_registrations(request, event_id):
    """View registrations for an event (organizers only)"""
    event = get_object_or_404(Event, id=event_id)
    
    if event.organizer != request.user:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    registrations = EventRegistration.objects.filter(event=event).order_by('-registered_at')
    
    context = {
        'event': event,
        'registrations': registrations,
    }
    return render(request, 'events/event_registrations.html', context)

@login_required
def event_create(request):
    """Create a new event (organizers only)"""
    if request.user.user_type != 'organizer':
        messages.error(request, 'Access denied. Organizers only.')
        return redirect('home')

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('organizer_dashboard')
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form, 'action': 'create'})

@login_required
def event_update(request, pk):
    """Update an existing event (organizers only)"""
    event = get_object_or_404(Event, pk=pk)
    if request.user.user_type != 'organizer' or event.organizer != request.user:
        messages.error(request, 'Access denied. You are not the organizer of this event.')
        return redirect('home')

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('organizer_dashboard')
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form, 'action': 'update', 'event': event})

@login_required
def event_delete(request, pk):
    """Delete an event (organizers only)"""
    event = get_object_or_404(Event, pk=pk)
    if request.user.user_type != 'organizer' or event.organizer != request.user:
        messages.error(request, 'Access denied. You are not the organizer of this event.')
        return redirect('home')

    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('organizer_dashboard')
    return render(request, 'events/event_confirm_delete.html', {'event': event})



# from django.shortcuts import render, get_object_or_404
# from django.core.mail import send_mail
# from django.conf import settings
# from .forms import SimpleRegistrationForm
# from .models import Event

# def event_registration(request, event_id):
#     event = get_object_or_404(Event, id=event_id)

#     if request.method == 'POST':
#         form = SimpleRegistrationForm(request.POST)
#         if form.is_valid():
#             name = form.cleaned_data['name']
#             email = form.cleaned_data['email']

#             # Send confirmation email
#             send_mail(
#                 subject=f"You're registered for {event.title}",
#                 message=f"Hi {name},\n\nThanks for registering for {event.title}!\nDate: {event.date}\nLocation: {event.location}\n\nSee you there!",
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[email],
#                 fail_silently=False,
#             )

#             return render(request, 'events/event_confirm_detail.html', {'event': event, 'email': email})
#     else:
#         form = SimpleRegistrationForm()

#     return render(request, 'events/event_registration.html', {'form': form, 'event': event})


# views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Registration

from django.http import HttpResponse
from .models import Registration

from django.contrib import messages
import logging
logger = logging.getLogger(__name__)

@login_required
def cancel_registration(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    try:
        registration = Registration.objects.get(event=event, user=request.user)
        registration.delete()
        messages.success(request, f'You have cancelled your registration for {event.title}.')
    except Registration.DoesNotExist:
        messages.warning(request, 'You were not registered for this event.')

    # ✅ Redirect back to event detail page
    return redirect('event_detail', pk=event.id)