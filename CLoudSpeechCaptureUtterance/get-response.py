import requests
import json

api_url_base = 'http://192.168.1.212:45455/api/myDemon'
parameters = {"Data":"post test another another","isComplete":False}
description = {"Content-Type":"application/json; charset=utf-8"}
#json_string = json.dumps(parameters)
#print(json_string)

#parameters = json.dumps('{"Data":"post test another","isComplete":false}')

response = requests.get(api_url_base)
print(response)
print(response.text)
#parameters = json.loads(response.text)
#parameters.data = "floop"
#response = requests.post(api_url_base, data = json_string)
#response = requests.post(api_url_base,data={"Data":"blah","isComplete":False},headers={"Content-Type":"application/json"})
#response = requests.post(api_url_base,data={"Data":"blah","isComplete":False})
response = requests.post(api_url_base, json = parameters, headers = description)
#response = requests.post(api_url_base, parameters, description)
#print(response)
#print(response.text)
response = requests.get(api_url_base)
print(response)
print(response.text)
