from urllib.parse import urlparse, parse_qsl
from django.urls import reverse
from rest_framework import serializers, exceptions
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from karmen import ROLE_ADMIN
from karmen.serializers import RelatedModelField, IdField, KarmenHyperlinkedModelSerializer, KarmenModelSerializer
from printers import models
from users.models import User
from printers.octoprint import OctoprintClient, DeviceError, PrinterNotOperationalError


class UserOnPrinterSerializer(KarmenHyperlinkedModelSerializer):

    url = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username')

    class Meta:
        model = models.UserOnPrinter
        fields = ['username', 'url', 'role']

    def get_url(self, user_on_printer):
        url = reverse('printer-user-detail', kwargs={
            'username': user_on_printer.user.username,
            'printer_id': user_on_printer.printer.pk
        })
        return self.context['request'].build_absolute_uri(url)


    def validate(self, attrs):
        attrs['printer'] = self.context['parent_instance']
        if 'user' in attrs:
            attrs['user'] = get_object_or_404(User, username=attrs['user']['username'])
        return attrs

    def create(self, validated_data):
        return self.context['parent_instance'].set_user(validated_data['user'], validated_data['role'])


class GroupsOnPrinterSerializer(KarmenModelSerializer):

    url = serializers.SerializerMethodField(source='get_url')
    groupUrl = serializers.HyperlinkedRelatedField(view_name='group-detail', source='group', read_only=True)
    groupId = IdField(source='group.id')
    groupName = serializers.CharField(source='group.name')

    class Meta:
        model = models.PrinterInGroup
        fields = ['url', 'groupUrl', 'groupName', 'groupId']

    def get_url(self, value):
        url = reverse('group-printer-detail', kwargs={
            'group_id': value.group.id,
            'printer_id': value.printer.id,
        })
        return self.context['request'].build_absolute_uri(url)


    def validate(self, attrs):
        if 'printer' not in attrs:
            if self.context['parent_instance']:
                attrs['printer'] = self.context['parent_instance']
            else:
                raise exceptions.ValidationError({'code': 'missing-printer', 'detail': 'Missing printer info'})
        if 'group' in attrs:
            attrs['group'] = get_object_or_404(models.Group, pk=attrs['group'])

        return attrs

    def create(self, validated_data):
        return self.context['parent_instance'].set_group(validated_data['group'], validated_data['role'])


class PrinterInGroupSerializer(KarmenModelSerializer):

    printerId = serializers.CharField(source='printer.id')
    printerName = serializers.CharField(source='printer.name', read_only=True)
    printerUrl = serializers.HyperlinkedRelatedField(view_name='printer-detail', source='printer.id', read_only=True)
    url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ['url', 'printerId', 'printerUrl', 'printerName']
        model = models.PrinterInGroup
        extra_kwargs={
            'name': {'read_only': True},
        }

    def get_url(self, value):
        printer_id = value.printer_id
        url = reverse('group-printer-detail', kwargs={
            'group_id': value.group.id,
            'printer_id': value.printer.id,
        })
        return self.context['request'].build_absolute_uri(url)

    def validate_printerId(self, value):
        try:
            printer = models.Printer.objects.get(pk=value)
        except models.Printer.DoesNotExist:
            raise exceptions.ValidationError(f"Printer '{value}' does not exist.")
        if not printer.can_modify(self.context['request'].user):
            raise exceptions.ValidationError(f"Printer '{value}' is not accessible.")
        return printer

    def create(self, validated_data):
        parent = self.context['request'].parent_instance
        printer_id = validated_data['printer']['id']
        parent.printers.add(printer_id)
        return self.Meta.model.objects.get(group=parent, printer_id=printer_id)



class OctoprintSerializer(serializers.BaseSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_api(self, connection_string):
        # FIXME: this is development verison, the printer will be connected
        # through websocket proxy server in real application
        parts = urlparse(connection_string)
        api_key = dict(parse_qsl(parts.query)).get('apikey')
        return OctoprintClient(api_uri=connection_string, api_key=api_key)

    def to_representation(self, value):
        if value.startswith('http'):
            try:
                api = self.get_api(value)
                response = {
                    'version': api.get_version(),
                    'files': api.list_files(),
                }
                try:
                    response['printer'] = api.get_printer()
                except PrinterNotOperationalError as e:
                    response['printer'] = None
            except DeviceError as e:
                return {
                    'error': str(e),
                }
        else:
            response = {
                'error': 'Missing connection information. Set api_key.'
            }
        return response


class PrinterSerializer(KarmenHyperlinkedModelSerializer):

    users = UserOnPrinterSerializer(many=True, source='useronprinter_set', read_only=True)
    groups = GroupsOnPrinterSerializer(many=True, read_only=True, source='printeringroup_set')
    octoprint =  OctoprintSerializer(read_only=True, source='api_key')

    class Meta:
        model = models.Printer
        fields = ['id', 'name', 'url', 'api_key', 'users', 'groups', 'octoprint', ]
        optional_fields = ['api_key', 'octoprint', 'users', 'groups', ]
        optional_fields_retrieve = ['octoprint', ]
        read_only_fields = ['id']

    def create(self, validated_data):
        printer = models.Printer.objects.create(**validated_data)
        printer.set_user(self.context['request'].user, ROLE_ADMIN)
        return printer
