from django.urls import path
from . import views

urlpatterns = [
    path('appraisal',views.AppraisalRequests.as_view(),name='AppraisalRequests'),
    path('appraisal/<str:pk>',views.HODDetails.as_view(),name='HODDetails'),
    path('appraisals/<str:pk>',views.UserInitiate.as_view(),name='UserInitiate'),
    path('appraisal/attachment/<str:pk>',views.UploadTargetAttachment,name='UploadTargetAttachment'),
    path('FnInitiateAppraisal/<str:pk>',views.FnInitiateAppraisal.as_view(),name='FnInitiateAppraisal'),
    path('FnAppraisalScores',views.FnAppraisalScores,name='FnAppraisalScores'),
    path('HODInitiate',views.HODInitiate.as_view(),name='HODInitiate'),
    path('EmployeeAppraisalAttachment/<str:pk>',views.EmployeeAppraisalAttachment,name='EmployeeAppraisalAttachment'),
    path('FnsendforReview/<str:pk>',views.FnsendforReview,name='FnsendforReview'),
    path('FnSendforFurtherReview/<str:pk>',views.FnSendforFurtherReview,name='FnSendforFurtherReview'),    
]