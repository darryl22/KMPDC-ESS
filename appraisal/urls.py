from django.urls import path
from . import views

urlpatterns = [
    path('appraisal',views.AppraisalRequests.as_view(),name='AppraisalRequests'),
    path('appraisal/<str:pk>',views.HODDetails.as_view(),name='HODDetails'),
    path('appraisal/attachment/<str:pk>',views.UploadTargetAttachment,name='UploadTargetAttachment'),
]