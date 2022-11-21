from django.shortcuts import redirect, render
from django.views import View
import requests
from django.conf import settings as config
import datetime as dt
from django.contrib import messages
import base64
from myRequest.views import UserObjectMixins

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
        try:
            HOD_User = request.session['HOD_User']
            userID = request.session['User_ID']
            department = request.session['User_Responsibility_Center']
            empNo = request.session['Employee_No_']
            numberOfEmployees = '0'
            outputTarget = '0'
            outputCode = '0'
            submittedAppraisals = '0'
            empAppraisal = ''
            submittedAppraisal = ''
            completeAppraisal = ''

            if "&" in department:
                department = department.replace("&","%26")

            empAppraisalEndpoint =config.O_DATA.format(f"/QyEmployeeAppraisals?$filter=DepartmentCode%20eq%20%27{department}%27")
            empAppraisalResponse = self.get_object(empAppraisalEndpoint)

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

                submittedAppraisals = [x for x in empAppraisalResponse['value'] if x['Status']=='Supervisor Appraisal']
            if HOD_User == False:
                empAppraisal = [x for x in empAppraisalResponse['value'] if (x['EmployeeNo'] == empNo and x['Status']=='Self Appraisal') or (x['EmployeeNo'] == empNo and x['Status']=='Open')]
                submittedAppraisal = [x for x in empAppraisalResponse['value'] if x['EmployeeNo'] == empNo and x['Status']=='Supervisor Appraisal']
                completeAppraisal = [x for x in empAppraisalResponse['value'] if x['EmployeeNo'] == empNo and x['Status']=='Completed']

            DPTCount = len(numberOfEmployees)
            targetCount = len(outputTarget)
            empAppraisalCount = len(empAppraisal)
            submittedAppraisalCount = len(submittedAppraisal)
            completeAppraisalCount = len(completeAppraisal)
            submittedAppraisalsCount = len(submittedAppraisals)
        except requests.exceptions.Timeout:
            messages.error(request, "API timeout. Server didn't respond, contact admin")
            return redirect('dashboard')
        except requests.exceptions.ConnectionError:
            messages.error(request, "Connection/network error,retry")
            return redirect('dashboard') 
        except requests.exceptions.TooManyRedirects:
            messages.error(request, "Server busy, retry")
            return redirect('dashboard') 
        except KeyError as e:
            print (e)
            messages.error(request, "Session Expired. Please Login")
            return redirect('auth')
        except Exception as e:
            print (e)
            messages.info(request, e)
            return redirect('auth')

        ctx = {
            "today": self.todays_date,
            "HOD_User":HOD_User,"department":department,
            'DPTCount':DPTCount,"full": userID,"appraisalCode":outputCode,
            "targetCount":targetCount, "outputTarget":outputTarget,
            "empAppraisalCount":empAppraisalCount,"empAppraisal":empAppraisal,
            "submittedAppraisalCount":submittedAppraisalCount,"completeAppraisalCount":completeAppraisalCount,
            "submittedAppraisal":submittedAppraisal,"completeAppraisal":completeAppraisal,
            "submittedAppraisalsCount":submittedAppraisalsCount,"submittedAppraisals":submittedAppraisals,
            }
        return render(request,"appraisal.html",ctx)
    def post(self,request):
        if request.method == "POST":
            try:
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
                response = config.CLIENT.service.FnDepartmentalAppraisalTarget(
                        applicationCode,departmentalAppraisalCode, description, 
                        weightedScore,eval(Quarter1),eval(Quarter2),eval(Quarter3),
                        eval(Quarter4),myAction)
                if response:
                    messages.success(request, "Request Successful")
                    return redirect('HODDetails',pk=response)
            except requests.exceptions.Timeout:
                messages.error(request, "API timeout. Server didn't respond, contact admin")
                return redirect('dashboard')
            except requests.exceptions.ConnectionError:
                messages.error(request, "Connection/network error,retry")
                return redirect('dashboard') 
            except requests.exceptions.TooManyRedirects:
                messages.error(request, "Server busy, retry")
                return redirect('dashboard') 
            except KeyError as e:
                print (e)
                messages.error(request, "Session Expired. Please Login")
                return redirect('auth')
            except Exception as e:
                print (e)
                messages.info(request, e)
                return redirect('auth')
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

            Access_File = config.O_DATA.format(f"/QyDocumentAttachments?$filter=No_%20eq%20%27{pk}%27%20and%20Table_ID%20eq%2052178028")
            res_file = self.get_object(Access_File)
            allFiles = [x for x in res_file['value']]

            ctx = {
                "target":res,"today": self.todays_date,
                "full":userID,"outputEmployees":outputEmployees,
                "availableEmployees":availableEmployees,"file":allFiles
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

class HODInitiate(UserObjectMixin,View):
    def post(self,request):
        if request.method == "POST":
            try:
                DepartmentalTarget = request.POST.get('DepartmentalTarget')
                empNo = request.POST.get('empNo')

                Access_Point = config.O_DATA.format(f"/QyDepartmentalAppraisalTargets?$filter=Code%20eq%20%27{DepartmentalTarget}%27")
                period_response = self.get_object(Access_Point)
                for appraisal in period_response['value']:
                    period = appraisal['DepartmentalAppraisalPeriod']

                empAppraisalEndpoint =config.O_DATA.format(f"/QyEmployeeAppraisals?$filter=EmployeeNo%20eq%20%27{empNo}%27%20and%20DepartmentalAppraisalPeriod%20eq%20%27{period}%27")
                empAppraisalResponse = self.get_object(empAppraisalEndpoint)

                for x in empAppraisalResponse['value']:
                    app_code = x['Code']

                
                response = config.CLIENT.service.FnInitiateAppraisal(app_code)
                print("response:",response)
                if response == True:
                    messages.success(request, "Success")
                    return redirect('HODDetails',pk=DepartmentalTarget)
                messages.error(request, response)
                return redirect('HODDetails',pk=DepartmentalTarget)
            except Exception as e:
                messages.error(request, e)
                print(e)
                return redirect('HODDetails',pk=DepartmentalTarget)

class UserInitiate(UserObjectMixin,View):
    def post(self,request,pk):
        if request.method == "POST":
            try:
                response = config.CLIENT.service.FnInitiateAppraisal(pk)
                print("response:",response)
                if response == True:
                    messages.success(request, "Success")
                    return redirect('FnInitiateAppraisal',pk=pk)
                messages.error(request, "False")
                return redirect('AppraisalRequests')
            except Exception as e:
                messages.error(request, e)
                print(e)
                return redirect('AppraisalRequests')
def UploadTargetAttachment(request, pk):
    if request.method == "POST":
        try:
            tableID = 52177591
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


class FnInitiateAppraisal(UserObjectMixins,View):
    def get(self,request,pk):
        try:
            userID = request.session['User_ID']
            department = request.session['User_Responsibility_Center']
            HOD_User = request.session['HOD_User']
            quarter = ''

            response = self.double_filtered_data("/QyEmployeeAppraisals","Code","eq",pk,
                                                "and","DepartmentCode","eq",department)
            for appraisal in response[1]:
                res = appraisal
                quarter = appraisal['CurrentQuarter']

            active_targets_response = self.double_filtered_data("/QyEmployeeAppraisalScores",
                                        "Appraisal_Code","eq",pk,"and","Quarter","eq",quarter)

            active_targets_count = active_targets_response[0]                      
            active_targets = active_targets_response[1]
            
            other_targets_response = self.double_filtered_data("/QyEmployeeAppraisalScores",
                                        "Appraisal_Code","eq",pk,"and","Quarter","ne",quarter)
            other_targets_count = other_targets_response[0]
            other_targets = other_targets_response[1]

            res_file = self.one_filter("/QyDocumentAttachments","No_","eq",pk)
            allFiles = [x for x in res_file[1]]

            training_response = self.one_filter("/QyAppraisalTrainingRecommendations","AppraisalNo","eq",pk)
            trainings = training_response[1]
            
        except requests.exceptions.Timeout:
            messages.error(request, "API timeout. Server didn't respond, contact admin")
            return redirect('dashboard')
        except requests.exceptions.ConnectionError:
            messages.error(request, "Connection/network error,retry")
            return redirect('dashboard') 
        except requests.exceptions.TooManyRedirects:
            messages.error(request, "Server busy, retry")
            return redirect('dashboard') 
        except KeyError as e:
            print (e)
            messages.error(request, "Session Expired. Please Login")
            return redirect('auth')
        except Exception as e:
            print(e)
            messages.info(request,e)
            return redirect('AppraisalRequests')
        ctx = {
                "appraisal":res,"HOD_User":HOD_User,
                "full":userID,"today": self.todays_date,"quarter":quarter,
                "active_targets":active_targets,"active_targets_count":active_targets_count,
                "file":allFiles, "other_targets_response":other_targets_response,
                "other_targets_count":other_targets_count,"other_targets":other_targets,
                "trainings":trainings
            }
        return render(request,"appDetails.html",ctx)
        

def FnAppraisalScores(request):
    if request.method == "POST":
        try:
            scoreScode = request.POST.get('scoreScode')
            employeeNo = request.POST.get('employeeNo')
            score = float(request.POST.get('score'))
            selfAppraisal = eval(request.POST.get('selfAppraisal'))
            appraisalCode = request.POST.get('appraisalCode')
            myAction = request.POST.get('myAction')
            quarter = request.POST.get('quarter')
            response = config.CLIENT.service.FnAppraisalScores(scoreScode,
            employeeNo,score,selfAppraisal,myAction)

            if response == True:
                messages.success(request, "Success")
                return redirect('FnInitiateAppraisal',pk=appraisalCode)
            messages.error(request, "False")
            return redirect('FnInitiateAppraisal',pk=appraisalCode)

                
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('FnInitiateAppraisal',pk=appraisalCode)
    return redirect('AppraisalRequests')

class FnRecommendedTrainings(UserObjectMixins,View):
    def post(self, request):
        try:
            appraisalCode = request.POST.get('appraisalCode')
            recommendedTraining = request.POST.get('recommendedTraining')
            selfAppraisal = eval(request.POST.get('selfAppraisal'))
            myAction = request.POST.get('myAction')

            training = config.CLIENT.service.FnRecommendedTrainings(appraisalCode,0,
                        recommendedTraining,selfAppraisal,myAction)
            if training == True:
                messages.success(request, "Success.")
                return redirect('FnInitiateAppraisal',pk=appraisalCode)
            messages.error(request, "Training info was not added")
            return redirect('FnInitiateAppraisal',pk=appraisalCode)
        except requests.exceptions.Timeout:
            messages.error(request, "API timeout. Server didn't respond, contact admin")
            return redirect('dashboard')
        except requests.exceptions.ConnectionError:
            messages.error(request, "Connection/network error,retry")
            return redirect('dashboard') 
        except requests.exceptions.TooManyRedirects:
            messages.error(request, "Server busy, retry")
            return redirect('dashboard') 
        except KeyError as e:
            print (e)
            messages.error(request, "Session Expired. Please Login")
            return redirect('auth')
        except Exception as e:
            print(e)
            messages.info(request,e)
            return redirect('AppraisalRequests')
            


def FnMovetoNextQuarter(request,pk):
    if request.method == 'POST':
        nextQuarter = config.CLIENT.service.FnMovetoNextQuarter(pk)
        if nextQuarter == True:
            messages.success(request, "Success. Moved to next quarter")
            return redirect('FnInitiateAppraisal',pk=pk)
        messages.error(request, "Success. Didn't move to next quarter, contact admin.")
        return redirect('FnInitiateAppraisal',pk=pk)
    return redirect('FnInitiateAppraisal',pk=pk)

def EmployeeAppraisalAttachment(request, pk):
    if request.method == "POST":
        try:
            tableID = 52178029
            attach = request.FILES.getlist('attachment')
        
            for files in attach:
                fileName = request.FILES['attachment'].name
                attachment = base64.b64encode(files.read())

                response = config.CLIENT.service.FnUploadAttachedDocument(
                        pk, fileName, attachment, tableID,request.session['User_ID'])

                if response == True:
                    messages.success(request, "File(s) Upload Successful")
                    return redirect('FnInitiateAppraisal',pk=pk)

                messages.error(request, "Failed, Try Again")
                return redirect('FnInitiateAppraisal',pk=pk)
        except Exception as e:
            messages.error(request,e)
            return redirect('FnInitiateAppraisal',pk=pk)
    return redirect('AppraisalRequests')

def FnsendforReview(request, pk):
    if request.method =='POST':
        try:
            response = config.CLIENT.service.FnsendforReview(pk)
            print("response:",response)
            if response == True:
                messages.success(request,"Submitted")
                return redirect('AppraisalRequests')
            messages.error(request,"Failed, contact admin")
            return redirect('FnInitiateAppraisal',pk=pk)

        except Exception as e:
            messages.error(request,e)
            return redirect('FnInitiateAppraisal',pk=pk)
    return redirect('FnInitiateAppraisal',pk=pk)

def FnSendforFurtherReview(request, pk):
    if request.method =='POST':
        try:
            response = config.CLIENT.service.FnSendforFurtherReview(pk)
            print("response:",response)
            if response == True:
                messages.success(request,"Submitted")
                return redirect('AppraisalRequests')
            messages.error(request,"Failed, contact admin")
            return redirect('FnInitiateAppraisal',pk=pk)
        except Exception as e:
            messages.error(request,e)
            return redirect('FnInitiateAppraisal',pk=pk)
    return redirect('FnInitiateAppraisal',pk=pk)