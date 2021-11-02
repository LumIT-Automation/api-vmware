from django.urls import path, include

from .controllers import Root


urlpatterns = [
    path('api/', Root.RootController.as_view()),
    path('api/v1/', Root.RootController.as_view()),

    path('api/v1/vmware/', include('vmware.VMwareUrls')),
]
