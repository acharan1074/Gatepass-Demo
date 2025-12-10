# Verify Gender Filter is Working

## Current Implementation

The gender filter is now implemented in `warden_dashboard` view (lines 694-724):

1. **Gets warden gender** and normalizes it (uppercase, trimmed)
2. **Filters ALL requests** to show ONLY students with matching gender
3. **Applied BEFORE** any other filters (date, status, etc.)

## How to Verify It's Working

### Step 1: Check Database Values

Run this in Django shell to verify gender values:

```python
python manage.py shell

from gatepass.models import User, GatePass, Student

# Check warden genders
print("=== WARDENS ===")
for w in User.objects.filter(role='warden'):
    print(f"Username: {w.username}, Gender: '{w.gender}' (type: {type(w.gender)})")

# Check student genders in pending requests
print("\n=== PENDING REQUESTS WITH STUDENT GENDERS ===")
for gp in GatePass.objects.filter(status='pending'):
    print(f"Request ID: {gp.id}, Student: {gp.student.student_name}, Gender: '{gp.student.user.gender}'")
```

### Step 2: Test the Filter Logic

Test what a male warden should see:

```python
# Get a male warden
male_warden = User.objects.filter(role='warden', gender='M').first()
if male_warden:
    print(f"\n=== What Male Warden '{male_warden.username}' Should See ===")
    # This is what the filter does
    warden_gender = str(male_warden.gender).strip().upper()
    filtered = GatePass.objects.filter(
        student__user__gender=warden_gender
    ).exclude(
        student__user__gender__isnull=True
    ).exclude(
        student__user__gender=''
    )
    print(f"Total requests visible: {filtered.count()}")
    for gp in filtered[:5]:
        print(f"  - {gp.student.student_name} (Gender: '{gp.student.user.gender}')")
```

### Step 3: Verify No Cross-Gender Requests

```python
# Check if male warden can see female student requests (should be 0)
male_warden = User.objects.filter(role='warden', gender='M').first()
if male_warden:
    warden_gender = str(male_warden.gender).strip().upper()
    # This should return 0 - male warden should NOT see female students
    female_requests = GatePass.objects.filter(
        student__user__gender=warden_gender
    ).filter(
        student__user__gender='F'  # This should be empty!
    )
    print(f"\nMale warden seeing female requests: {female_requests.count()} (should be 0)")
```

## Common Issues

### Issue 1: Gender values are NULL or empty
**Solution**: Set gender for all wardens and students:
```python
# Fix warden
warden = User.objects.get(username='warden_username')
warden.gender = 'M'  # or 'F'
warden.save()

# Fix student
student = Student.objects.get(hall_ticket_no='TICKET123')
student.user.gender = 'F'  # or 'M'
student.user.save()
```

### Issue 2: Gender values are stored as 'Male'/'Female' instead of 'M'/'F'
**Solution**: Update to use 'M' and 'F':
```python
# Update all users
User.objects.filter(gender='Male').update(gender='M')
User.objects.filter(gender='Female').update(gender='F')
```

### Issue 3: Server not restarted
**CRITICAL**: After code changes, you MUST restart the Django server:
```bash
# Stop server (Ctrl+C) and restart
python manage.py runserver
```

### Issue 4: Case sensitivity
**Solution**: Code now handles this with `.upper()` conversion, but database should still use 'M'/'F'

## Expected Behavior

✅ **Male Warden Login:**
- Sees ONLY requests from male students (gender='M')
- Does NOT see requests from female students (gender='F')
- Sees 0 requests if no male students have pending requests

✅ **Female Warden Login:**
- Sees ONLY requests from female students (gender='F')
- Does NOT see requests from male students (gender='M')
- Sees 0 requests if no female students have pending requests

## Code Location

The filter is applied in:
- **File**: `gatepass/views.py`
- **Function**: `warden_dashboard` (line 694-724)
- **Applied**: BEFORE date/status filters, so it affects ALL queries

## If Still Not Working

1. **Restart server** (most common issue)
2. **Check database values** using the shell commands above
3. **Verify warden gender is set** correctly in database
4. **Check student genders** in pending requests
5. **Clear browser cache** and try again

