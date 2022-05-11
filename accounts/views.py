from logging import exception
from django.http import response
from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings as config
import json
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import datetime
from datetime import date
from zeep import Client
from zeep.transports import Transport
from django.contrib import messages
from requests.auth import HTTPBasicAuth
# Create your views here.


def login_request(request):
    todays_date = date.today()
    year = todays_date.year
    request.session['years'] = year
    if request.method == 'POST':
        username = request.POST.get('username').upper().strip()
        password = request.POST.get('password').strip()
        print(username, password)
        user = Session()
        user.auth = HTTPBasicAuth(username, password)
        Access_Point = config.O_DATA.format("/QyEmployees")
        Access2 = config.O_DATA.format("/QyUserSetup")
        try:
            CLIENT = Client(config.BASE_URL, transport=Transport(session=user))
            response = user.get(Access_Point, timeout=10).json()
            res_data = user.get(Access2, timeout=10).json()
            Employees = []
            Data = []
            for staff in response['value']:
                if staff['User_ID'] == username:
                    output_json = json.dumps(staff)
                    Employees.append(json.loads(output_json))
                    fullname = Employees[0]['First_Name'] + \
                        " " + Employees[0]['Last_Name']
                    request.session['fullname'] = fullname
                    request.session['User_ID'] = Employees[0]['User_ID']
                    request.session['No_'] = Employees[0]['No_']
                    user_id = request.session['User_ID']
                    full = request.session['fullname']
                    Emp_No = request.session['No_']
                    print("logged In as:", full)
                    print("UserID", user_id)
            for data in res_data['value']:
                if data['User_ID'] == username:
                    output_json = json.dumps(data)
                    Data.append(json.loads(output_json))
                    request.session['Employee_No_'] = Data[0]['Employee_No_']
                    Employee_No_ = request.session['Employee_No_']
                    request.session['Customer_No_'] = Data[0]['Customer_No_']
                    Customer_No_ = request.session['Customer_No_']
                    request.session['E_Mail'] = Data[0]['E_Mail']
                    E_Mail = request.session['E_Mail']
                    request.session['User_Responsibility_Center'] = Data[0]['User_Responsibility_Center']
                    User_Responsibility_Center = request.session['User_Responsibility_Center']
                    print('User_Responsibility_Center:',
                          User_Responsibility_Center)
                    print(request.session['User_ID'])
            return redirect('dashboard')
        except:
            messages.error(request, "Invalid username or password!!")
            return redirect('auth')
    ctx = {"year": year}
    return render(request, 'auth.html', ctx)
