from django.contrib import admin
from groups.models import Group
from printers.admin import PrinterInline

class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    inlines = [PrinterInline]

admin.site.register(Group, GroupAdmin)
