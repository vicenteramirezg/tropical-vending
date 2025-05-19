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
        
        # If this is an update, get the old value to calculate the difference
        if not is_new:
            old_instance = RestockEntry.objects.get(pk=self.pk)
            old_restocked = old_instance.restocked
        
        # Call the parent save method
        super().save(*args, **kwargs)
        
        # Update current stock in MachineItemPrice
        machine = self.visit_machine_restock.machine
        try:
            machine_item = machine.item_prices.get(product=self.product)
            machine_item.current_stock = self.stock_before - self.discarded + self.restocked
            machine_item.save(update_fields=['current_stock', 'updated_at'])
        except machine.item_prices.model.DoesNotExist:
            # If the product doesn't exist in the machine yet, we don't update anything
            pass
        
        # Update product warehouse inventory
        # Only deduct inventory for new items, or the difference for updated items
        try:
            if is_new:
                # For new entries, subtract the full restocked amount from inventory
                self.product.update_inventory(-self.restocked)
            else:
                # For updates, only adjust for the difference in restocked amount
                inventory_change = old_restocked - self.restocked
                if inventory_change != 0:
                    self.product.update_inventory(inventory_change)
        except ValueError as e:
            # Handle case where there's not enough inventory
            # You might want to add custom error handling here
            raise 