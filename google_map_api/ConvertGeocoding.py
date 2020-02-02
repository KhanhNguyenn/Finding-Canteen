from googlemaps import Client

lat = input('Enter latitude: ')
lng = input('Enter longitude: ')

gm = Client(key="AIzaSyCMw47C5XfGqpJD_WoB37sO6DwRyO3i5l4")
rev_geo = gm.reverse_geocode((lat, lng))

print("Street address:", rev_geo[0]["formatted_address"])
print("Location name: ",rev_geo[0]['address_components'][0]['long_name'])
