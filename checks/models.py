import uuid
from django.db import models

TYPE_OF_CHECK = [
    ('kitchen', 'Kitchen'),
    ('client', 'Client'),
]

STATUS_OF_CHECK = [
    ('new', 'New'),
    ('rendered', 'Rendered'),
    ('printed', 'Printed'),
]


class MerchantPoint(models.Model):
    """Merchant point model"""

    class Meta:
        verbose_name = 'merchant point'
        verbose_name_plural = 'merchant points'

    name = models.CharField(max_length=100, verbose_name='Name')
    address = models.CharField(max_length=250, verbose_name='Address')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creation date')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated date')

    def __str__(self) -> str:
        return self.name


class Printer(models.Model):
    """Printer model"""

    class Meta:
        verbose_name = 'printer'
        verbose_name_plural = 'printers'

    name = models.CharField(max_length=100, verbose_name='Name')
    api_key = models.CharField(default=uuid.uuid4, unique=True, verbose_name='API access key')
    check_type = models.CharField(max_length=10, choices=TYPE_OF_CHECK, verbose_name='Type of check')
    merchant_point = models.ForeignKey(to=MerchantPoint, on_delete=models.PROTECT,
                                       verbose_name='Merchant point')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creation date')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated date')

    def __str__(self) -> str:
        return self.name


class Check(models.Model):
    """Check model"""

    class Meta:
        verbose_name = 'check'
        verbose_name_plural = 'checks'

    printer = models.ForeignKey(to=Printer, on_delete=models.PROTECT, verbose_name='Printer')
    check_type = models.CharField(max_length=10, choices=TYPE_OF_CHECK, verbose_name='Type of check')
    order = models.JSONField(verbose_name='Order data')
    status = models.CharField(max_length=10, default='new', choices=STATUS_OF_CHECK,
                              verbose_name='Status of check')
    pdf_file = models.FileField(null=True, verbose_name='PDF file')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creation date')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated date')

    def __str__(self):
        return f"Check #{self.id}"
