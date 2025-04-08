from django.db import models


class MachineItemPrice(models.Model):
    machine = models.ForeignKey('core.Machine', on_delete=models.CASCADE, related_name='item_prices', db_index=True)
    product = models.ForeignKey('core.Product', on_delete=models.CASCADE, related_name='machine_prices', db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    slot = models.PositiveIntegerField(help_text="Numeric slot position in the machine", null=True, blank=True, default=1)
    current_stock = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ('machine', 'product'),
            # ('machine', 'slot')  # Temporarily disabled - will be re-enabled in the future
        ]
        indexes = [
            models.Index(fields=['machine', 'product']),
            models.Index(fields=['machine', 'slot']),  # Index for querying by slot
            models.Index(fields=['price']),
        ]

    def __str__(self):
        slot_display = f"Slot {self.slot}: " if self.slot else ""
        return f"{slot_display}{self.product.name} at {self.machine} - ${self.price}"
        
    @property
    def profit_margin(self):
        """Calculate profit margin as a percentage"""
        if not self.product.average_cost or self.price == 0:
            return 0
        
        cost = self.product.average_cost
        return ((self.price - cost) / self.price) * 100 