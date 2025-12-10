"""
Management command to clear all gatepass data.
This is useful when you need to delete many records without hitting the admin limit.

Usage:
    python manage.py clear_gatepass_data
    python manage.py clear_gatepass_data --confirm  # Skip confirmation prompt
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from gatepass.models import GatePass, Notification, ParentVerification


class Command(BaseCommand):
    help = 'Clear all gatepass data (gatepasses, notifications, parent verifications)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        # Count records
        gatepass_count = GatePass.objects.count()
        notification_count = Notification.objects.count()
        verification_count = ParentVerification.objects.count()

        if gatepass_count == 0 and notification_count == 0 and verification_count == 0:
            self.stdout.write(self.style.SUCCESS('No gatepass data to delete.'))
            return

        # Show summary
        self.stdout.write(self.style.WARNING('\n=== Gatepass Data Summary ==='))
        self.stdout.write(f'GatePass records: {gatepass_count}')
        self.stdout.write(f'Notification records: {notification_count}')
        self.stdout.write(f'ParentVerification records: {verification_count}')
        self.stdout.write('')

        # Confirmation
        if not options['confirm']:
            confirm = input('Are you sure you want to delete ALL gatepass data? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Operation cancelled.'))
                return

        # Delete in transaction
        try:
            with transaction.atomic():
                # Delete in correct order (respecting foreign keys)
                deleted_notifications = Notification.objects.all().delete()
                deleted_verifications = ParentVerification.objects.all().delete()
                deleted_gatepasses = GatePass.objects.all().delete()

                self.stdout.write(self.style.SUCCESS('\n=== Deletion Summary ==='))
                self.stdout.write(f'Deleted GatePass records: {deleted_gatepasses[0]}')
                self.stdout.write(f'Deleted Notification records: {deleted_notifications[0]}')
                self.stdout.write(f'Deleted ParentVerification records: {deleted_verifications[0]}')
                self.stdout.write(self.style.SUCCESS('\nAll gatepass data has been cleared successfully!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nError occurred during deletion: {str(e)}'))
            raise

