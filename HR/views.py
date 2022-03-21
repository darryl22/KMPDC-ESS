import base64
from curses.ascii import isdigit
from urllib import request
from django.shortcuts import render, redirect
from datetime import date, datetime
from isodate import date_isoformat
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime as dt
from django.contrib import messages

# Create your views here.


def Leave_Planner(request):
    fullname = request.session['fullname']
    year = request.session['years']
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyLeavePlannerHeaders")
    try:
        response = session.get(Access_Point, timeout=10).json()
        Plans = []
        for leave in response['value']:
            if leave['Employee_No_'] == request.session['Employee_No_']:
                output_json = json.dumps(leave)
                Plans.append(json.loads(output_json))
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": Plans,
           "year": year, "full": fullname}
    return render(request, 'planner.html', ctx)


def CreatePlanner(request):
    plannerNo = ""
    employeeNo = request.session['Employee_No_']
    myAction = ""
    if request.method == 'POST':
        try:
            myAction = request.POST.get('myAction')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('LeavePlanner')
    try:
        response = config.CLIENT.service.FnLeavePlannerHeader(
            plannerNo, employeeNo, myAction)
        messages.success(request, "You have successfully  Added!!")
        print(response)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('LeavePlanner')


def PlanDetail(request, pk):
    fullname = request.session['fullname']
    year = request.session['years']
    session = requests.Session()
    session.auth = config.AUTHS
    res = ''
    state = ''
    Access_Point = config.O_DATA.format("/QyLeavePlannerHeaders")
    try:
        response = session.get(Access_Point, timeout=10).json()
        openPlan = []
        Pending = []
        for plan in response['value']:
            if plan['Employee_No_'] == request.session['Employee_No_']:
                output_json = json.dumps(plan)
                openPlan.append(json.loads(output_json))
                for claim in openPlan:
                    if claim['No_'] == pk:
                        res = claim
    except requests.exceptions.ConnectionError as e:
        print(e)
    Lines_Res = config.O_DATA.format("/QyLeavePlannerLines")
    try:
        responses = session.get(Lines_Res, timeout=10).json()
        openLines = []
        for train in responses['value']:
            if train['Document_No_'] == pk and train['Employee_No_'] == request.session['Employee_No_']:
                output_json = json.dumps(train)
                openLines.append(json.loads(output_json))
    except requests.exceptions.ConnectionError as e:
        print(e)
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res,
           "year": year, "full": fullname,
           "line": openLines}
    return render(request, 'planDetails.html', ctx)


def FnSubmitLeavePlanner(request, pk):
    plannerNo = pk
    employeeNo = request.session['Employee_No_']
    if request.method == 'POST':
        try:
            response = config.CLIENT.service.FnSubmitLeavePlanner(
                plannerNo, employeeNo)
            messages.success(request, "You have successfully  Added!!")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('PlanDetail', pk=pk)

# Delete leave Planner Header


def FnDeleteLeavePlannerHeader(request):
    plannerNo = ""
    employeeNo = request.session['Employee_No_']
    if request.method == 'POST':
        plannerNo = request.POST.get('plannerNo')
        try:
            response = config.CLIENT.service.FnDeleteLeavePlannerHeader(
                plannerNo, employeeNo)
            messages.success(request, "Successfully Deleted")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('LeavePlanner')


def CreatePlannerLine(request, pk):
    lineNo = ""
    plannerNo = pk
    startDate = ""
    endDate = ""
    myAction = ""

    if request.method == 'POST':
        try:
            lineNo = int(request.POST.get('lineNo'))
            startDate = datetime.strptime(
                (request.POST.get('startDate')), '%Y-%m-%d').date()
            endDate = datetime.strptime(
                (request.POST.get('endDate')), '%Y-%m-%d').date()
            myAction = request.POST.get('myAction')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('PlanDetail', pk=pk)
    if not lineNo:
        lineNo = 0
    try:
        response = config.CLIENT.service.FnLeavePlannerLine(
            lineNo, plannerNo, startDate, endDate, myAction)
        messages.success(request, "You have successfully  Added!!")
        print(response)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('PlanDetail', pk=pk)


def FnDeleteLeavePlannerLine(request, pk):
    plannerNo = pk
    lineNo = ""

    if request.method == 'POST':
        try:
            lineNo = int(request.POST.get('lineNo'))
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('PlanDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnDeleteLeavePlannerLine(plannerNo,
                                                                  lineNo)
        messages.success(request, "Successfully  Deleted!!")
        print(response)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('PlanDetail', pk=pk)


def Leave_Request(request):
    fullname = request.session['fullname']
    year = request.session['years']
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyLeaveApplications")
    LeaveTypes = config.O_DATA.format("/QyLeaveTypes")
    LeavePlanner = config.O_DATA.format("/QyLeavePlannerLines")
    try:
        response = session.get(Access_Point, timeout=10).json()
        res_types = session.get(LeaveTypes, timeout=10).json()
        res_planner = session.get(LeavePlanner, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
        Pending = []
        Plan = []
        Leave = res_types['value']
        for planner in res_planner['value']:
            if planner['Employee_No_'] == request.session['Employee_No_']:
                output_json = json.dumps(planner)
                Plan.append(json.loads(output_json))
        for imprest in response['value']:
            if imprest['Status'] == 'Open' and imprest['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                open.append(json.loads(output_json))
            if imprest['Status'] == 'Released' and imprest['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                Approved.append(json.loads(output_json))
            if imprest['Status'] == 'Rejected' and imprest['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                Rejected.append(json.loads(output_json))
            if imprest['Status'] == "Pending Approval" and imprest['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                Pending.append(json.loads(output_json))
        counts = len(open)
        pend = len(Pending)
        print(request.session['User_ID'])

        counter = len(Approved)

        reject = len(Rejected)

    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open,
           "count": counts, "response": Approved,
           "counter": counter, "rej": Rejected,
           'reject': reject, 'leave': Leave,
           "plan": Plan, "pend": pend,
           "pending": Pending, "year": year,
           "full": fullname}
    return render(request, 'leave.html', ctx)


def CreateLeave(request):
    applicationNo = ''
    employeeNo = request.session['Employee_No_']
    usersId = request.session['User_ID']
    dimension3 = ''
    leaveType = ""
    plannerStartDate = "",
    daysApplied = ""
    isReturnSameDay = ''
    myAction = ''
    if request.method == 'POST':
        try:
            applicationNo = request.POST.get('applicationNo')
            leaveType = request.POST.get('leaveType')
            plannerStartDate = datetime.strptime(
                (request.POST.get('plannerStartDate')), '%Y-%m-%d').date()
            daysApplied = int(request.POST.get('daysApplied'))
            isReturnSameDay = eval(request.POST.get('isReturnSameDay'))
            myAction = request.POST.get('myAction')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('leave')
    if not applicationNo:
        applicationNo = " "
    print(applicationNo)
    try:
        response = config.CLIENT.service.FnLeaveApplication(
            applicationNo, employeeNo, usersId, dimension3, leaveType, plannerStartDate, daysApplied, isReturnSameDay, myAction)
        messages.success(request, "You have successfully  Added!!")
        print(response)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('leave')


def FnDeleteLeavePlannerHeader(request):
    plannerNo = ""
    employeeNo = request.session['Employee_No_']
    if request.method == 'POST':
        plannerNo = request.POST.get('plannerNo')
        try:
            response = config.CLIENT.service.FnDeleteLeavePlannerHeader(
                plannerNo, employeeNo)
            messages.success(request, "Successfully Deleted")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('LeavePlanner')


def FnDeleteLeaveApplication(request):
    employeeNo = request.session['Employee_No_']
    applicationNo = ""

    if request.method == 'POST':
        applicationNo = request.POST.get('applicationNo')
        try:
            response = config.CLIENT.service.FnDeleteLeaveApplication(
                employeeNo, applicationNo)
            messages.success(request, "Successfully Deleted")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('leave')


def LeaveDetail(request, pk):
    fullname = request.session['fullname']
    year = request.session['years']
    session = requests.Session()
    session.auth = config.AUTHS
    res = ''
    state = ''
    Access_Point = config.O_DATA.format("/QyLeaveApplications")
    Approver = config.O_DATA.format("/QyApprovalEntries")
    Ledger = config.O_DATA.format("/QyLeaveLedgerEntries")
    try:
        response = session.get(Access_Point, timeout=10).json()
        res_approver = session.get(Approver, timeout=10).json()
        res_Ledger = session.get(Ledger, timeout=10).json()
        openClaim = []
        Approvers = []
        Pending = []
        Ledgers = []
        # for Ledger in res_Ledger['value']:
        #     if Ledger['Staff_No_'] == request.session['Employee_No_'] and Ledger['Leave_Period_Code'] == request.session['Leave_Period'] and Ledger['Leave_Type'] == request.session['Leave_Code']:
        #         output_json = json.dumps(Ledger)
        #         Ledgers.append(json.loads(output_json))
        for approver in res_approver['value']:
            if approver['Document_No_'] == pk:
                output_json = json.dumps(approver)
                Approvers.append(json.loads(output_json))
        for claim in response['value']:
            if claim['Status'] == 'Released' and claim['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['Application_No'] == pk:
                        res = claim
                        if claim['Status'] == 'Released':
                            state = 3
            if claim['Status'] == 'Open' and claim['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['Application_No'] == pk:
                        request.session['Leave_Period'] = claim['Leave_Period']
                        request.session['Leave_Code'] = claim['Leave_Code']
                        res = claim
                        if claim['Status'] == 'Open':
                            state = 1
            if claim['Status'] == 'Rejected' and claim['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['Application_No'] == pk:
                        res = claim
            if claim['Status'] == "Pending Approval" and claim['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(claim)
                Pending.append(json.loads(output_json))
                for claim in Pending:
                    if claim['Application_No'] == pk:
                        res = claim
                        if claim['Status'] == 'Pending Approval':
                            state = 2
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res,
           "Approvers": Approvers, "state": state,
           "year": year, "full": fullname}
    return render(request, 'leaveDetail.html', ctx)


def UploadLeaveAttachment(request, pk):
    docNo = pk
    response = ""
    fileName = ""
    attachment = ""
    tableID = 52177494

    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
        except Exception as e:
            return redirect('IMPDetails', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    docNo, fileName, attachment, tableID)
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "Successfully Sent !!")

            return redirect('LeaveDetail', pk=pk)
        else:
            messages.error(request, "Not Sent !!")
            return redirect('LeaveDetail', pk=pk)

    return redirect('LeaveDetail', pk=pk)


def LeaveApproval(request, pk):
    employeeNo = request.session['Employee_No_']
    applicationNo = ""
    if request.method == 'POST':
        try:
            applicationNo = request.POST.get('applicationNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('LeaveDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnRequestLeaveApproval(
            employeeNo, applicationNo)
        messages.success(request, "Approval Request Successfully Sent!!")
        print(response)
        return redirect('LeaveDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('LeaveDetail', pk=pk)


def LeaveCancelApproval(request, pk):
    employeeNo = request.session['Employee_No_']
    applicationNo = ""
    if request.method == 'POST':
        try:
            applicationNo = request.POST.get('applicationNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('LeaveDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnCancelLeaveApproval(
            employeeNo, applicationNo)
        messages.success(request, "Cancel Approval Request Successful !!")
        print(response)
        return redirect('LeaveDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('LeaveDetail', pk=pk)


def Training_Request(request):
    fullname = request.session['fullname']
    year = request.session['years']

    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyTrainingRequests")
    currency = config.O_DATA.format("/QyCurrencies")
    trainingNeed = config.O_DATA.format("/QyTrainingNeeds")
    destination = config.O_DATA.format("/QyDestinations")
    try:
        response = session.get(Access_Point, timeout=10).json()
        res_currency = session.get(currency, timeout=10).json()
        res_train = session.get(trainingNeed, timeout=10).json()
        res_dest = session.get(destination, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
        Pending = []
        cur = res_currency['value']
        trains = res_train['value']
        destinations = res_dest['value']
        for imprest in response['value']:
            if imprest['Status'] == 'Open' and imprest['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(imprest)
                open.append(json.loads(output_json))
            if imprest['Status'] == 'Released' and imprest['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(imprest)
                Approved.append(json.loads(output_json))
            if imprest['Status'] == 'Rejected' and imprest['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(imprest)
                Rejected.append(json.loads(output_json))
            if imprest['Status'] == 'Pending Approval' and imprest['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(imprest)
                Pending.append(json.loads(output_json))
        counts = len(open)

        counter = len(Approved)

        reject = len(Rejected)

        pend = len(Pending)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open,
           "count": counts, "response": Approved,
           "counter": counter, "rej": Rejected,
           'reject': reject, 'cur': cur,
           "train": trains, "des": destinations,
           "pend": pend, "pending": Pending,
           "year": year, "full": fullname}
    return render(request, 'training.html', ctx)


def CreateTrainingRequest(request):
    requestNo = ''
    employeeNo = request.session['Employee_No_']
    usersId = request.session['User_ID']
    designation = request.session['User_Responsibility_Center']
    isAdhoc = ""
    trainingNeed = ""
    description = ""
    startDate = ''
    endDate = ''
    destination = ''
    myAction = ''
    if request.method == 'POST':
        try:
            requestNo = request.POST.get('requestNo')
            isAdhoc = eval(request.POST.get('isAdhoc'))
            description = request.POST.get('description')
            startDate = datetime.strptime(
                request.POST.get('startDate'), '%Y-%m-%d').date()
            trainingNeed = request.POST.get('trainingNeed')
            destination = request.POST.get('destination')
            endDate = datetime.strptime(
                request.POST.get('endDate'), '%Y-%m-%d').date()
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('training_request')
    if not requestNo:
        requestNo = " s"
    print(requestNo)
    try:
        response = config.CLIENT.service.FnTrainingRequest(
            requestNo, employeeNo, usersId, designation, isAdhoc, trainingNeed, description, startDate, endDate, destination, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('training_request')


def EditTrainingRequest(request):
    requestNo = ''
    employeeNo = request.session['Employee_No_']
    usersId = request.session['User_ID']
    designation = request.session['User_Responsibility_Center']
    isAdhoc = ""
    trainingNeed = ""
    description = ""
    startDate = ''
    endDate = ''
    destination = ''
    currency = ''
    myAction = 'modify'
    if request.method == 'POST':
        try:
            isAdhoc = request.POST.get('isAdhoc')
            description = request.POST.get('description')
            startDate = request.POST.get('startDate')
            trainingNeed = request.POST.get('trainingNeed')
            destination = request.POST.get('destination')
            endDate = request.POST.get('endDate')
            currency = request.POST.get('currency')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('training_request')
    try:
        response = config.CLIENT.service.FnTrainingRequest(
            requestNo, employeeNo, usersId, designation, isAdhoc, trainingNeed, description, startDate, endDate, destination, currency, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('training_request')


def TrainingDetail(request, pk):
    fullname = request.session['fullname']
    year = request.session['years']

    session = requests.Session()
    session.auth = config.AUTHS
    res = ''
    state = ""
    train_status = ""
    Access_Point = config.O_DATA.format("/QyTrainingRequests")
    Approver = config.O_DATA.format("/QyApprovalEntries")
    try:
        response = session.get(Access_Point, timeout=10).json()
        res_approver = session.get(Approver, timeout=10).json()
        openClaim = []
        Approvers = []
        Pending = []
        for approver in res_approver['value']:
            if approver['Document_No_'] == pk:
                output_json = json.dumps(approver)
                Approvers.append(json.loads(output_json))
        for claim in response['value']:
            if claim['Status'] == 'Released' and claim['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['Request_No_'] == pk:
                        res = claim
                        if claim['Status'] == 'Released':
                            state = 3
            if claim['Status'] == 'Open' and claim['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['Request_No_'] == pk:
                        res = claim
                        if claim['Status'] == 'Open':
                            state = 1
                        if claim['Adhoc'] == True:
                            train_status = "Adhoc"
            if claim['Status'] == 'Rejected' and claim['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['Request_No_'] == pk:
                        res = claim
            if claim['Status'] == 'Pending Approval' and claim['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(claim)
                Pending.append(json.loads(output_json))
                for claim in Pending:
                    if claim['Request_No_'] == pk:
                        res = claim
                        if claim['Status'] == 'Pending Approval':
                            state = 2
    except requests.exceptions.ConnectionError as e:
        print(e)
    Lines_Res = config.O_DATA.format("/QyTrainingNeedsRequest")
    try:
        response = session.get(Lines_Res, timeout=10).json()
        openLines = []
        for train in response['value']:
            if train['Source_Document_No'] == pk and train['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(train)
                openLines.append(json.loads(output_json))
    except requests.exceptions.ConnectionError as e:
        print(e)
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res,
           "Approvers": Approvers, "state": state,
           "year": year, "full": fullname,
           "train_status": train_status, "line": openLines}
    return render(request, 'trainingDetail.html', ctx)


def FnAdhocTrainingNeedRequest(request, pk):
    requestNo = pk
    no = ""
    employeeNo = request.session['Employee_No_']
    trainingName = ""
    trainingArea = ""
    trainingObjectives = ""
    venue = ""
    provider = ""
    myAction = "insert"
    if request.method == 'POST':
        try:
            trainingName = request.POST.get('trainingName')
            trainingArea = request.POST.get('trainingArea')
            trainingObjectives = request.POST.get('trainingObjectives')
            venue = request.POST.get('venue')
            provider = request.POST.get('provider')

        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnAdhocTrainingNeedRequest(requestNo,
                                                                    no, employeeNo, trainingName, trainingArea, trainingObjectives, venue, provider, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
        return redirect('TrainingDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('TrainingDetail', pk=pk)


def UploadTrainingAttachment(request, pk):
    docNo = pk
    response = ""
    fileName = ""
    attachment = ""
    tableID = 52177501

    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
        except Exception as e:
            return redirect('IMPDetails', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    docNo, fileName, attachment, tableID)
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "Successfully Sent !!")

            return redirect('TrainingDetail', pk=pk)
        else:
            messages.error(request, "Not Sent !!")
            return redirect('TrainingDetail', pk=pk)

    return redirect('TrainingDetail', pk=pk)


def FnAdhocTrainingEdit(request, pk, no):
    requestNo = pk
    no = no
    employeeNo = request.session['Employee_No_']
    trainingName = ""
    trainingArea = ""
    trainingObjectives = ""
    venue = ""
    provider = ""
    myAction = "modify"

    if request.method == 'POST':
        try:
            trainingName = request.POST.get('trainingName')
            trainingArea = request.POST.get('trainingArea')
            trainingObjectives = request.POST.get('trainingObjectives')
            venue = request.POST.get('venue')
            provider = request.POST.get('provider')

        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnAdhocTrainingNeedRequest(requestNo,
                                                                    no, employeeNo, trainingName, trainingArea, trainingObjectives, venue, provider, myAction)
        messages.success(request, "Successfully Edited!!")
        print(response)
        return redirect('TrainingDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('TrainingDetail', pk=pk)


def FnDeleteTrainingRequest(request):
    requestNo = ""
    employeeNo = request.session['Employee_No_']
    usersId = request.session['User_ID']

    if request.method == 'POST':
        try:
            requestNo = request.POST.get('requestNo')
        except ValueError as e:
            return redirect('training_request')

    try:
        response = config.CLIENT.service.FnDeleteTrainingRequest(
            requestNo, employeeNo, usersId)
        messages.success(request, "Successfully Deleted!!")
        print(response)
        return redirect('training_request')
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('training_request')


def FnAdhocLineDelete(request, pk):
    requestNo = pk
    needNo = ''

    if request.method == 'POST':
        try:
            needNo = request.POST.get('needNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
    print("requestNo", requestNo)
    print("needno", needNo)
    try:
        response = config.CLIENT.service.FnDeleteAdhocTrainingNeedRequest(
            requestNo, needNo)
        messages.success(request, "Successfully Deleted!!")
        print(response)
        return redirect('TrainingDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('TrainingDetail', pk=pk)


def TrainingApproval(request, pk):
    myUserID = request.session['User_ID']
    trainingNo = ""
    if request.method == 'POST':
        try:
            trainingNo = request.POST.get('trainingNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnRequestTrainingApproval(
            myUserID, trainingNo)
        messages.success(request, "Approval Request Successfully Sent!!")
        print(response)
        return redirect('TrainingDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('TrainingDetail', pk=pk)


def TrainingCancelApproval(request, pk):
    myUserID = request.session['User_ID']
    trainingNo = ""
    if request.method == 'POST':
        try:
            trainingNo = request.POST.get('trainingNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnCancelTrainingApproval(
            myUserID, trainingNo)
        messages.success(request, "Cancel Approval Request Successful !!")
        print(response)
        return redirect('TrainingDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('TrainingDetail', pk=pk)


def PNineRequest(request):
    fullname = request.session['fullname']
    year = request.session['years']
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")

    employeeNo = request.session['Employee_No_']
    filenameFromApp = ""
    startDate = ""
    endDate = ""
    if request.method == 'POST':
        try:
            filenameFromApp = request.POST.get('filenameFromApp')
            startDate = datetime.strptime(
                request.POST.get('startDate'), '%Y-%m-%d').date()
            endDate = datetime.strptime(
                request.POST.get('endDate'), '%Y-%m-%d').date()
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('pNine')
        filenameFromApp = filenameFromApp + ".pdf"
        try:
            response = config.CLIENT.service.FnGeneratePNine(
                employeeNo, filenameFromApp, startDate, endDate)
            messages.success(request, "Request Successful !!")
            print(response)
            return redirect('pNine')
        except Exception as e:
            messages.error(request, e)
            print(e)
    ctx = {"today": todays_date, "year": year, "full": fullname}
    return render(request, "p9.html", ctx)


def PayslipRequest(request):
    fullname = request.session['fullname']
    year = request.session['years']
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    employeeNo = request.session['Employee_No_']
    filenameFromApp = ""
    paymentPeriod = ""
    if request.method == 'POST':
        try:
            filenameFromApp = request.POST.get('filenameFromApp')
            paymentPeriod = datetime.strptime(
                request.POST.get('paymentPeriod'), '%Y-%m-%d').date()

        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('payslip')
        filenameFromApp = filenameFromApp + ".pdf"
        try:
            response = config.CLIENT.service.FnGeneratePayslip(
                employeeNo, filenameFromApp, paymentPeriod)
            messages.success(request, "Request Successful !!")
            print(response)
            return redirect('payslip')
        except Exception as e:
            messages.error(request, e)
            print(e)
    ctx = {"today": todays_date, "year": year, "full": fullname}
    return render(request, "payslip.html", ctx)
# Leave Report


def FnGenerateLeaveReport(request, pk):
    employeeNo = request.session['Employee_No_']
    filenameFromApp = ''
    applicationNo = pk
    if request.method == 'POST':
        try:
            filenameFromApp = request.POST.get('filenameFromApp')
        except ValueError as e:
            messages.error(request, "Invalid Line number, Try Again!!")
            return redirect('LeaveDetail', pk=pk)
    filenameFromApp = filenameFromApp + ".pdf"
    try:
        response = config.CLIENT.service.FnGenerateLeaveReport(
            employeeNo, filenameFromApp, applicationNo)
        messages.success(request, "Successfully Sent!!")
        print(response)
        return redirect('LeaveDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('LeaveDetail', pk=pk)
# Training report


def FnGenerateTrainingReport(request, pk):
    employeeNo = request.session['Employee_No_']
    filenameFromApp = ''
    applicationNo = pk
    if request.method == 'POST':
        try:
            filenameFromApp = request.POST.get('filenameFromApp')
        except ValueError as e:
            messages.error(request, "Invalid Line number, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
    filenameFromApp = filenameFromApp + ".pdf"
    try:
        response = config.CLIENT.service.FnGenerateLeaveReport(
            employeeNo, filenameFromApp, applicationNo)
        messages.success(request, "Successfully Sent!!")
        print(response)
        return redirect('TrainingDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('TrainingDetail', pk=pk)
