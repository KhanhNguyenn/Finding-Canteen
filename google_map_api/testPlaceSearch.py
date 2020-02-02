import urllib.request
import json
from googlemaps import Client
API_KEY = "AIzaSyCMw47C5XfGqpJD_WoB37sO6DwRyO3i5l4"

def place_search(address,api=API_KEY):
    base='https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
    addP="location="+str(address[0])+","+str(address[1])
    geoUrl = base + addP + "&radius=1" + "&key=" + api # make a request
    response = urllib.request.urlopen(geoUrl)
    jsonRaw = response.read()
    jsonData = json.loads(jsonRaw) 
    name=jsonData['results'][1]['name']
    lat=jsonData['results'][1]['geometry']['location']['lat']
    lng=jsonData['results'][1]['geometry']['location']['lng']
    return [name , lat,lng]  
a=1.3503707,103.6846965
print(place_search(a))
    

    
