# Gender Filter Debugging Guide

## Issue
Female student requests are showing for male wardens (and vice versa), which should NOT happen.

## What Was Fixed

1. **Warden Dashboard Filter** (`warden_dashboard` view):
   - Now filters requests to show ONLY students with matching gender
   - Male wardens see ONLY 'M' students
   - Female wardens see ONLY 'F' students
   - Case-insensitive comparison added

2. **Notification Logic** (`create_gatepass` view):
   - Only notifies wardens with matching gender
   - Female students notify ONLY female wardens
   - Male students notify ONLY male wardens

3. **Approval Validation** (`warden_approve_gatepass` view):
   - Blocks cross-gender approvals
   - Validates gender before allowing approval

## Steps to Verify the Fix

### 1. Restart Django Server
**CRITICAL**: You MUST restart your Django development server for changes to take effect:
```bash
# Stop the server (Ctrl+C) and restart:
python manage.py runserver
```

### 2. Verify Database Gender Values

Check that gender values are stored correctly in the database:

**For Wardens:**
- Male warden should have: `gender = 'M'` (not 'Male', not 'm', not NULL)
- Female warden should have: `gender = 'F'` (not 'Female', not 'f', not NULL)

**For Students:**
- Male student should have: `gender = 'M'`
- Female student should have: `gender = 'F'`

### 3. Check Database Values

Run this in Django shell to verify:
```python
python manage.py shell

from gatepass.models import User, Student, GatePass

# Check wardens
print("=== WARDENS ===")
for w in User.objects.filter(role='warden'):
    print(f"Warden: {w.username}, Gender: '{w.gender}', Approved: {w.is_approved}")

# Check students
print("\n=== STUDENTS ===")
for s in Student.objects.all()[:10]:
    print(f"Student: {s.student_name}, Gender: '{s.user.gender}'")

# Check pending requests
print("\n=== PENDING REQUESTS ===")
for gp in GatePass.objects.filter(status='pending'):
    print(f"ID: {gp.id}, Student: {gp.student.student_name}, Student Gender: '{gp.student.user.gender}'")
```

### 4. Fix Incorrect Gender Values (if needed)

If gender values are wrong, fix them:
```python
# Fix a warden's gender
warden = User.objects.get(username='warden_username')
warden.gender = 'M'  # or 'F'
warden.save()

# Fix a student's gender
student = Student.objects.get(hall_ticket_no='TICKET123')
student.user.gender = 'F'  # or 'M'
student.user.save()
```

### 5. Test the Filter

1. **As Female Warden:**
   - Login as female warden
   - Should see ONLY requests from female students
   - Should NOT see requests from male students

2. **As Male Warden:**
   - Login as male warden
   - Should see ONLY requests from male students
   - Should NOT see requests from female students

3. **Create New Request:**
   - Female student creates request → Should appear ONLY for female warden
   - Male student creates request → Should appear ONLY for male warden

## Common Issues

### Issue 1: Gender values are NULL or empty
**Solution**: Set gender values for all wardens and students

### Issue 2: Gender values are stored as 'Male'/'Female' instead of 'M'/'F'
**Solution**: Update database to use 'M' and 'F' values

### Issue 3: Server not restarted
**Solution**: Restart Django server

### Issue 4: Case sensitivity
**Solution**: Code now handles this automatically with `.upper()` conversion

## Code Changes Summary

- **Line 687-708**: Added strict gender filtering in `warden_dashboard`
- **Line 412-439**: Updated notification logic to only notify matching gender wardens
- **Line 785-800**: Added gender validation in approval function

All filtering is now case-insensitive and handles NULL/empty values properly.

