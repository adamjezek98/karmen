from django.core.mail import send_mail
from karmen.serializers import KarmenModelSerializer
from users.models import User
from django.conf import settings
from rest_framework import serializers, exceptions, status
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.response import Response
from tokens.token import EmailVerificationToken


class InvitationRequestSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True, label='Your e-mail')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise exceptions.ValidationError('The user is already registered.')
        return value

    def create(self, validated_data):
        email = validated_data['email']
        token = EmailVerificationToken.for_email(email)
        activation_url = settings.FRONTEND_ACTIVATION_URL % token
        send_mail(
            subject='Karmen new account activation',
            message=f'Than you for registering to Karmen, please click on this link: {activation_url}',
            from_email=settings.EMAIL_FROM,
            recipient_list=(email,),
        )
        return token


class ActivationRequestSerializer(serializers.Serializer):

    token = serializers.CharField(label='Token')
    password = serializers.CharField()

    def validate_token(self, value):
        token = EmailVerificationToken(token=value)
        try:
            token.verify()
        except TokenError:
            raise InvalidToken({'details': 'The token is not valid.'})
        return token

    def validate(self, attrs):

        attrs['email'] = attrs['token']['sub']

        if User.objects.filter(email=attrs['email']).exists():
            raise exceptions.ValidationError(f'Email {attrs["email"]} is already registered.')

        return attrs

    def create(self, validated_data):
        email = validated_data['email']

        new_user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data['password'],
        )
        new_user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(label='old password for validation', required=True)
    password = serializers.CharField(label='password to change to', required=True)

    def validate_old_password(self, old_password):
        if not self.instance.check_password(old_password):
            raise exceptions.ValidationError('Invalid password.')

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class UserSerializer(KarmenModelSerializer):

    restricted_fields = set(('id', 'username', 'last_login', 'first_name', 'last_name', 'email')) 
    

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id', 'last_login', 'date_joined', 'groups', 'user_permissions']
        extra_kwargs = {'password': {'write_only': True}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_user = kwargs['context']['request'].user
        if not current_user.has_perm('change_user'):
            all_fields = set(self.fields.keys())
            for field_name in (all_fields - self.restricted_fields):
                self.fields.pop(field_name)
            self.fields['username'].read_only = True

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        for field_name, field in self.fields.items():
            if field_name in validated_data and not field.read_only:
                setattr(instance, field_name, validated_data[field_name])
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance
