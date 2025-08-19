from django.db import models


class RestockEntry(models.Model):
    visit_machine_restock = models.ForeignKey('core.VisitMachineRestock', on_delete=models.CASCADE, related_name='restock_entries')
    product = models.ForeignKey('core.Product', on_delete=models.CASCADE, related_name='restock_entries')
    stock_before = models.IntegerField()
    discarded = models.IntegerField(default=0)
    restocked = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} in {self.visit_machine_restock.machine} restocked: {self.restocked}"
    
    def save(self, *args, **kwargs):
        """Update current_stock in MachineItemPrice when restocking and reduce product inventory"""
        # Track if this is a new record (no ID yet) or an update
        is_new = self.pk is None
        
        # Skip automatic inventory updates if bulk_save flag is set
        # This allows bulk operations to handle inventory updates more efficiently
        skip_inventory_update = kwargs.pop('skip_inventory_update', False)
        
        # Call the parent save method
        super().save(*args, **kwargs)
        
        # Only perform these actions for new entries and if not skipping updates
        if is_new and not skip_inventory_update:
            # Update current stock in MachineItemPrice using F expression for atomic update
            machine = self.visit_machine_restock.machine
            try:
                from django.db import models
                # Use F expression to avoid race conditions
                models.MachineItemPrice.objects.filter(
                    machine=machine,
                    product=self.product
                ).update(
                    current_stock=self.stock_before - self.discarded + self.restocked
                )
            except Exception:
                # If the product doesn't exist in the machine yet, we don't update anything
                pass
            
            # Update product warehouse inventory using F expression
            try:
                from django.db import models
                # Use F expression for atomic inventory update
                updated_rows = models.Product.objects.filter(
                    id=self.product.id,
                    inventory_quantity__gte=self.restocked  # Ensure sufficient inventory
                ).update(
                    inventory_quantity=models.F('inventory_quantity') - self.restocked
                )
                
                if updated_rows == 0:
                    # Check if product exists and has insufficient inventory
                    product = models.Product.objects.get(id=self.product.id)
                    if product.inventory_quantity < self.restocked:
                        raise ValueError(f"Insufficient inventory. Available: {product.inventory_quantity}, Required: {self.restocked}")
                    else:
                        raise ValueError("Product not found")
                        
            except models.Product.DoesNotExist:
                raise ValueError("Product not found")
            except ValueError:
                raise  # Re-raise inventory errors 