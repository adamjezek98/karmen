from django.contrib import admin
from django.db.models import Count
from printers.models import Printer, PrinterInGroup

class PrinterInline(admin.TabularInline):
    model = PrinterInGroup
    extra = 0

class PrinterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_on', 'last_updated_on')

admin.site.register(Printer, PrinterAdmin)
