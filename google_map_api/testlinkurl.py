#Function to make description of routes in words
def getRoutes(origin,destination,mode,transitMode,transitRoutingPreference):
  endpoint='https://maps.googleapis.com/maps/api/directions/json?'
  origin=origin.replace(' ','+')
  destination=destination.replace(' ','+')
  navRequest='origin={}&destination={}&mode={}&transit_mode={}&transit_routing_preference={}&key={}'.format(origin,destination,mode,transitMode,transitRoutingPreference,API_KEY)
  request=endpoint+ navRequest
  response=urllib.request.urlopen(request).read()
  directions=json.loads(response)
  #retrieve information about the routes as well as about the transportation from the list return by the directions func in googlemaps module
  routes=[]
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
