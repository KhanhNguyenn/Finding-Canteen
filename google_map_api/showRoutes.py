import urllib.request
import json
endpoint='https://maps.googleapis.com/maps/api/directions/json?'
api_key='AIzaSyCMw47C5XfGqpJD_WoB37sO6DwRyO3i5l4'
origin=input('Where are you: ?').replace(' ','+')
destination=input('where do you want to go: ').replace(' ','+')
mode=input("Enter the mode of transportation: ")
transit_mode=input("enter the transit mode: ")
transit_routing_preference=input("Enter the preference:")

nav_request='origin={}&destination={}&mode={}&transit_mode={}&transit_routing_preference={}&key={}'.format(origin,destination,mode,transit_mode,transit_routing_preference,api_key)
request=endpoint+ nav_request
response=urllib.request.urlopen(request).read()
directions=json.loads(response)
for i in range (len(directions['routes'][0]['legs'][0]['steps'])):
    print(directions['routes'][0]['legs'][0]['steps'][i]['html_instructions'])
    if directions['routes'][0]['legs'][0]['steps'][i]['travel_mode']=='TRANSIT':
        print('   ','The arrival stop is: ',directions['routes'][0]['legs'][0]['steps'][i]['transit_details']['arrival_stop']['name'])
        print('   ','The departure stop is: ',directions['routes'][0]['legs'][0]['steps'][i]['transit_details']['departure_stop']['name'])
        print('   ','The headsign is: ',directions['routes'][0]['legs'][0]['steps'][i]['transit_details']['headsign'])
        print('   ','The vehicle is: ',directions['routes'][0]['legs'][0]['steps'][i]['transit_details']['line']['vehicle']['type'],end=" ")
        if 'short_name' in directions['routes'][0]['legs'][0]['steps'][i]['transit_details']['line']: 
            print(directions['routes'][0]['legs'][0]['steps'][i]['transit_details']['line']['short_name'])
        else:
            print(directions['routes'][0]['legs'][0]['steps'][i]['transit_details']['line']['name'])
        print('   ','The number of stops are: ',directions['routes'][0]['legs'][0]['steps'][i]['transit_details']['num_stops'])     
                      
