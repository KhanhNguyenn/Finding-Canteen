import requests

img = open('tmp.png','wb')
img.write(requests.get('https://maps.googleapis.com/maps/api/staticmap?center=33.0456,131.3009&zoom=12&size=320x385&key=YOUR_API_KEY').content)
img.close()
