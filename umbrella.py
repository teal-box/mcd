#-------------------------------------------------------------------------------
# Author:      ashok.chauhan
# Purpose:     Meraki Dashboard Validation for McD
#-------------------------------------------------------------------------------
import csv
import requests, json, re
import requests.packages
from typing import List, Dict
requests.packages.urllib3.disable_warnings()

################## Global Paramenters ############

def readCSV(csvFile):
    d = []
    with open(csvFile) as f:
        lines = csv.DictReader(f)
        for line in lines:
            d.append(line)
    return d

############### Base Class for Me
class Umbrella:
    # create for the ops of NSX4 tasks
    # required requests
    def __init__(self, apiKey="", secret="", gs="abc.csv"):
        self.s = requests.Session()
        self.s.verify = False
        self.headers = {
          'Accept-Encoding': 'gzip',
          'Content-Type': "application/json",
          'Accept': 'application/json'
        }
        # 'Authorization': f'Bearer {apiKey}'
        self.baseUrl = f'https://api.umbrella.com'

##        for item in wb[1]:
##            print(item)


    def __do(self, method="GET", api="", payload={}):
        url = f"{self.baseUrl}{api}"
        if method == "GET":
          response = self.s.get(url, headers = self.headers)
          if response.status_code >= 200 and response.status_code <= 299:
            return response.json()
          else:
            print("API Call: ", url)
            print("Not able to GET api, please check for API Token/credentials!!")
            return None
        if method == "POST":
          response = self.s.post(url, headers = self.headers, data=payload)
          if response.status_code >= 200 and response.status_code <= 299:
            return response.json()
          else:
            print("API Call: ", url)
            print("Not able to GET api, please check for API Token/credentials!!")
            return None

    def getToken(self, apiKey, secret):
        api = "/auth/v2/token"
        # get base auth
        import base64
        temp = bytes(f"{apiKey}:{secret}", encoding="utf8")
        temp = base64.b64encode(temp).decode("utf8")
        auth = f"Basic {temp}"
        self.headers.setdefault("Authorization", auth)
        res = self.__do(api=api)
        if res:
            self.headers.setdefault("Authorization", auth)
            del self.headers["Authorization"]
            self.headers.setdefault("Authorization", f"Bearer {res['access_token']}")
        else:
            print("Not able to get API Token check credentials")

    def getInternalNetworks(self):
        api = f"/deployments/v2/internalnetworks"
        data = self.__do(api=api)
        self.inetwork = {}
        for item in data:
            self.inetwork.setdefault(item['name'], item)
        return self.inetwork

    def createInternalNetworks(self, name, ipAddress, prefixLength, tunnelId):
        payload = self.payloadInternalNetworks(name, ipAddress, prefixLength, tunnelId)
        api = "/deployments/v2/internalnetworks"
        res = self.__do(method="POST", api=api, payload=payload)
        print(res)


    def payloadInternalNetworks(self, name, ipAddress, prefixLength, tunnelId):
        return json.dumps( {\
            "name": name,\
            "ipAddress": ipAddress, \
            "prefixLength": prefixLength, \
            "tunnelId": tunnelId \
            } )


cas = Umbrella(apiKey="", secret="")
cas.getToken(apiKey="6a9e3ea0898641429c7e080fbbd407ff", secret="27684a7253644e9b99f1a10949abaa5a")

# Internet Network-1    10.220.20.0    27    0

# cas.getInternalNetworks()
file = r"InternalNetworks.csv"
inetwork = cas.getInternalNetworks()

d = readCSV(file)
for item in d:
    # print(cas.payloadInternalNetworks(item['name'],item['ipAddress'],item['prefixLength'],item['tunnelId']))
    # cas.createInternalNetworks(item['name'],item['ipAddress'],item['prefixLength'],item['tunnelId'])
    if item['name'] in inetwork:
        print(f"{item['name']} already exist, ignoring")
    else:
        print(f"creating {item['name']}...")
        cas.createInternalNetworks(item['name'],item['ipAddress'],item['prefixLength'],item['tunnelId'])

# print(cas.getInternalNetworks())


# print(data)

