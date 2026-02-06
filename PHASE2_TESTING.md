# Phase 2: Testing Guide

## Quick Test Instructions

### ✅ Step 1: Verify URL Loading

Start the server and check console output:

```bash
python manage.py runserver
```

**Expected Output:**
```
Loaded URLs for module: attendance
Loaded URLs for module: payroll
Loaded URLs for module: timetable
Django version 4.2.8, using settings 'config.settings.dev'
Starting development server at http://127.0.0.1:8000/
```

✅ If you see "Loaded URLs for module" messages, Phase 2 is working!

---

### ✅ Step 2: Test Module Installation

1. **Visit Dashboard:**
   ```
   http://localhost:8000/dashboard/
   ```

2. **Click "Install" on Attendance Module**

3. **Expected Behavior:**
   - ✅ Redirected to `/attendance/`
   - ✅ See Attendance module homepage with 📋 icon
   - ✅ Success message: "Attendance has been installed and activated!"
   - ✅ Page shows: Mark Attendance, Reports, Settings cards

---

### ✅ Step 3: Test "Open" Button

1. **Return to Dashboard:**
   ```
   http://localhost:8000/dashboard/
   ```

2. **Attendance Card Now Shows:**
   - ✅ "Open" button (instead of "Install")
   - ✅ Button color matches module theme

3. **Click "Open":**
   - ✅ Redirected to `/attendance/`
   - ✅ Same module homepage loads

---

### ✅ Step 4: Test Access Control (Important!)

**Try accessing an UNINSTALLED module:**

If Payroll is not installed, try:
```
http://localhost:8000/payroll/
```

**Expected Behavior:**
- ❌ Access denied
- ✅ Redirected to dashboard
- ✅ Error message: "The payroll module is not installed. Please install it from the dashboard."

**This proves the middleware is working!**

---

### ✅ Step 5: Test All Module URLs

After installing Attendance, test these URLs:

```bash
# Main page
http://localhost:8000/attendance/

# Sub-pages
http://localhost:8000/attendance/mark/
http://localhost:8000/attendance/reports/
```

**Expected Behavior:**
- ✅ All pages load successfully
- ✅ Show "feature coming soon" info message
- ✅ Redirect back to attendance home

---

### ✅ Step 6: Install Multiple Modules

1. Install Payroll → Redirected to `/payroll/` ✅
2. Install Timetable → Redirected to `/timetable/` ✅
3. Return to Dashboard
4. All three modules now show "Open" buttons ✅

---

### ✅ Step 7: Test Navigation

From any module page:

1. **Click "Back to Dashboard"** → Returns to dashboard ✅
2. **Click module feature buttons** → Shows info messages ✅
3. **Use browser back button** → Works normally ✅

---

## Common Issues & Solutions

### Issue: Module URLs not loading

**Symptoms:**
- No "Loaded URLs for module" messages on startup
- 404 errors when accessing `/attendance/`

**Solution:**
1. Verify `urls.py` exists in module directory
2. Check `config/urls.py` includes:
   ```python
   from core.plugins.url_loader import url_loader
   module_urls = url_loader.get_module_urls()
   urlpatterns.extend(module_urls)
   ```
3. Restart server

---

### Issue: Can access uninstalled modules

**Symptoms:**
- Can visit `/payroll/` without installing it

**Solution:**
1. Verify middleware is added to `config/settings/base.py`:
   ```python
   MIDDLEWARE = [
       ...
       'core.plugins.middleware.TenantModuleAccessMiddleware',
   ]
   ```
2. Restart server

---

### Issue: Install button doesn't work

**Symptoms:**
- Clicking "Install" does nothing
- No redirect after clicking

**Solution:**
1. Check browser console for errors
2. Verify CSRF token in template
3. Check `install_module` view in `core/users/views.py`

---

## Verification Checklist

Run through this checklist:

- [ ] Server starts without errors
- [ ] Console shows "Loaded URLs for module" messages
- [ ] Dashboard displays all three modules
- [ ] Uninstalled modules show "Install" button
- [ ] Click "Install" redirects to module page
- [ ] Success message appears after installation
- [ ] Module homepage displays correctly with icon
- [ ] "Back to Dashboard" button works
- [ ] Dashboard now shows "Open" button for installed module
- [ ] Click "Open" navigates to module
- [ ] Accessing uninstalled module URL is blocked
- [ ] Error message shown when accessing uninstalled module
- [ ] Multiple modules can be installed
- [ ] Each tenant sees only their installed modules

**If all boxes are checked, Phase 2 is working perfectly! ✅**

---

## Test with Shell (Optional)

Verify in Django shell:

```bash
python manage.py shell
```

```python
from core.plugins.models import Module, TenantModule
from core.tenants.models import Tenant

# Check modules
Module.objects.all()
# Should show: Attendance, Payroll, Timetable

# Check what's installed for a tenant
tenant = Tenant.objects.first()
TenantModule.objects.filter(tenant=tenant, is_installed=True)
# Should show installed modules

# Test module access
attendance = Module.objects.get(slug='attendance')
TenantModule.objects.filter(tenant=tenant, module=attendance, is_installed=True).exists()
# True = installed, False = not installed
```

---

## Next Steps

Once all tests pass:

✅ **Phase 2 Complete!**  
📋 **Ready for Phase 3:** Build the Attendance module with real functionality

**Current Status:**
- ✅ Phase 1: Module Registry System
- ✅ Phase 2: Dynamic URL Registration
- ⏳ Phase 3: First Real Module (Attendance)

---

## Need Help?

If something doesn't work:

1. Check server console for error messages
2. Review [PHASE2_COMPLETE.md](PHASE2_COMPLETE.md) for detailed docs
3. Verify all files were created correctly
4. Restart the server
5. Clear browser cache

**Happy Testing! 🚀**
