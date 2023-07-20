from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import SimpleRouter
from rest_framework.schemas import get_schema_view

from checks import views
from checks.views import download

router = SimpleRouter()
router.register(r'merchant-points', views.MerchantPointViewSet)
router.register(r'printers', views.PrinterViewSet)
router.register(r'checks', views.CheckViewSet)

urlpatterns = [
    path('media/<path:path>/', download, name='media'),
    path('openapi/', get_schema_view(
        title='Checks API',
        description='API microservice for generating checks by orders',
        public=True,
        version='v1'
    ), name='openapi-schema'),
    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger_ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger'),
    path('redoc/', TemplateView.as_view(
        template_name='redoc.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='redoc'),
    path('', include(router.urls))
]
