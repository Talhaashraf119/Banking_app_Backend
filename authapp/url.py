from django.urls import path
from .views import *
urlpatterns = [
    path('login/',login_user),
    path('register/',register_user),
    path('resetpass/',otp_send),
    path('verifyotp/',verify_otp),
    path('changepass/',change_pass),
]