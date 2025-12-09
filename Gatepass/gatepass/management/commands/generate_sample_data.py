from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from gatepass.models import Student, Warden, Security, GatePass
from django.utils import timezone
from datetime import datetime, timedelta
import random
import string

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate sample data for testing capacity with 2000-5000 people'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=2500,
            help='Number of students to generate (default: 2500, range: 2000-5000)'
        )
        parser.add_argument(
            '--wardens',
            type=int,
            default=20,
            help='Number of wardens to generate (default: 20)'
        )
        parser.add_argument(
            '--security',
            type=int,
            default=30,
            help='Number of security staff to generate (default: 30)'
        )

    def handle(self, *args, **options):
        count = options['count']
        warden_count = options['wardens']
        security_count = options['security']

        # Validate count
        if count < 2000 or count > 5000:
            self.stdout.write(
                self.style.ERROR(f'Count must be between 2000 and 5000. Got {count}')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'Starting to generate sample data...')
        )
        self.stdout.write(f'Students: {count}, Wardens: {warden_count}, Security: {security_count}')

        try:
            # Generate Wardens
            self.stdout.write('Generating wardens...')
            self.generate_wardens(warden_count)

            # Generate Security Staff
            self.stdout.write('Generating security staff...')
            self.generate_security_staff(security_count)

            # Generate Students
            self.stdout.write(f'Generating {count} students...')
            self.generate_students(count)

            # Generate Sample GatePasses
            self.stdout.write('Generating sample gate passes...')
            self.generate_sample_gatepasses(count // 5)  # 20% of students have gate passes

            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully generated all sample data!')
            )
            self.stdout.write(f'Total Students: {count}')
            self.stdout.write(f'Total Wardens: {warden_count}')
            self.stdout.write(f'Total Security Staff: {security_count}')
            self.stdout.write(f'Total GatePasses: {count // 5}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

    def generate_random_string(self, length=8):
        """Generate random string"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def generate_random_mobile(self):
        """Generate random 10-digit mobile number"""
        return ''.join([str(random.randint(0, 9)) for _ in range(10)])

    def generate_wardens(self, count):
        """Generate warden users and profiles"""
        departments = ['Boys Hostel A', 'Boys Hostel B', 'Girls Hostel A', 'Girls Hostel B', 'Central']
        genders = ['M', 'F']

        for i in range(count):
            try:
                username = f'warden_{i+1}'
                if User.objects.filter(username=username).exists():
                    continue

                email = f'warden{i+1}@gatepass.com'
                mobile = self.generate_random_mobile()

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='Warden@123',
                    role='warden',
                    mobile_number=mobile,
                    gender=random.choice(genders),
                    is_approved=True,
                    first_name=f'Warden{i+1}'
                )

                Warden.objects.create(
                    user=user,
                    name=f'Warden {i+1}',
                    department=random.choice(departments)
                )
                self.stdout.write(f'  Created warden: {username}')

            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  Error creating warden {i+1}: {str(e)}'))
                continue

    def generate_security_staff(self, count):
        """Generate security users and profiles"""
        shifts = ['Morning', 'Afternoon', 'Night']

        for i in range(count):
            try:
                username = f'security_{i+1}'
                if User.objects.filter(username=username).exists():
                    continue

                email = f'security{i+1}@gatepass.com'
                mobile = self.generate_random_mobile()

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='Security@123',
                    role='security',
                    mobile_number=mobile,
                    gender='M',
                    is_approved=True,
                    first_name=f'Security{i+1}'
                )

                Security.objects.create(
                    user=user,
                    name=f'Security Staff {i+1}',
                    shift=random.choice(shifts)
                )
                self.stdout.write(f'  Created security staff: {username}')

            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  Error creating security {i+1}: {str(e)}'))
                continue

    def generate_students(self, count):
        """Generate student users and profiles"""
        first_names = ['Raj', 'Priya', 'Amit', 'Neha', 'Arjun', 'Isha', 'Vikram', 'Ananya', 'Rohan', 'Diya']
        last_names = ['Singh', 'Patel', 'Kumar', 'Sharma', 'Gupta', 'Reddy', 'Verma', 'Joshi', 'Nair', 'Rao']
        genders = ['M', 'F']
        rooms = ['A101', 'A102', 'B101', 'B102', 'C101', 'C102', 'D101', 'D102']

        batch_size = 500
        users_to_create = []
        students_to_create = []
        created_count = 0

        # Get existing count to avoid conflicts
        existing_students = Student.objects.values_list('hall_ticket_no', flat=True)
        existing_usernames = User.objects.values_list('username', flat=True)
        existing_set = set(existing_students)
        username_set = set(existing_usernames)

        for i in range(count):
            try:
                # Generate unique hall ticket
                base_index = i + 1000  # Start from 1000 to avoid conflicts
                hall_ticket = f'20{base_index % 24:02d}{base_index % 100000:05d}'

                # Skip if already exists
                if hall_ticket in existing_set:
                    continue

                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                student_name = f'{first_name} {last_name}'
                username = f'student_{base_index}'

                if username in username_set:
                    continue

                email = f'student{base_index}@gatepass.com'
                mobile = self.generate_random_mobile()
                parent_mobile = self.generate_random_mobile()
                gender = random.choice(genders)

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='Student@123',
                    role='student',
                    mobile_number=mobile,
                    gender=gender,
                    is_approved=True,
                    first_name=first_name,
                    last_name=last_name
                )

                Student.objects.create(
                    user=user,
                    hall_ticket_no=hall_ticket,
                    student_name=student_name,
                    room_no=random.choice(rooms),
                    parent_name=f'{first_name} Parent',
                    parent_mobile=parent_mobile
                )

                created_count += 1
                existing_set.add(hall_ticket)
                username_set.add(username)

                if created_count % 500 == 0:
                    self.stdout.write(f'  Created {created_count} students...')

            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  Error creating student {i+1}: {str(e)}'))
                continue

        self.stdout.write(self.style.SUCCESS(f'  Total students created: {created_count}'))

    def generate_sample_gatepasses(self, count):
        """Generate sample gate passes for students"""
        purposes = [
            'Home visit',
            'Medical emergency',
            'Family emergency',
            'Doctor appointment',
            'University work',
            'Project work',
            'Interview',
            'Personal work'
        ]
        statuses = ['pending', 'warden_approved', 'security_approved', 'returned', 'completed']

        students = list(Student.objects.all()[:count])
        wardens = list(User.objects.filter(role='warden'))
        security_users = list(User.objects.filter(role='security'))

        for i, student in enumerate(students):
            try:
                outing_date = timezone.now().date() + timedelta(days=random.randint(1, 30))
                outing_time = timezone.now().time().replace(hour=random.randint(8, 17), minute=0, second=0)
                expected_return_date = outing_date + timedelta(days=random.randint(1, 7))
                expected_return_time = timezone.now().time().replace(hour=random.randint(18, 22), minute=0, second=0)

                status = random.choice(statuses)

                gatepass = GatePass.objects.create(
                    student=student,
                    outing_date=outing_date,
                    outing_time=outing_time,
                    expected_return_date=expected_return_date,
                    expected_return_time=expected_return_time,
                    purpose=random.choice(purposes),
                    status=status,
                    warden_approval=random.choice(wardens) if wardens else None,
                    security_approval=random.choice(security_users) if security_users else None,
                    parent_verification=random.choice([True, False]),
                    actual_return_date=expected_return_date if status in ['returned', 'completed'] else None,
                    actual_return_time=expected_return_time if status in ['returned', 'completed'] else None,
                )

                if (i + 1) % 200 == 0:
                    self.stdout.write(f'  Created {i + 1} gate passes...')

            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  Error creating gatepass for student {i+1}: {str(e)}'))
                continue

        self.stdout.write(self.style.SUCCESS(f'  Total gate passes created: {len(students)}'))
