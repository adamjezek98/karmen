from django.urls import reverse
from rest_framework import serializers, exceptions
from django.shortcuts import get_object_or_404
from karmen import ROLE_ADMIN
from karmen.serializers import RelatedModelField, IdField, KarmenHyperlinkedModelSerializer, KarmenModelSerializer
from printers.serializers import PrinterInGroupSerializer
from users.models import User
from groups import models


class GroupFieldSerializer(KarmenHyperlinkedModelSerializer):
    
    class Meta:
        fields = ['id', 'url', 'name']
        model = models.Group
        extra_kwargs = {
            'name': {'read_only': True},
        }

class GroupField(RelatedModelField):

    serializer = GroupFieldSerializer


class UserInGroupSerializer(KarmenModelSerializer):
    url = serializers.SerializerMethodField()
    userUrl = serializers.HyperlinkedRelatedField(view_name='user-detail', source='user', lookup_field='pk', read_only=True)
    #url = serializers.HyperlinkedRelatedField(view_name='user-detail', source='user', lookup_field='pk', read_only=True)
    userId = IdField(source='user.id')
    username = serializers.CharField(source='user.username')

    class Meta:
        model = models.UserInGroup
        fields = ['userId', 'username', 'url', 'userUrl', 'role']

    def get_url(self, value):
        url = reverse('group-user-detail', kwargs={
            'username': value.user.username,
            'group_id': value.group.id,
        })
        return self.context['request'].build_absolute_uri(url)

    def validate(self, attrs):
        attrs['group'] = self.context['parent_instance']
        if 'user' in attrs:
            try:
                attrs['user'] = User.objects.get(username=attrs['user']['username'])
            except User.DoesNotExist:
                raise exceptions.ValidationError({'user': 'Username does not exist.'})
        return attrs

    def create(self, validated_data):
        return models.UserInGroup.objects.create(**validated_data)


class GroupSerializer(KarmenHyperlinkedModelSerializer):
    url = serializers.HyperlinkedRelatedField(view_name='group-detail', source='pk', read_only=True)
    users = UserInGroupSerializer(many=True, read_only=True, source='useringroup_set')
    printers = PrinterInGroupSerializer(read_only=True, many=True, source='printeringroup_set')

    class Meta:
        fields = ['id', 'name', 'url', 'users', 'printers']
        optional_fields = ['users', 'printers']
        model = models.Group
        extra_kwargs = {
            'id': {'read_only': True},
        }

    def create(self, validated_data):
        group = super().create(validated_data)
        group.set_user(self.context['request'].user, ROLE_ADMIN)
        return group
