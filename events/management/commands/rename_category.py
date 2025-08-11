from django.core.management.base import BaseCommand
from events.models import Category, Event

class Command(BaseCommand):
    help = 'Renames the "Business" category to "Non-Technical"'

    def handle(self, *args, **options):
        try:
            # Get or create the "Non-Technical" category
            non_technical_category, created = Category.objects.get_or_create(
                name='Non-Technical',
                defaults={'description': 'Soft skills, business, marketing, and other non-technical events'}
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Created "Non-Technical" category.'))

            # Find the "Business" category
            try:
                business_category = Category.objects.get(name='Business')
                
                # Re-assign events from "Business" to "Non-Technical"
                events_to_update = Event.objects.filter(category=business_category)
                if events_to_update.exists():
                    events_to_update.update(category=non_technical_category)
                    self.stdout.write(self.style.SUCCESS(f'Re-assigned {events_to_update.count()} events from "Business" to "Non-Technical".'))

                # Delete the "Business" category if it's not the same as "Non-Technical"
                if business_category.pk != non_technical_category.pk:
                    business_category.delete()
                    self.stdout.write(self.style.SUCCESS('Deleted "Business" category.'))
                
                self.stdout.write(self.style.SUCCESS('Successfully replaced "Business" category with "Non-Technical".'))

            except Category.DoesNotExist:
                self.stdout.write(self.style.WARNING('Category "Business" not found. No changes made.'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An error occurred: {e}'))
