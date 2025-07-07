# Railway Production Deployment Steps

## 🚀 **Quick Deployment Guide**

### Step 1: Commit All Changes
```bash
# From project root
git add .
git commit -m "feat: Add supplier model and migrate from varchar to foreign key

- Add Supplier model with full CRUD functionality  
- Migrate WholesalePurchase.supplier from CharField to ForeignKey
- Preserve backward compatibility with supplier_name field
- Add comprehensive supplier management UI
- Create data migration for existing purchases"
```

### Step 2: Create Database Backup (CRITICAL)
```bash
# Install Railway CLI if not already installed
npm install -g @railway/cli

# Login and create backup
railway login
railway run pg_dump $DATABASE_URL > supplier_migration_backup_$(date +%Y%m%d_%H%M%S).sql
```

### Step 3: Deploy to Railway
```bash
# Push to trigger auto-deployment (if enabled)
git push origin main

# OR manually deploy
railway up
```

### Step 4: Monitor Deployment
```bash
# Watch logs during deployment
railway logs --follow

# Look for these migration messages:
# - Applying core.0004_create_supplier_model
# - Applying core.0005_add_supplier_name_field
# - Applying core.0006_migrate_supplier_data  
# - Applying core.0007_add_supplier_foreign_key
```

### Step 5: Verify Deployment
```bash
# Check migration status
railway run python manage.py showmigrations core

# Verify database state
railway run python manage.py shell -c "
from core.models import Supplier, WholesalePurchase
print(f'Suppliers: {Supplier.objects.count()}')
print(f'Purchases: {WholesalePurchase.objects.count()}')
for s in Supplier.objects.all():
    print(f'- {s.name}: {s.wholesale_purchases.count()} purchases')
"
```

## ✅ **Expected Results**
- **4 Suppliers created**: Unknown Supplier, Sams Club, Walmart, Costco
- **All existing purchases** linked to "Unknown Supplier" 
- **API endpoints** working: `/api/suppliers/`
- **Frontend** supplier management functional

## 🚨 **If Something Goes Wrong**
```bash
# Rollback migrations
railway run python manage.py migrate core 0003

# Restore from backup
railway run psql $DATABASE_URL < supplier_migration_backup_[timestamp].sql
```

## 🔧 **Environment Check**
Ensure Railway environment has:
- `DATABASE_URL` (PostgreSQL)
- `DJANGO_SETTINGS_MODULE=vendingapp.settings`
- `DEBUG=False`
- `ALLOWED_HOSTS` includes your Railway domain

---
**Total deployment time: ~2-5 minutes** 