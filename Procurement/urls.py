from django.urls import path
from . import views

urlpatterns = [
    path('PurchaseRequisition', views.PurchaseRequisition, name='purchase'),
    path('CreatePurchaseRequisition', views.CreatePurchaseRequisition,
         name='CreatePurchaseRequisition'),
    path('PurchaseDetail/<str:pk>',
         views.PurchaseRequestDetails, name='PurchaseDetail'),
    path('PurchaseApprove/<str:pk>',
         views.PurchaseApproval, name='PurchaseApprove'),
    path('PurchaseCancel/<str:pk>',
         views.FnCancelPurchaseApproval, name='PurchaseCancel'),
    path('PurchaseLines/<str:pk>',
         views.CreatePurchaseLines, name='PurchaseLines'),
    path('FnDeletePurchaseRequisitionHeader', views.FnDeletePurchaseRequisitionHeader,
         name='FnDeletePurchaseRequisitionHeader'),
    path('FnDeletePurchaseRequisitionLine/<str:pk>',
         views.FnDeletePurchaseRequisitionLine, name='FnDeletePurchaseRequisitionLine'),
    path('FnGeneratePurchaseReport/<str:pk>',
         views.FnGeneratePurchaseReport, name='FnGeneratePurchaseReport'),
    path('UploadPurchaseAttachment/<str:pk>',
         views.UploadPurchaseAttachment, name='UploadPurchaseAttachment'),

    path('RepairRequest', views.RepairRequest, name='repair'),
    path('CreateRepairRequest', views.CreateRepairRequest,
         name='CreateRepairRequest'),
    path('RepairDetail/<str:pk>',
         views.RepairRequestDetails, name='RepairDetail'),
    path('RepairApprove/<str:pk>',
         views.RepairApproval, name='RepairApprove'),
    path('RepairLines/<str:pk>',
         views.CreateRepairLines, name='RepairLines'),
    path('RepairCancel/<str:pk>',
         views.FnCancelRepairApproval, name='RepairCancel'),
    path('FnDeleteRepairRequisitionHeader', views.FnDeleteRepairRequisitionHeader,
         name='FnDeleteRepairRequisitionHeader'),
    path('FnDeleteRepair/<str:pk>',
         views.FnDeleteRepairRequisitionLine, name='FnDeleteRepairRequisitionLine'),
    path('FnGenerateRepairReport/<str:pk>',
         views.FnGenerateRepairReport, name='FnGenerateRepairReport'),
    path('UploadRepairAttachment/<str:pk>',
         views.UploadRepairAttachment, name='UploadRepairAttachment'),



    path('StoreRequest', views.StoreRequest, name='store'),
    path('CreateStoreRequest', views.CreateStoreRequisition,
         name='CreateStoreRequest'),
    path('StoreDetail/<str:pk>',
         views.StoreRequestDetails, name='StoreDetail'),
    path('StoreApprove/<str:pk>',
         views.StoreApproval, name='StoreApprove'),
    path('StoreCancel/<str:pk>',
         views.FnCancelStoreApproval, name='StoreCancel'),
    path('CreateStoreLine/<str:pk>',
         views.CreateStoreLines, name='CreateStoreLine'),
    path('FnDeleteStoreRequisition', views.FnDeleteStoreRequisitionHeader,
         name='FnDeleteStoreRequisitionHeader'),
    path('FnDeleteStore/<str:pk>',
         views.FnDeleteStoreRequisitionLine, name='FnDeleteStoreRequisitionLine'),
    path('FnGenerateStoreReport/<str:pk>',
         views.FnGenerateStoreReport, name='FnGenerateStoreReport'),
    path('UploadStoreAttachment/<str:pk>',
         views.UploadStoreAttachment, name='UploadStoreAttachment'),
]
