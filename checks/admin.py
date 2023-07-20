from django.contrib import admin

from checks import models


@admin.register(models.MerchantPoint)
class MerchantPointAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'created_at', 'updated_at'
    )
    search_fields = ('name',)


@admin.register(models.Printer)
class PrinterAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'api_key', 'created_at', 'updated_at'
    )
    list_filter = ('check_type',)
    search_fields = ('name',)


@admin.register(models.Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = (
        'pdf_file', 'created_at', 'updated_at'
    )
    list_filter = ('printer', 'check_type', 'status')
