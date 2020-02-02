import urllib.request
import json
from googlemaps import Client
API_KEY = "AIzaSyCMw47C5XfGqpJD_WoB37sO6DwRyO3i5l4"


def place_from_name(address: str, api=API_KEY):
    base = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input="
    second = "&inputtype=textquery&fields=name,geometry&key="
    addP = "NTU+" + address.replace(' ','+') + "+Singapore"
    url = base + addP + second + api
    response = urllib.request.urlopen(url)
    jsonData = json.loads(response.read())
    if jsonData['status'] == 'OK':   # if the addresses exist
        name = jsonData['candidates'][0]['name']
        lat = jsonData['candidates'][0]['geometry']['location']['lat']
        lng = jsonData['candidates'][0]['geometry']['location']['lng']
        return [name, lat, lng]
    else:
        return [None, None, None]


#Function to convert lat/lng into building name
def place_search(address,api=API_KEY): # address in tuple of (lat,lng)
    base='https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
    addP="location="
    if type(address) == tuple:
        addP += str(address[0]) + "," + str(address[1])
    elif type(address) == str:
        addP += "NTU+" + address + "+Singapore"
    else:
        raise TypeError("Invalid Type")
    geoUrl = base + addP + "&radius=1" + "&key=" + api # make a request
    print(geoUrl)
    response = urllib.request.urlopen(geoUrl)
    jsonRaw = response.read()
    jsonData = json.loads(jsonRaw)
    name=jsonData['results'][1]['name']
    lat=jsonData['results'][1]['geometry']['location']['lat']
    lng=jsonData['results'][1]['geometry']['location']['lng']
    return [name , lat,lng] 

# THIS HERE CRASHES
# Function to convert the location name into its buiding name and latitude/ longtitude coordinate
def name_to_lat_lon(address, api=API_KEY): #address in string of" name or address"
    base = r"https://maps.googleapis.com/maps/api/geocode/json?"
    addP = "address=" + "NTU+" + address.replace(" ","+")+"+Singapore"
    geoUrl = base + addP + "&key=" + api # make a request
    response = urllib.request.urlopen(geoUrl)
    jsonRaw = response.read()
    jsonData = json.loads(jsonRaw)  # load information and put it in jsonData
    if jsonData['status'] == 'OK':   # if the addresses exist
        # Retrieve value (information) for the key result from jsonData
        resu = jsonData['results'][0]
        lat=resu['geometry']['location']['lat']
        lng=resu['geometry']['location']['lng']
        # TODO This line below obviously crashes the function
        name= resu['formatted_address']
        # retrive information about the address, latitude, longtitude and return them as a List
        finList = [name, resu['geometry']['location']['lat'], resu['geometry']['location']['lng']]
    else:  # if the address does not exist, return None
        finList = [None, None, None]
    return finList  # finList[0]="name",finList[1]=latitude,finList[2]=longtitude


# Function to convert lat/longtitude into the address name
def convert_geocoding(lat, lng):
    gm = Client(key=API_KEY)
    revGeo = gm.reverse_geocode((lat, lng))  # reverse_geocode func in googlemaps return 	list of reverse geocoding results
    return revGeo[0]["formatted_address"]  # retrieve information from the list returned


# Function to calculate the distance along path betwee two location
def get_distance(origin, destination):# Enter the origin and destination location , type: string "address" , tuple (latitude,longtitude)
    endpoint = 'https://maps.googleapis.com/maps/api/directions/json?'
    try:
        origin = "NTU+"+origin.replace(' ', '+')+"+Singapore" #if the address input is a string
    except AttributeError:
        origin =str(origin[0])+','+str(origin[1]) # if the address iput is a tuple of lat,lng
    try:
        destination ="NTU+"+ destination.replace(' ', '+')+"+Singapore"
    except AttributeError:
        destination=str(destination[0])+','+str(destination[1])
    # Enter the place wnt to go to, type string "address" or tuple (latitude,longtitude)
    # Make the request form to google api
    navRequest = 'origin={}&destination={}&key={}'.format(origin, destination, API_KEY)
    request = endpoint + navRequest
    response = urllib.request.urlopen(request).read()
    directions = json.loads(response)
    # Direction is the built- in func in goolgemaps module and return list of routes, which contains the distance
    
    if directions['status']=='ZERO_RESULTS':
        return None
    else:
        distance = int(float(directions['routes'][0]['legs'][0]['distance']['text'][:len(directions['routes'][0]['legs'][0]['distance']['text'])-3]) * 1000)
        return distance
# distance as a integer ,value in m

#Function to caculate list of distance from given origin and list of destinations
def distance_list(origin,destination):
    try:
        origin="NTU+"+origin+"+Singapore"
        pass
    except:
        pass
    for i in range(len(destination)):
        try:
            destination[i]="NTU+" + destination[i].replace(" ","+") + "+Singapore"
        except:
            pass
        
    gmaps = Client(key=API_KEY)
    matrix = gmaps.distance_matrix(origin, destination, mode="walking")
    list=[]
    for i in range(len(matrix['rows'][0]['elements'])):
        if matrix['rows'][0]['elements'][i]['status']=='ZERO_RESULTS':# Check for infeasible routes
            list.append(None) # If there is no viable routes, distance is returned as None
        else:
            list.append(int(float(matrix['rows'][0]['elements'][i]['distance']['text'][:len(matrix['rows'][0]['elements'][i]['distance']['text'])-3])*1000))
    return list

  
   
# Function to open url for direction
def get_url(origin, destination):
    try:
        origin ="NTU+" + origin.replace(' ', '+') +"+Singapore"
    except:
        origin=str(origin[0]) +',' +str(origin[1])
    try:
        destination="NTU+" + destination.reolace(' ','+') + "+Singapore"
    except:
        destination=str(destination[0]) +',' +str(destination[1])
    url = "https://maps.google.com/?saddr={}&daddr={}".format(origin, destination)
    return url  


# Function to open url for direction
def get_directions_url(origin, destination):
    try:
        origin ="NTU+" + origin.replace(' ', '+') +"+Singapore"
    except:
        origin=str(origin[0]) +',' +str(origin[1])
    try:
        destination="NTU+" + destination.reolace(' ','+') + "+Singapore"
    except:
        destination=str(destination[0]) +',' +str(destination[1])
    url = "https://www.google.com/maps/dir/?api=1&origin={}&destination={}&travelmode=walking".format(origin, destination)
    return url



 
