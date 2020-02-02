import urllib.request, json, time
def GoogGeoAPI(address,api="",delay=0.1):
  base = r"https://maps.googleapis.com/maps/api/geocode/json?"
  addP = "address=" + address.replace(" ","+")
  GeoUrl = base + addP + "&key=" + api
  response = urllib.request.urlopen(GeoUrl)
  jsonRaw = response.read()
  jsonData = json.loads(jsonRaw)
  if jsonData['status'] == 'OK':
    resu = jsonData['results'][0]
    finList = [resu['formatted_address'],resu['geometry']['location']['lat'],resu['geometry']['location']['lng']]
  else:
    finList = [None,None,None]
  time.sleep(delay) #in seconds
  return finList
#while True:
text=input("Enter the loacation:")
geoR = GoogGeoAPI(address=text, api="AIzaSyCMw47C5XfGqpJD_WoB37sO6DwRyO3i5l4",delay=0)
print (geoR)
