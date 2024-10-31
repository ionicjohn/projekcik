# project1/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from aplikacja1.views import PersonListView, PersonDetailView
from aplikacja1.handlers import handler404, handler500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/people/', PersonListView.as_view(), name='person-list'),
    path('api/people/<int:id>/', PersonDetailView.as_view(), name='person-detail'),
]


handler404 = 'aplikacja1.handlers.handler404'
handler500 = 'aplikacja1.handlers.handler500'

if settings.DEBUG:
    from django.conf.urls import handler404 as h404, handler500 as h500
    
    urlpatterns += [
        path('404/', handler404, {'exception': Exception()}),
        path('500/', handler500),
    ]