import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models.deletion import ProtectedError
from django.http import Http404, FileResponse
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from checks import models, serializers
from checks.tasks import create_checks

log = logging.getLogger(__name__)


class CustomModelViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    """Custom ModelViewSet"""

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ProtectedError as err:
            log.error(err)
            data = {
                'detail': 'Cannot delete object as it is being used',
                'protected_objects': [
                    {'id': obj.pk, 'name': str(obj)} for obj in err.protected_objects
                ]
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        instance.delete()


class MerchantPointViewSet(CustomModelViewSet):
    """
    Views set for MerchantPoint
    list: Returns merchant point list
    create: Create merchant point
    retrieve: Returns merchant point
    partial_update: Update merchant point
    delete: Delete merchant point
    """
    queryset = models.MerchantPoint.objects.order_by('pk')
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.MerchantPointListSerializer
        return serializers.MerchantPointItemSerializer


class PrinterViewSet(CustomModelViewSet):
    """
    Views set for Printer
    list: Returns printer list
    create: Create printer
    retrieve: Returns printer
    partial_update: Update printer
    delete: Delete printer
    """
    queryset = models.Printer.objects.order_by('pk')
    http_method_names = ['get', 'post', 'patch', 'delete']
    filterset_fields = ['check_type', 'merchant_point']

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PrinterListSerializer
        return serializers.PrinterItemSerializer


class CheckViewSet(CustomModelViewSet):
    """
    Views set for Check
    list: Returns check list
    create: Create check
    retrieve: Returns check
    partial_update: Update check
    delete: Delete check
    get_for_print: Returns rendered check by printer api key
    """
    queryset = models.Check.objects.order_by('pk')
    http_method_names = ['get', 'post', 'patch', 'delete']
    filterset_fields = ['printer', 'check_type', 'status']

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.CheckListSerializer
        if self.action == 'partial_update':
            return serializers.CheckUpdateItemSerializer
        return serializers.CheckItemSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        create_checks.delay(serializer.data['order']['uuid'])
        return Response(
            data=serializer.data['order'],
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(
        methods=['get'],
        detail=False,
        url_path=r'for-print/(?P<api_key>[\w-]+)',
        url_name='for-print'
    )
    def get_for_print(self, request, api_key):
        try:
            printer = models.Printer.objects.get(api_key=api_key)
        except (ObjectDoesNotExist, ValidationError) as err:
            log.error(err)
            raise NotFound
        queryset = models.Check.objects.filter(
            printer_id=printer.pk, status='rendered'
        ).order_by('pk')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


def download(request, path):
    file_path = settings.MEDIA_ROOT / path

    if not file_path.exists():
        log.info(f'File {file_path} not found')
        raise Http404

    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = f'inline; filename={file_path.name}'
    return response
