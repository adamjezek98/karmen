from rest_framework import serializers, exceptions
from django.shortcuts import get_object_or_404
from karmen.serializers import IdField, RelatedModelField, KarmenHyperlinkedModelSerializer, KarmenModelSerializer
from users.models import User
from files import models
from groups.serializers import GroupField


class UserField(serializers.RelatedField):

    def to_representation(self, instance):
        return {
            'id': instance.pk,
            'username': instance.username,
        }


class FileSerializer(KarmenHyperlinkedModelSerializer):
    id = IdField()
    uploadedBy = UserField(source='uploaded_by', read_only=True)
    group = GroupField()

    class Meta:
        fields = ['id', 'name', 'url', 'file', 'uploadedBy', 'group' ]# 'groupId', 'groupName']
        model = models.File

    def validate(self, attrs):
        attrs['uploaded_by'] = self.context['request'].user
        return attrs


class FilesInGroupSerializer(FileSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].read_only = True

    def validate(self, attrs):
        attrs['group'] = self.context['parent_instance']
        return super().validate(attrs)
