"""
Management command to audit (and optionally fix) missing/invalid gender data
for wardens and students. This helps ensure gender-based routing works.

Usage:
    python manage.py check_gender_data               # report only
    python manage.py check_gender_data --fix-warden M --fix-student F

Notes:
- Only sets gender where it is missing/invalid; it will NOT override valid values.
- Valid values are 'M' and 'F'.
"""

from django.core.management.base import BaseCommand
from gatepass.models import User, Student


VALID = {"M", "F"}


class Command(BaseCommand):
    help = "Audit and optionally fix gender data for wardens and students."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix-warden",
            choices=["M", "F"],
            help="Set missing/invalid warden gender to this value",
        )
        parser.add_argument(
            "--fix-student",
            choices=["M", "F"],
            help="Set missing/invalid student gender to this value",
        )

    def handle(self, *args, **options):
        fix_warden = options.get("fix_warden")
        fix_student = options.get("fix_student")

        # Wardens: missing/invalid
        warden_qs = User.objects.filter(role="warden")
        invalid_wardens = warden_qs.exclude(gender__in=VALID)

        # Students: missing/invalid
        student_qs = Student.objects.select_related("user")
        invalid_students = student_qs.exclude(user__gender__in=VALID)

        self.stdout.write(self.style.WARNING("=== Gender Audit ==="))
        self.stdout.write(
            f"Wardens total: {warden_qs.count()} | Missing/invalid: {invalid_wardens.count()}"
        )
        self.stdout.write(
            f"Students total: {student_qs.count()} | Missing/invalid: {invalid_students.count()}"
        )

        if invalid_wardens.exists():
            self.stdout.write(self.style.WARNING("\nWardens missing/invalid:"))
            for u in invalid_wardens:
                self.stdout.write(f" - {u.username} | gender='{u.gender}' | approved={u.is_approved}")

        if invalid_students.exists():
            self.stdout.write(self.style.WARNING("\nStudents missing/invalid:"))
            for s in invalid_students:
                self.stdout.write(
                    f" - {s.student_name} | user='{s.user.username}' | gender='{s.user.gender}'"
                )

        # Apply fixes if requested
        if fix_warden and invalid_wardens.exists():
            updated = invalid_wardens.update(gender=fix_warden)
            self.stdout.write(
                self.style.SUCCESS(f"\nUpdated {updated} warden(s) to gender='{fix_warden}'")
            )

        if fix_student and invalid_students.exists():
            count = 0
            for s in invalid_students:
                s.user.gender = fix_student
                s.user.save(update_fields=["gender"])
                count += 1
            self.stdout.write(
                self.style.SUCCESS(f"Updated {count} student(s) to gender='{fix_student}'")
            )

        self.stdout.write(self.style.SUCCESS("\nAudit complete."))

