from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.user_login,name="login"),
    path('logout/', views.user_logout, name="logout"),
    path('register/',views.registration_page,name="register"),
    path('verify/',views.otp_verification,name="verify"),
    path('',views.user_page,name="userpage")
]