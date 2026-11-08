from django.urls import path
from . import views

urlpatterns = [
    path('',views.form_booking, name="booking"),
    path('serialised_courts/', views.serialised_court),
    path('court/', views.selection, name="courts")
]