"""XwareSupportBackend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
import xwareBackend.views
import XwareSupportBackend.accessTokenCenter as access
from XwareSupportBackend import ownerInit
urlpatterns = [
    path('admin/', admin.site.urls),
    path("login",xwareBackend.views.login.as_view()),
    path("setpersonalInfo",xwareBackend.views.setUserInfo.as_view()),
    path("problems",xwareBackend.views.ProblemType.as_view()),
    path("timeSlotList",xwareBackend.views.TimeslotList.as_view()),
    path("Appointment",xwareBackend.views.AppointmentManager.as_view()),
    path("myAppointment",xwareBackend.views.myAppointment.as_view()),
    path("bindFunctionary",xwareBackend.views.bindFunctionary.as_view()),
    path("startEvent",xwareBackend.views.startEvent.as_view()),
    path("myHandleEvent",xwareBackend.views.myHandleEvent.as_view()),
    path("Event", xwareBackend.views.Event.as_view()),
    path("image", xwareBackend.views.image.as_view())
]
#print(access.appConfig)
ownerInit.init()