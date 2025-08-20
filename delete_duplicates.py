from django.db.models import Count
from events.models import Registration

duplicates = Registration.objects.values('event', 'user').annotate(count=Count('id')).filter(count__gt=1)

for duplicate in duplicates:
    event_id = duplicate['event']
    user_id = duplicate['user']
    
    # Get all duplicate registrations for this event and user
    registrations_to_delete = Registration.objects.filter(event=event_id, user=user_id).order_by('registered_at')
    
    # Keep the first one, delete the rest
    for registration in registrations_to_delete[1:]:
        registration.delete()

print("Duplicate registrations removed.")