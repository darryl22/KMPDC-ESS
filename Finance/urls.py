from django.urls import path
from . import views


urlpatterns = [
    path('ImprestRequisition', views.ImprestRequisition, name='imprestReq'),
    path('CreateImp', views.CreateImprest, name='create'),
    path('Imp/<str:pk>', views.ImprestDetails, name='IMPDetails'),
    path('ImprestSurrender', views.ImprestSurrender, name='imprestSurr'),
    path('StaffClaim', views.StaffClaim, name='claim'),
    path("NewClaim", views.CreateClaim, name="NewClaim"),
    path('raise/<str:pk>', views.SurrenderDetails, name='raise'),
]
