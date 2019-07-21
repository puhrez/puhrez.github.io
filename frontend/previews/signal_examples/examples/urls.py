from django.urls import path
from . import views

app_name = 'examples'


urlpatterns = (
    path('view', views.ViewLogicExample.as_view(),
         name='view-based-example'),
    path('serializer', views.SerializerLogicExample.as_view(),
         name='serializer-based-example'),
    path('serializer-from-manager',
         views.SerializerFromManagerExample.as_view(),
         name='serializer-from-manager-based-example'),
    path('publish', views.PublishBook.as_view(), name='publish-book')
)
