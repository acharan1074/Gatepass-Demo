# How to Delete All Gatepass Data

## Problem
When trying to delete many gatepass records in Django admin, you get this error:
```
TooManyFieldsSent: The number of GET/POST parameters exceeded settings.DATA_UPLOAD_MAX_NUMBER_FIELDS
```

## Solution: Use the Management Command

The easiest way to delete all gatepass data is to use the management command:

### Step 1: Open Terminal/Command Prompt
Navigate to your project directory:
```bash
cd "C:\Users\charan\Downloads\Gatepass final deploy after\Gatepass final deploy\Gatepass nov2\Gatepass"
```

### Step 2: Run the Command

**Option A: With Confirmation Prompt**
```bash
python manage.py clear_gatepass_data
```
This will show you a summary and ask for confirmation before deleting.

**Option B: Skip Confirmation (for scripts)**
```bash
python manage.py clear_gatepass_data --confirm
```

### What Gets Deleted
- All GatePass records
- All Notification records (related to gatepasses)
- All ParentVerification records (related to gatepasses)

### Example Output
```
=== Gatepass Data Summary ===
GatePass records: 1500
Notification records: 3000
ParentVerification records: 1500

Are you sure you want to delete ALL gatepass data? (yes/no): yes

=== Deletion Summary ===
Deleted GatePass records: 1500
Deleted Notification records: 3000
Deleted ParentVerification records: 1500

All gatepass data has been cleared successfully!
```

## Alternative: Delete in Smaller Batches via Admin

If you prefer to use the admin interface:

1. **Restart your Django server** (important for settings to take effect)
2. Go to GatePass admin page
3. Use filters to narrow down records (e.g., by status, date)
4. Delete in batches of 50-100 records at a time
5. The admin now shows only 50 records per page to avoid the error

## Settings Applied

The following settings have been applied to help with bulk operations:
- `DATA_UPLOAD_MAX_NUMBER_FIELDS = 50000` (increased from default 1000)
- Admin pagination set to 50 records per page
- Custom admin action for safe bulk deletion

## If You Still Get Errors

1. **Make sure server is restarted** after changing settings
2. **Use the management command** instead of admin interface
3. **Delete in smaller batches** using filters in admin

