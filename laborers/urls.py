
from django.contrib import admin
from django.urls import path,include
from payease import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('payease.urls')),
]