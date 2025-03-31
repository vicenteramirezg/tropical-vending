from django.db import models


class RestockEntry(models.Model):
    visit_machine_restock = models.ForeignKey('core.VisitMachineRestock', on_delete=models.CASCADE, related_name='restock_entries')
    product = models.ForeignKey('core.Product', on_delete=models.CASCADE, related_name='restock_entries')
    stock_before = models.IntegerField()
    restocked = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} in {self.visit_machine_restock.machine} restocked: {self.restocked}"
    
    def save(self, *args, **kwargs):
        """Update current_stock in MachineItemPrice when restocking"""
        super().save(*args, **kwargs)
        
        # Update current stock in MachineItemPrice
        machine = self.visit_machine_restock.machine
        try:
            machine_item = machine.item_prices.get(product=self.product)
            machine_item.current_stock = self.stock_before + self.restocked
            machine_item.save(update_fields=['current_stock', 'updated_at'])
        except machine.item_prices.model.DoesNotExist:
            # If the product doesn't exist in the machine yet, we don't update anything
            pass 