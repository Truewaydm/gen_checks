import json
import logging
from base64 import b64encode

import requests
from celery import shared_task
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string

from checks.models import Check, MerchantPoint

log = logging.getLogger(__name__)


@shared_task(bind=True)
def create_checks(self, order_uuid):
    """Task for check creation"""
    checks = Check.objects.filter(order__uuid=order_uuid)
    if not checks:
        raise ObjectDoesNotExist(f'Checks by {order_uuid} not found')
    merchant_point = MerchantPoint.objects.get(
        pk=checks[0].order['merchant_point'])
    for check in checks:
        html = render_to_string(
            template_name='check.html',
            context={'check': check, 'address': merchant_point.address}
        )
        file_name = f"{check.pk}_{check.order['uuid']}_{check.check_type}.pdf"
        try:
            convert_html_to_pdf(html=html, file_name=file_name)
            check.status = 'rendered'
            check.pdf_file = file_name
            check.save()
        except requests.RequestException as err:
            log.error(err)
            raise self.retry(exc=err)


def convert_html_to_pdf(html, file_name):
    """Convert HTML to PDF with wkhtmltopdf"""
    enc = 'utf-8'
    data = b64encode(bytearray(html, encoding=enc)).decode(enc)
    resp = requests.post(
        url=settings.WKHTMLTOPDF_URL,
        data=json.dumps({'contents': data}),
        headers={'Content-Type': 'application/json'}
    )
    resp.raise_for_status()
    with open(settings.MEDIA_ROOT / file_name, 'wb') as f:
        f.write(resp.content)
