from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import  EventFeedback, Message, EventSuggestion, Certificate, Event, Registration
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone (Optional)'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Bio (Optional)'}), required=False)
    user_type = forms.ChoiceField(
        choices=[('organizer', 'Organizer'), ('participant', 'Participant')],
        widget=forms.HiddenInput()
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'bio', 'password1', 'password2', 'user_type')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Password', 'autocomplete': 'off'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'autocomplete': 'off'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password1')
        user_type = cleaned_data.get('user_type')

        if user_type == 'organizer' and password and not password.startswith('admin'):
            self.add_error('password1', "Invalid Password.")

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'bio', 'profile_picture')

class EventFeedbackForm(forms.ModelForm):
    class Meta:
        model = EventFeedback
        fields = ('rating', 'comment')
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.HiddenInput()
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('receiver', 'content')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)
        if sender:
            self.fields['receiver'].queryset = User.objects.exclude(id=sender.id)

class EventSuggestionForm(forms.ModelForm):
    class Meta:
        model = EventSuggestion
        fields = ('suggestion',)
        widgets = {
            'suggestion': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter your suggestion for this event...'})
        }

class CertificateUploadForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['name', 'certificate_file', 'certificate_type']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        self.fields['name'].widget.attrs.update({
            'placeholder': 'Enter certificate name',
            'class': 'form-control'
        })
        self.fields['certificate_file'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['certificate_type'].widget.attrs.update({
            'class': 'form-control'
        })

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['organizer', 'created_at', 'updated_at', 'duration']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email address'}),
        }