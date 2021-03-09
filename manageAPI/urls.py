from django.urls import path
from . import views

urlpatterns = [
    path("login", views.login.as_view()),
    path("logout", views.logout.as_view()),
    path("checkLogin", views.checkLogin.as_view()),
    path("User", views.User.as_view()),
    path("changePassword",views.changePassword.as_view()),
    path("timeSlot",views.timeSlop.as_view()),
    path("AP", views.AP.as_view()),
    path("myHandle", views.myHandle.as_view()),
    path("handleDetail", views.handleDetail.as_view())
]
