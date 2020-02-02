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
print (directions)
