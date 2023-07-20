import uuid

from rest_framework import serializers

from checks import models


class MerchantPointItemSerializer(serializers.ModelSerializer):
    """Serializer for item MerchantPoint"""

    class Meta:
        model = models.MerchantPoint
        fields = (
            'id',
            'name',
            'address',
            'created_at',
            'updated_at'
        )


class MerchantPointListSerializer(serializers.ModelSerializer):
    """Serializer for list MerchantPoint"""

    class Meta:
        model = models.MerchantPoint
        fields = (
            'id',
            'url',
            'name',
            'address'
        )


class PrinterItemSerializer(serializers.ModelSerializer):
    """Serializer for item Printer"""

    class Meta:
        model = models.Printer
        fields = (
            'id',
            'name',
            'api_key',
            'check_type',
            'merchant_point',
            'created_at',
            'updated_at'
        )


class PrinterListSerializer(serializers.ModelSerializer):
    """Serializer for list Printer"""

    class Meta:
        model = models.Printer
        fields = (
            'id',
            'url',
            'name',
            'check_type',
            'merchant_point'
        )


class CheckItemSerializer(serializers.ModelSerializer):
    """Serializer for item Check"""

    class Meta:
        model = models.Check
        fields = (
            'id',
            'printer',
            'check_type',
            'order',
            'status',
            'pdf_file',
            'created_at',
            'updated_at'
        )
        read_only_fields = (
            'id',
            'printer',
            'check_type',
            'status',
            'pdf_file',
            'created_at',
            'updated_at'
        )

        # Custom attribute for caching database values
        # used when checking and creating an object
        printers = None

        def validate_order(self, value):
            self.validate_items(value.get('items'))
            if not value.get('total_price'):
                raise serializers.ValidationError('The order must contain an ' + 'total_price')
            merchant_point = value.get('merchant_point')
            if not merchant_point:
                raise serializers.ValidationError('The order must contain an ' + 'merchant_point')
            self.printers = models.Printer.objects.filter(merchant_point=merchant_point)
            if not self.printers:
                raise serializers.ValidationError('No printers found for the merchant point')
            return value

        def validate_items(self, items):
            """Validate items in order"""
            if not items or not isinstance(items, list):
                raise serializers.ValidationError('The order must contain a non-empty list of ' + 'items')
            for item in items:
                is_name = item.get('name')
                is_price = item.get('price')
                is_count = item.get('count')
                if not is_name or not is_price or not is_count:
                    raise serializers.ValidationError('Each item must contain a '
                                                      + 'name', 'price', 'count')

        def create(self, validated_data):
            instance = None
            validated_data['order']['uuid'] = str(uuid.uuid4())
            for printer in self.printers:
                validated_data['printer'] = printer
                validated_data['check_type'] = printer.check_type
                instance = super().create(validated_data)
            return instance


class CheckListSerializer(serializers.ModelSerializer):
    """Serializer for list Check"""

    class Meta:
        model = models.Check
        fields = (
            'id',
            'printer',
            'check_type',
            'status',
            'pdf_file'
        )


class CheckUpdateItemSerializer(serializers.ModelSerializer):
    """Serializer for update item Check"""

    class Meta:
        model = models.Check
        fields = ('status',)
