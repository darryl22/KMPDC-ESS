from django.shortcuts import render
import requests
from django.conf import settings as config

# Create your views here.
class UserObjectMixin(object):
    model =None
    session = requests.Session()
    session.auth = config.AUTHS

    def get_object(self,endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response

    def get_filtered_data(self,endpoint,property,filter):
        Access_Point = config.O_DATA.format(f"{endpoint}?$filter={property}%20eq%20%27{filter}%27")

        response = self.get_object(Access_Point)
        return response