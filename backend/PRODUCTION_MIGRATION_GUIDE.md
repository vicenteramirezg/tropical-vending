# Production Migration Guide: Railway + PostgreSQL

## Overview
This guide covers the safe deployment of the supplier migration to Railway production environment with PostgreSQL.

## ⚠️ **CRITICAL: Pre-Migration Checklist**

### 1. **Database Backup** (MANDATORY)
```bash
# Connect to Railway PostgreSQL and create backup
railway login
railway environment production
railway run pg_dump $DATABASE_URL > supplier_migration_backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. **Verify Current State**
```bash
# Check current migration status in production
railway run python manage.py showmigrations core
```

### 3. **Test Migration on Staging** (HIGHLY RECOMMENDED)
- Create a staging environment with production data copy
- Test the complete migration process
- Verify functionality works as expected

## 🚀 **Step-by-Step Production Deployment**

### Step 1: Prepare Local Environment
```bash
# Ensure all changes are committed
git add .
git commit -m "feat: Add supplier model and migrate from varchar to foreign key

- Add Supplier model with full CRUD functionality
- Migrate WholesalePurchase.supplier from CharField to ForeignKey
- Preserve backward compatibility with supplier_name field
- Add comprehensive supplier management UI
- Create data migration for existing purchases"

# Push to your main branch
git push origin main
```

### Step 2: Pre-Deployment Verification
```bash
# Verify migrations are ready
python manage.py makemigrations --dry-run
python manage.py migrate --plan

# Check for any pending migrations
python manage.py showmigrations
```

### Step 3: Deploy to Railway

#### Option A: Automatic Deployment (if auto-deploy enabled)
```bash
# Railway will automatically deploy when you push to main
# Monitor the deployment in Railway dashboard
```

#### Option B: Manual Deployment
```bash
railway login
railway link [your-project-id]
railway up
```

### Step 4: Monitor Deployment
1. **Watch Railway Logs**:
   ```bash
   railway logs --follow
   ```

2. **Check Build Status** in Railway Dashboard
3. **Verify Migration Execution** in logs

### Step 5: Post-Deployment Verification

#### Verify Database State
```bash
# Connect to production database
railway run python manage.py shell

# In Django shell:
from core.models import Supplier, WholesalePurchase
print(f"Suppliers: {Supplier.objects.count()}")
print(f"Purchases: {WholesalePurchase.objects.count()}")

# Check supplier relationships
for purchase in WholesalePurchase.objects.all():
    print(f"Purchase {purchase.id}: {purchase.supplier.name if purchase.supplier else 'None'}")
```

#### Test API Endpoints
```bash
# Test supplier endpoints
curl https://your-app.railway.app/api/suppliers/
curl https://your-app.railway.app/api/wholesale-purchases/
```

#### Verify Frontend Functionality
1. Access your production app
2. Test supplier management features
3. Test purchase form with supplier dropdown
4. Verify existing data displays correctly

## 🔄 **Migration Execution Order in Production**

Railway will automatically run these migrations in sequence:
1. `0004_create_supplier_model` - Creates Supplier table
2. `0005_add_supplier_name_field` - Adds legacy field
3. `0006_migrate_supplier_data` - Migrates data and creates suppliers
4. `0007_add_supplier_foreign_key` - Adds foreign key relationships

## 🚨 **Troubleshooting Common Issues**

### Issue 1: Migration Timeout
```bash
# If migration times out, run manually:
railway run python manage.py migrate core 0004
railway run python manage.py migrate core 0005
railway run python manage.py migrate core 0006
railway run python manage.py migrate core 0007
```

### Issue 2: Data Migration Fails
```bash
# Check for data conflicts
railway run python manage.py shell
# Inspect existing data before migration
```

### Issue 3: Foreign Key Constraint Errors
```bash
# Verify supplier data exists
railway run python manage.py shell -c "
from core.models import Supplier
print('Suppliers:', list(Supplier.objects.values_list('name', flat=True)))
"
```

## 🔙 **Rollback Plan** (Emergency Only)

### If Migration Fails Completely:
```bash
# 1. Rollback to previous migration
railway run python manage.py migrate core 0003

# 2. Restore from backup
railway run psql $DATABASE_URL < supplier_migration_backup_[timestamp].sql

# 3. Redeploy previous version
git revert [commit-hash]
git push origin main
```

### If Partial Migration Success:
```bash
# Check which migrations applied
railway run python manage.py showmigrations core

# Apply remaining migrations manually
railway run python manage.py migrate core [target-migration]
```

## ✅ **Post-Migration Checklist**

- [ ] All 4 migrations applied successfully
- [ ] Supplier table created with default suppliers
- [ ] All purchases have supplier relationships
- [ ] API endpoints responding correctly
- [ ] Frontend supplier management working
- [ ] Purchase forms using dynamic suppliers
- [ ] No data loss confirmed
- [ ] Performance acceptable
- [ ] Error monitoring shows no issues

## 🔧 **Environment Variables Check**

Ensure these are set in Railway:
```
DATABASE_URL=postgresql://...
DJANGO_SETTINGS_MODULE=vendingapp.settings
DEBUG=False
ALLOWED_HOSTS=your-domain.railway.app
```

## 📊 **Expected Results in Production**

After successful migration:
- **Suppliers**: 4 total (Unknown Supplier + 3 defaults)
- **Purchases**: All existing purchases linked to "Unknown Supplier"
- **API**: Full CRUD operations for suppliers
- **UI**: Complete supplier management interface
- **Data**: Zero data loss, full backward compatibility

## 🚀 **Performance Considerations**

- Migration should complete in < 30 seconds for typical datasets
- No downtime expected during migration
- Database indexes automatically created
- Foreign key constraints improve query performance

## 📞 **Support Contacts**

If issues occur:
1. Check Railway logs first
2. Verify database state with Django shell
3. Review migration status with `showmigrations`
4. Use rollback plan if necessary

---

**Remember**: Always test on staging first, backup production data, and have a rollback plan ready! 