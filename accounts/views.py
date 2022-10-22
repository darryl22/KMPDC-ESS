
from django.shortcuts import render, redirect
from django.conf import settings as config
import requests
from requests import Session
from django.contrib import messages
from requests.auth import HTTPBasicAuth
from django.views import View
from datetime import date
import datetime
import json
# Create your views here.
class UserObjectMixin(object):
    model =None
    user = Session()
    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    def get_object(self,username,password,endpoint):
        self.user.auth = HTTPBasicAuth(username, password)
        response = self.user.get(endpoint, timeout=10)
        return response

class Login(UserObjectMixin,View):
    template_name = 'auth.html'
    def get(self, request):
        return render(request, self.template_name)
    def post(self,request):
        username = request.POST.get('username').upper().strip()
        password = request.POST.get('password').strip()
        print(username, password)
        try:
            QyUserSetup = config.O_DATA.format(f"/QyUserSetup?$filter=User_ID%20eq%20%27{username}%27")
            res_data = self.get_object(username, password,QyUserSetup)
            if res_data.status_code != 200:
                print("QyUserSetup:",res_data.status_code)
                messages.error(request,f"Wrong Password/Username. QyUserSetup failed with status code: {res_data.status_code}")
                return redirect('auth')
            cleanedData = res_data.json()
            for data in cleanedData['value']:
                output_json = json.dumps(data)
                loadedData= json.loads(output_json)
                request.session['Employee_No_'] = loadedData['Employee_No_']
                request.session['Customer_No_'] = loadedData['Customer_No_']
                request.session['User_ID'] = loadedData['User_ID']
                request.session['E_Mail'] = loadedData['E_Mail']
                request.session['User_Responsibility_Center'] = loadedData['User_Responsibility_Center']
                request.session['password'] = password
                current_year = date.today().year
                request.session['years'] = current_year
                print(request.session['Employee_No_'])
                QyEmployees = config.O_DATA.format(f"/QyEmployees?$filter=No_%20eq%20%27{request.session['Employee_No_']}%27")
                response = self.get_object(username, password,QyEmployees)
                if response.status_code != 200:
                    messages.error(request,f"Wrong Password/Username. QyEmployees failed with status code: {response.status_code}")
                    return redirect('auth')
                cleanedData2 = response.json()
                for emp in cleanedData2['value']:
                    output_json2 = json.dumps(emp)
                    loadedData2= json.loads(output_json2)
                    request.session['Department'] = loadedData2['Department_Code']
                return redirect('dashboard')
        except requests.exceptions.RequestException as e:
            print(e)
            messages.error(request, "Invalid Username or Password")
            return redirect('auth')
        except TypeError as e:
            print(e)
            messages.error(request, e)
            return redirect('auth')

def logout(request):
    try:
        del request.session['User_ID']
        del request.session['Employee_No_']
        del request.session['Customer_No_']
        del request.session['User_Responsibility_Center']
        del request.session['Department']
        del request.session['years']
        del request.session['E_Mail']
        messages.success(request,"Logged out successfully")
    except KeyError:
        print(False)
    return redirect('auth')

class profile(UserObjectMixin,View):
    def get(self, request):
        try:
            year =request.session['years']
            fullname =request.session['User_ID']
            empNo =request.session['Employee_No_']
            Dpt =request.session['Department']
            mail =request.session['E_Mail']
        except KeyError as e:
            messages.error(request, e)
            return redirect('auth')

        ctx = {"today": self.todays_date,"year": year,"full": fullname,"empNo":empNo,"Dpt":Dpt,"mail":mail}
        return render(request,"profile.html",ctx)