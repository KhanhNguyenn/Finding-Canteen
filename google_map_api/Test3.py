import urllib.request
import json
from googlemaps import Client
API_KEY = "AIzaSyCMw47C5XfGqpJD_WoB37sO6DwRyO3i5l4"
def place_search(address,api=API_KEY): # address in tuple of (lat,lng)
    base='https://maps.googleapis.com/maps/api/place/findplacefromtext/json?'
    addP="input="+ address.replace(' ','+')
    geoUrl = base + addP + "&inputtype=textquery" + "&key=" + api # make a request
    response = urllib.request.urlopen(geoUrl)
    jsonRaw = response.read()
    jsonData = json.loads(jsonRaw) 
    return jsonData
print(place_search("30 Nanyang Crecent"))