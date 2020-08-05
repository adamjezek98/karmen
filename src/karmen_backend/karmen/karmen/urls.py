"""karmen URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework.response import Response
from users.views import InvitationsViewSet, UsersViewSet
from printers import views as printer_views
from groups import views as group_views
from files import views as file_views
from debugging_tools.views import DebuggingViewSet
from tokens.views import TokensViewSet


# rest-framework-urls (to api viewsets)
router = routers.DefaultRouter()
router.register(r'invitations', InvitationsViewSet, basename='invitation')
router.register(r'users/me/printers', printer_views.MyPrintersViewSet, basename='me-printer')
router.register(r'users/me/groups', group_views.MyGroupsViewSet, basename='me-group')
router.register(r'users/me/files', file_views.MyFilesViewSet, basename='me-file')
router.register(r'users', UsersViewSet, basename='user')
router.register(r'tokens', TokensViewSet, basename='token')
router.register(r'printers', printer_views.PrintersViewSet, basename='printer')
router.register(r'printers/(?P<printer_id>[^/]{8,12})/users', printer_views.UsersOnPrinterViewSet, basename='printer-user')
router.register(r'printers/(?P<printer_id>[^/]{8,12})/groups', printer_views.PrinterGroupsViewSet, basename='printer-group')
router.register(r'groups', group_views.GroupsViewSet, basename='group')
router.register(r'groups/(?P<group_id>[^/]{8,12})/users', group_views.UsersInGroupViewSet, basename='group-user')
router.register(r'groups/(?P<group_id>[^/]{8,12})/printers', printer_views.PrintersInGroupViewSet, basename='group-printer')
router.register(r'groups/(?P<group_id>[^/]{8,12})/files', file_views.FilesInGroupViewSet, basename='group-files')
router.register(r'files', file_views.FilesViewSet, basename='file')
router.register(r'debug', DebuggingViewSet, basename='debug')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('api/2/', include(router.urls)),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
