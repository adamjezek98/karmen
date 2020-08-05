from django.shortcuts import render
from django.core import mail
from rest_framework import viewsets, serializers, decorators
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter


class DebuggingViewSet(viewsets.ViewSet):
    '''
    Debugging and testing endpoints
    '''

    @decorators.action(detail=False, methods=['get'])
    def mails(self, request):
        '''API endpoint for listing and reading messages under locmem email backend.'''
        response = []
        if hasattr(mail, 'outbox'):
            response = list([
                {
                    'sub': m.subject,
                    'to': m.to,
                    'message': m.body
                }
                for m in mail.outbox
            ])

        return Response(response)
