from django.shortcuts import render, redirect
import requests
import json
from django.conf import settings as config
import datetime
from django.contrib import messages
from django.views import View
from myRequest.views import UserObjectMixins
# Create your views here.

class Dashboard(UserObjectMixins,View):

    def get(self,request):
        userId =  request.session['User_ID']
        empNo = request.session['Employee_No_']
        try:
            
            Leave = self.one_filter("/QyLeaveApplications","User_ID","eq",userId)
            open_leave_list = len([x for x in Leave[1] if x['Status'] == 'Open'])
            app_leave_list = len([x for x in Leave[1]  if x['Status'] == 'Released'])
            pendLeave = len([x for x in Leave[1]  if x['Status'] == 'Pending Approval'])

            Training = self.one_filter("/QyTrainingRequests","Employee_No","eq",empNo)
            open_train_list = len([x for x in Training[1]  if x['Status'] == 'Open'])
            app_train_list = len([x for x in Training[1]  if x['Status'] == 'Released'])
            pendTrain = len([x for x in Training[1]  if x['Status'] == 'Pending Approval'])

            myImprest = self.one_filter("/Imprests","User_Id","eq",userId)
            open_imp_list = len([x for x in myImprest[1] if x['Status'] == 'Open'])
            app_imp_list = len([x for x in myImprest[1] if x['Status'] == 'Released'])
            pendImp = len([x for x in myImprest[1] if x['Status'] == 'Pending Approval'])

            Surrender = self.one_filter("/QyImprestSurrenders","User_Id","eq",userId)
            open_surrender_list = len([x for x in Surrender[1]  if x['Status'] == 'Open'])
            app_surrender_list = len([x for x in Surrender[1]  if x['Status'] == 'Released'])
            pendSurrender = len([x for x in Surrender[1]  if x['Status'] == 'Pending Approval'])

            Claim = self.one_filter("/QyStaffClaims","User_Id","eq",userId)
            open_claim_list = len([x for x in Claim[1]  if x['Status'] == 'Open'])
            app_claim_list = len([x for x in Claim[1]  if x['Status'] == 'Released'])
            pendClaim = len([x for x in Claim[1]  if x['Status'] == 'Pending Approval'])

            Purchase = self.one_filter("/QyPurchaseRequisitionHeaders","Employee_No_","eq",empNo)
            open_purchase_list = len([x for x in Purchase[1]  if x['Status'] == 'Open'])
            app_purchase_list = len([x for x in Purchase[1]  if x['Status'] == 'Released'])
            pendPurchase = len([x for x in Purchase[1]  if x['Status'] == 'Pending Approval'])

            Repair = self.one_filter("/QyRepairRequisitionHeaders","Requested_By","eq",userId)
            open_repair_list = len([x for x in Repair[1] if x['Status'] == 'Open'])
            app_repair_list = len([x for x in Repair[1] if x['Status'] == 'Released'])
            pendRepair = len([x for x in Repair[1] if x['Status'] == 'Pending Approval'])

            Store = self.one_filter("/QyStoreRequisitionHeaders","Requested_By","eq",userId)
            open_store_list = len([x for x in Store[1] if x['Status'] == 'Open'])
            app_store_list = len([x for x in Store[1] if x['Status'] == 'Released'])
            pendStore = len([x for x in Store[1] if x['Status'] == 'Pending Approval'])
        except requests.exceptions.Timeout:
            messages.error(request, "API timeout. Server didn't respond, contact admin")
            return redirect('auth')
        except requests.exceptions.ConnectionError:
            messages.error(request, "Connection/network error,retry")
            return redirect('auth') 
        except requests.exceptions.TooManyRedirects:
            messages.error(request, "Server busy, retry")
            return redirect('auth') 
        except KeyError as e:
            print (e)
            messages.success(request, "Session Expired. Please Login")
            return redirect('auth')
        ctx = {"today": self.todays_date,
                "res": open, "full": userId,
                "imprest_open": open_imp_list,"pendImp":pendImp, "imprest_app": app_imp_list,
                "open_train": open_train_list,"pendTrain":pendTrain,"app_train": app_train_list,
                "open_store": open_store_list,"app_store": app_store_list, "pendStore": pendStore,
                 "leave_open": open_leave_list,"pendLeave":pendLeave, "leave_app": app_leave_list,
                "open_repair": open_repair_list, "app_repair": app_repair_list,"pendRepair": pendRepair,
                "surrender_open": open_surrender_list,"pendSurrender": pendSurrender, "surrender_app": app_surrender_list,
                "open_claim": open_claim_list, "app_claim": app_claim_list,"pendClaim": pendClaim,
                 "open_purchase": open_purchase_list,"app_purchase": app_purchase_list, "pendPurchase": pendPurchase,
                }
        return render(request, 'main/dashboard.html', ctx)

class Manual(View):
    def get(self, request):
        try:
            userId =  request.session['User_ID']
            todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
        except KeyError as e:
            print (e)
            messages.success(request, "Session Expired. Please Login")
            return redirect('auth')
        ctx = {"today": todays_date,"full": userId,}
        return render(request,"manual.html",ctx)

