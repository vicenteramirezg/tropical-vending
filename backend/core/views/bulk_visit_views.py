from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction, models
from django.core.exceptions import ValidationError
from core.models import Visit, VisitMachineRestock, RestockEntry, MachineItemPrice, Product
from core.serializers import VisitSerializer
import logging

logger = logging.getLogger(__name__)


class BulkVisitSaveView(APIView):
    """
    Optimized bulk endpoint for saving complete visit data including all machine restocks
    and restock entries in a single atomic transaction.
    
    Expected payload format:
    {
        "visit": {
            "location": 1,
            "visit_date": "2025-01-15T10:30:00Z",
            "notes": "Regular restock",
            "user": 1
        },
        "machine_restocks": [
            {
                "machine": 1,
                "notes": "",
                "restock_entries": [
                    {
                        "product": 1,
                        "stock_before": 5,
                        "discarded": 1,
                        "restocked": 10
                    }
                ]
            }
        ]
    }
    """
    
    def post(self, request):
        """Create a new visit with all associated data in bulk"""
        logger.info(f"Bulk visit save request received. Data keys: {list(request.data.keys())}")
        try:
            with transaction.atomic():
                # Extract visit data
                visit_data = request.data.get('visit', {})
                machine_restocks_data = request.data.get('machine_restocks', [])
                
                logger.info(f"Processing visit for location {visit_data.get('location')} with {len(machine_restocks_data)} machine restocks")
                
                # Validate required fields
                if not visit_data.get('location'):
                    return Response(
                        {'error': 'Location is required'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Set user if not provided
                if not visit_data.get('user') and request.user.is_authenticated:
                    visit_data['user'] = request.user.id
                
                # Create the visit
                visit_serializer = VisitSerializer(data=visit_data, context={'request': request})
                if not visit_serializer.is_valid():
                    return Response(visit_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                visit = visit_serializer.save()
                
                # Process machine restocks in bulk
                self._process_machine_restocks_bulk(visit, machine_restocks_data)
                
                # Return the created visit
                response_serializer = VisitSerializer(visit)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                
        except ValidationError as e:
            logger.error(f"Validation error in bulk visit save: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in bulk visit save: {e}")
            return Response(
                {'error': 'An unexpected error occurred'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, visit_id=None):
        """Update an existing visit with all associated data in bulk"""
        try:
            with transaction.atomic():
                # Get the existing visit
                try:
                    visit = Visit.objects.get(id=visit_id)
                except Visit.DoesNotExist:
                    return Response(
                        {'error': 'Visit not found'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Extract data
                visit_data = request.data.get('visit', {})
                machine_restocks_data = request.data.get('machine_restocks', [])
                
                # Update the visit
                visit_serializer = VisitSerializer(
                    visit, 
                    data=visit_data, 
                    partial=True, 
                    context={'request': request}
                )
                if not visit_serializer.is_valid():
                    return Response(visit_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                visit = visit_serializer.save()
                
                # Clear existing machine restocks and entries to avoid conflicts
                self._clear_existing_restocks(visit)
                
                # Process new machine restocks in bulk
                self._process_machine_restocks_bulk(visit, machine_restocks_data)
                
                # Return the updated visit
                response_serializer = VisitSerializer(visit)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error updating bulk visit: {e}")
            return Response(
                {'error': 'Failed to update visit'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _clear_existing_restocks(self, visit):
        """Clear existing machine restocks and revert inventory changes"""
        # Get all existing machine restocks for this visit with related data
        machine_restocks = VisitMachineRestock.objects.filter(visit=visit).prefetch_related(
            'restock_entries__product',
            'machine__item_prices'
        )
        
        # Collect all inventory changes to revert in bulk
        inventory_updates = {}
        machine_stock_updates = []
        
        for restock in machine_restocks:
            for entry in restock.restock_entries.all():
                # Collect inventory changes to revert
                product_id = entry.product.id
                if product_id not in inventory_updates:
                    inventory_updates[product_id] = 0
                inventory_updates[product_id] += entry.restocked  # Return to inventory
                
                # Collect machine stock changes to revert
                try:
                    machine_item = restock.machine.item_prices.get(product=entry.product)
                    net_change = entry.restocked - entry.discarded
                    machine_stock_updates.append({
                        'machine_item': machine_item,
                        'change': -net_change  # Revert the change
                    })
                except restock.machine.item_prices.model.DoesNotExist:
                    pass
        
        # Apply inventory updates in bulk
        for product_id, change in inventory_updates.items():
            if change != 0:
                Product.objects.filter(id=product_id).update(
                    inventory_quantity=models.F('inventory_quantity') + change
                )
        
        # Apply machine stock updates in bulk
        for update in machine_stock_updates:
            MachineItemPrice.objects.filter(id=update['machine_item'].id).update(
                current_stock=models.F('current_stock') + update['change']
            )
        
        # Delete all machine restocks (will cascade to entries)
        machine_restocks.delete()
    
    def _process_machine_restocks_bulk(self, visit, machine_restocks_data):
        """Process all machine restocks and entries in optimized bulk operations"""
        if not machine_restocks_data:
            return
        
        # Create all VisitMachineRestock objects in bulk
        machine_restocks_to_create = []
        for restock_data in machine_restocks_data:
            if restock_data.get('restock_entries'):  # Only create if there are entries
                machine_restocks_to_create.append(VisitMachineRestock(
                    visit=visit,
                    machine_id=restock_data['machine'],
                    notes=restock_data.get('notes', '')
                ))
        
        if not machine_restocks_to_create:
            return
        
        # Bulk create machine restocks
        created_restocks = VisitMachineRestock.objects.bulk_create(machine_restocks_to_create)
        
        # Create a mapping for quick lookup
        machine_to_restock = {
            restock.machine_id: restock 
            for restock in created_restocks
        }
        
        # Prepare bulk restock entries
        restock_entries_to_create = []
        inventory_updates = {}  # product_id -> quantity_change
        machine_stock_updates = []  # List of machine stock updates
        
        for restock_data in machine_restocks_data:
            machine_id = restock_data['machine']
            restock = machine_to_restock.get(machine_id)
            
            if not restock or not restock_data.get('restock_entries'):
                continue
            
            for entry_data in restock_data['restock_entries']:
                product_id = entry_data['product']
                stock_before = entry_data['stock_before']
                discarded = entry_data['discarded']
                restocked = entry_data['restocked']
                
                # Create restock entry object
                restock_entries_to_create.append(RestockEntry(
                    visit_machine_restock=restock,
                    product_id=product_id,
                    stock_before=stock_before,
                    discarded=discarded,
                    restocked=restocked
                ))
                
                # Collect inventory updates (reduce by restocked amount)
                if product_id not in inventory_updates:
                    inventory_updates[product_id] = 0
                inventory_updates[product_id] -= restocked
                
                # Collect machine stock updates
                machine_stock_updates.append({
                    'machine_id': machine_id,
                    'product_id': product_id,
                    'stock_before': stock_before,
                    'discarded': discarded,
                    'restocked': restocked
                })
        
        # Bulk create restock entries
        if restock_entries_to_create:
            RestockEntry.objects.bulk_create(restock_entries_to_create)
        
        # Apply inventory updates in bulk using F expressions for atomic updates
        for product_id, change in inventory_updates.items():
            if change != 0:
                Product.objects.filter(id=product_id).update(
                    inventory_quantity=models.F('inventory_quantity') + change
                )
        
        # Apply machine stock updates in bulk
        self._update_machine_stocks_bulk(machine_stock_updates)
    
    def _update_machine_stocks_bulk(self, machine_stock_updates):
        """Update machine item stocks in bulk using efficient queries"""
        if not machine_stock_updates:
            return
        
        # Group updates by machine for efficient querying
        machine_updates = {}
        for update in machine_stock_updates:
            machine_id = update['machine_id']
            if machine_id not in machine_updates:
                machine_updates[machine_id] = []
            machine_updates[machine_id].append(update)
        
        # Process each machine's updates
        for machine_id, updates in machine_updates.items():
            # Get all relevant machine items in one query
            product_ids = [update['product_id'] for update in updates]
            machine_items = MachineItemPrice.objects.filter(
                machine_id=machine_id,
                product_id__in=product_ids
            ).select_for_update()
            
            # Create lookup for efficient updates
            machine_item_lookup = {item.product_id: item for item in machine_items}
            
            # Apply updates
            items_to_update = []
            for update in updates:
                product_id = update['product_id']
                machine_item = machine_item_lookup.get(product_id)
                
                if machine_item:
                    # Calculate new stock: stock_before - discarded + restocked
                    new_stock = update['stock_before'] - update['discarded'] + update['restocked']
                    machine_item.current_stock = new_stock
                    items_to_update.append(machine_item)
            
            # Bulk update machine items
            if items_to_update:
                MachineItemPrice.objects.bulk_update(
                    items_to_update, 
                    ['current_stock', 'updated_at']
                )
