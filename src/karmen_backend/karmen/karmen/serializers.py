from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework import serializers

class IdField(serializers.CharField):

    help_text = 'Unique identity of the object.'
    default_kwargs = {
        'max_length': settings.ID_FIELD_LENGTH,
        'min_length': settings.ID_FIELD_LENGTH,
        'read_only': True,
        'label': 'ID',
    }

    def __init__(self, *args, **kwargs):
        # setup default kwargs
        for key, val in self.default_kwargs.items():
            kwargs[key] = kwargs.get(key, val)
        super().__init__(*args, **kwargs)


class RelatedModelField(serializers.CharField):
    '''
    Usage:

        class ChildSerializer(serializers.ModelsSerializer):
            class Meta:
                model = Child
                fileds = '__all__'

        class ParentSerializer(serializers.ModelsSerializer):
            child = RelatedModelField(serializer=ChildSerializer)

            class Meta:
                model = Parent
                fields = '__all__'

    Asymetric field which acts as nested serializer (see
    https://www.django-rest-framework.org/api-guide/relations/#nested-relationships) when representing data. 

    To craate / update this field, only pk needs to be sent.
    '''

    def __init__(self, **kwargs):
        if 'serializer' in kwargs:
            self.serializer = kwargs.pop('serializer')
        if self.serializer is None:
            raise ImproperlyConfigured('RelatedModelField requires serializer as kwarg.')
        super().__init__(**kwargs)

    def use_pk_only_optimization(self):
        return False

    def to_internal_value(self, data):
        model = self.serializer.Meta.model
        if self.serializer:
            try:
                return model.objects.get(pk=data)
            except model.DoesNotExist:
                raise exceptions.ValidationError(f'{model.__name__} \'{data}\' does not exist.')
        else:
            return super().to_internal_value(data)

    def to_representation(self, instance):
        return self.serializer(instance, context=self.context).data

class OptionalFieldsSerializerMixin:
    '''
    Adds dynamic field removal based on request query param `fields` and view type.
    Add `request` to serializer context for this mixin to work (this is the
    default for ModelViewSets).

    Usage:

    class MySerializer(OptionalFieldsSerializerMixin, serializers.Serializer):

        class Meta:
            fields = ['first_name', 'surname', 'birthdate', 'friends']
            # optional fields for list view (action == 'list')
            optional_fields = ['surname', 'birthdate', 'friends', ]
            # optional fields for detail view (action == 'retrieve')
            optional_fields_retrieve =  ['friends', ]


    Fetching listing (e.g. `http://.../my-serializer-view`) will not show `surname`,
    `birthdate` nor friends by default.
    Fetching detail (retrieve action) (e.g. `http://.../my-serializer-view/123`) will show all fields but `friends`.

    To include optional fields, add `fields` qeury parameter with comma separated list of optional fields to include
    `http://.../my-serializer-view?fields=surname,birthdate

    To include all optional fields use `?fields=all`.

    To hide default field `name` on the other hand append the name of the field
    to `fields` param with preceeding `-`: For example
    `http://.../my-serializer-view?fields=-name` (notice the `-` sign before `name`)

    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'request' in self.context:
            request = self.context['request']
            action = self.context['view'].action if 'view' in self.context else ''
            fields_param = request.query_params.get('fields', '')
            if fields_param == 'all':
                pass # do not remove any optional fields
            else:
                fields_list = fields_param.split(',')

                optional_fields_to_show = set(field for field in fields_list if not field.startswith('-'))
                optional_fields = None
                # try to get optional fields for current action
                if hasattr(self.Meta, 'optional_fields_%s' % action):
                    optional_fields = getattr(self.Meta, 'optional_fields_%s' % action)
                # if the action is 'list' use optional_fields
                elif hasattr(self.Meta, 'optional_fields') and action == 'list':
                    optional_fields = getattr(self.Meta, 'optional_fields')

                # remove optional fields which are not specified in query `?fields=<field1>,<field2>`
                if optional_fields:
                    optional_fields = set(optional_fields)
                    for field in optional_fields - optional_fields_to_show:
                        field = field.lstrip('+')
                        if field in self.fields:
                            del self.fields[field]

                # remove fields which was added to `fields` query param with `-` sign
                fields_to_exclude = set(field for field in fields_list if field.startswith('-'))
                for field in fields_to_exclude:
                    field = field[1:]
                    if field in self.fields:
                        del self.fields[field]

class KarmenModelSerializer(OptionalFieldsSerializerMixin, serializers.ModelSerializer):
    '''Shortcut composition of OptionalFieldsSerializerMixin and ModelsSerializer'''
    pass


class KarmenHyperlinkedModelSerializer(OptionalFieldsSerializerMixin, serializers.HyperlinkedModelSerializer):
    '''Shortcut composition of OptionalFieldsSerializerMixin and HyperlinkedModelSerializer'''
    pass
