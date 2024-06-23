from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Ikea

class IkeaResource(resources.ModelResource):
 class Meta:
  model = Ikea

@admin.register(Ikea)
class IkeaAdmin(ImportExportModelAdmin):
 ordering = ['id']
 list_display = ('item_id','name','category','price',
                 'old_price','sellable_online','link',
                 'other_colors','short_description','designer',
                 'depth','height','width')
 
 resource_class = IkeaResource