from django.shortcuts import redirect, render
from django.views import View
import requests
from django.conf import settings as config
import datetime as dt
from django.contrib import messages
import base64

# Create your views here.
class UserObjectMixin(object):
    model =None
    session = requests.Session()
    session.auth = config.AUTHS
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    def get_object(self,endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response

class AppraisalRequests(UserObjectMixin,View):
    def get(self,request):
        HOD_User = request.session['HOD_User']
        userID = request.session['User_ID']
        department = request.session['User_Responsibility_Center']
        empNo = request.session['Employee_No_']
        numberOfEmployees = '0'
        outputTarget = '0'
        outputCode = '0'

        if HOD_User == True:
            departmentUsers = config.O_DATA.format(f"/QyUserSetup?$filter=User_Responsibility_Center%20eq%20%27{department}%27")
            DPTResponse = self.get_object(departmentUsers)
            numberOfEmployees = [x for x in DPTResponse['value'] if x['User_Responsibility_Center'] == department]

            appraisalCode = config.O_DATA.format(f"/QyDepartmentalAppraisalPeriods?$filter=Department%20eq%20%27{department}%27")
            CodeResponse = self.get_object(appraisalCode)
            outputCode = [x for x in CodeResponse['value'] if x['Department'] == department]

            appraisalTargets = config.O_DATA.format(f"/QyDepartmentalAppraisalTargets?$filter=DepartmentCode%20eq%20%27{department}%27")
            targetResponse = self.get_object(appraisalTargets)
            outputTarget = [x for x in targetResponse['value'] if x['DepartmentCode'] == department]

        empAppraisalEndpoint =config.O_DATA.format(f"/QyEmployeeAppraisals?$filter=EmployeeNo%20eq%20%27{empNo}%27")
        empAppraisalResponse = self.get_object(empAppraisalEndpoint)
        empAppraisal = [x for x in empAppraisalResponse['value'] if x['DepartmentCode'] == department and x['Status']=='Self Appraisal']

        DPTCount = len(numberOfEmployees)
        targetCount = len(outputTarget)
        empAppraisalCount = len(empAppraisal)


        ctx = {
            "today": self.todays_date,
            "HOD_User":HOD_User,"department":department,
            'DPTCount':DPTCount,"full": userID,"appraisalCode":outputCode,
            "targetCount":targetCount, "outputTarget":outputTarget,
            "empAppraisalCount":empAppraisalCount,"empAppraisal":empAppraisal
            }
        return render(request,"appraisal.html",ctx)
    def post(self,request):
        if request.method == "POST":
            applicationCode = request.POST.get('applicationCode')
            departmentalAppraisalCode = request.POST.get('departmentalAppraisalCode')
            weightedScore = int(request.POST.get('weightedScore'))
            description = request.POST.get('description')
            Quarter1 = request.POST.get('Quarter1')
            Quarter2 = request.POST.get('Quarter2')
            Quarter3 = request.POST.get('Quarter3')
            Quarter4 = request.POST.get('Quarter4')
            myAction = request.POST.get('myAction')  
      
            if not Quarter1:
                Quarter1 = 'False'
            if not Quarter2:
                Quarter2 = 'False'

            if not Quarter3:
                Quarter3 = 'False'
            if not Quarter4:
                Quarter4 = 'False'
            try:
                response = config.CLIENT.service.FnDepartmentalAppraisalTarget(
                        applicationCode,departmentalAppraisalCode, description, 
                        weightedScore,eval(Quarter1),eval(Quarter2),eval(Quarter3),
                        eval(Quarter4),myAction)
                print("response:",response)
                if response:
                    messages.success(request, "Request Successful")
                    return redirect('HODDetails',pk=response)
            except Exception as e:
                messages.error(request, e)
                print(e)
        return redirect('AppraisalRequests')

class HODDetails(UserObjectMixin,View):
    def get(self,request,pk):
        try:
            userID = request.session['User_ID']
            department = request.session['User_Responsibility_Center']

            Access_Point = config.O_DATA.format(f"/QyDepartmentalAppraisalTargets?$filter=Code%20eq%20%27{pk}%27")
            response = self.get_object(Access_Point)
            for appraisal in response['value']:
                res = appraisal
            assignedEmployees = config.O_DATA.format(f"/QyAppraisalTargetEmployees?$filter=DepartmentalTarget%20eq%20%27{pk}%27")
            assignedEmployeesResponse = self.get_object(assignedEmployees)
            outputEmployees = [x for x in assignedEmployeesResponse['value'] if x['DepartmentalTarget'] == pk]
            
            empAssignedList = []
            for assigned in assignedEmployeesResponse['value']:
                empAssignedList.append(assigned['EmployeeNo'])
            
            employees = config.O_DATA.format(f"/QyUserSetup?$filter=User_Responsibility_Center%20eq%20%27{department}%27")
            employeesResponse = self.get_object(employees)
            availableEmployees = [x for x in employeesResponse['value'] if x['Employee_No_'] not in empAssignedList]

            ctx = {
                "target":res,"today": self.todays_date,
                "full":userID,"outputEmployees":outputEmployees,
                "availableEmployees":availableEmployees
                }
        except Exception as e:
            messages.error(request,e)
            return redirect('HODDetails',pk=pk)
        return render(request,"hodDetails.html",ctx)
    def post(self,request,pk):
        if request.method == "POST":
            try:
                employeeNo = request.POST.get('employeeNo')
                myAction = request.POST.get('myAction')

                try:
                    response = config.CLIENT.service.FnResponsibleEmployees(
                            pk,employeeNo,myAction)
                    print("response:",response)
                    if response == True:
                        messages.success(request, "Successfully added")
                        return redirect('HODDetails',pk=pk)
                    messages.error(request, "Error!! Not added")
                    return redirect('HODDetails',pk=pk)
                except Exception as e:
                    messages.error(request, e)
                    print(e)
                    return redirect('HODDetails',pk=pk)
            except Exception as e:
                messages.error(request, e)
                print(e)
                return redirect('HODDetails',pk=pk)
        return redirect('HODDetails',pk=pk)

def HODInitiate(request,pk):
    if request.method == "POST":
        try:
            response = config.CLIENT.service.FnInitiateAppraisal(pk)
            print("response:",response)
            print(pk)
            if response == True:
                messages.success(request, "Success")
                return redirect('HODDetails',pk=pk)
            messages.error(request, response)
            return redirect('HODDetails',pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('HODDetails',pk=pk)
    return redirect('HODDetails',pk=pk)


def UploadTargetAttachment(request, pk):
    if request.method == "POST":
        try:
            tableID = ""
            attach = request.FILES.getlist('attachment')
        except Exception as e:
            return redirect('HODDetails', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    pk, fileName, attachment, tableID,request.session['User_ID'])
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "File(s) Upload Successful")
            return redirect('HODDetails', pk=pk)
        else:
            messages.error(request, "Failed, Try Again")
            return redirect('HODDetails', pk=pk)
    return redirect('HODDetails', pk=pk)

class FnInitiateAppraisal(UserObjectMixin,View):
    def get(self,request,pk):
        try:
            department = request.session['User_Responsibility_Center']

            Access_Point = config.O_DATA.format(f"/QyEmployeeAppraisals?$filter=Code%20eq%20%27{pk}%27%20and%20DepartmentCode%20eq%20%27{department}%27")
            response = self.get_object(Access_Point)
            for appraisal in response['value']:
                res = appraisal
            ctx = {
                "appraisal":res,
            }
        except Exception as e:
            print(e)
            messages.error(request,e)
            return redirect('AppraisalRequests')
        return render(request,"appDetails.html",ctx)
        

def FnAppraisalScores(request):
    if request.method == "POST":
        try:
            depAppraisalPeriod = request.POST.get('depAppraisalPeriod')
            employeeNo = request.session['Employee_No_']
            print(employeeNo)
            target = request.POST.get('target')
            quarter = int(request.POST.get('quarter'))
            score = float(request.POST.get('score'))
            selfAppraisal = True
            myAction = request.POST.get('myAction')

            response = config.CLIENT.service.FnAppraisalScores(depAppraisalPeriod,
            employeeNo,target,quarter,score,selfAppraisal,myAction)
            print("response:",response)
            if response == True:
                messages.success(request, "Success")
                return redirect('FnInitiateAppraisal',pk=target)
            messages.error(request, response)
            return redirect('FnInitiateAppraisal',pk=target)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('FnInitiateAppraisal',pk=target)
    return redirect('AppraisalRequests')
