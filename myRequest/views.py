from django.shortcuts import render
import requests
from django.conf import settings as config
import datetime as dt
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport
from requests import Session
# Create your views here.
class UserObjectMixins(object):
    model =None
    session = requests.Session()
    session.auth = config.AUTHS
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    
    def get_object(self,endpoint):
        response = self.session.get(endpoint).json()
        return response
    
    def one_filter(self,endpoint,property,filter,field_name):

        Access_Point = config.O_DATA.format(f"{endpoint}?$filter={property}%20{filter}%20%27{field_name}%27")
        response = self.get_object(Access_Point)['value']
        count=len(response)
        return count,response
   
    def double_filtered_data(self,endpoint,property_x,filter_x,filed_name_x,operater_1,property_y,filter_y,field_name_y):

        Access_Point = config.O_DATA.format(f"{endpoint}?$filter={property_x}%20{filter_x}%20%27{filed_name_x}%27%20{operater_1}%20{property_y}%20{filter_y}%20%27{field_name_y}%27")
        response = self.get_object(Access_Point)['value']
        count=len(response)
        return count,response

    def triple_filtered_data(self,endpoint,property_x,filter_x,filed_name_x,operater_1,property_y,filter_y,field_name_y,operater_2,property_z,filter_z,field_name_z):

        Access_Point = config.O_DATA.format(f"{endpoint}?$filter={property_x}%20{filter_x}%20%27{filed_name_x}%27%20{operater_1}%20{property_y}%20{filter_y}%20%27{field_name_y}%27%20{operater_2}%20{property_z}%20{filter_z}%20%27{field_name_z}%27")
        response = self.get_object(Access_Point)['value']
        count=len(response)
        return count,response

    def zeep_client(self,request):
        Username = request.session['User_ID']
        Password = request.session['password']
        AUTHS = Session()
        AUTHS.auth = HTTPBasicAuth(Username, Password)
        CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))
        return CLIENT

    def comparison_double_filter(self,endpoint,property_x,filter_x,field_name,operater_1,property_y,filter_y,property_z):
        Access_Point = config.O_DATA.format(f"{endpoint}?$filter={property_x}%20{filter_x}%20%27{field_name}%27%20{operater_1}%20{property_y}%20{filter_y}%20{property_z}")
        response = self.get_object(Access_Point)['value']
        count=len(response)
        return count,response
