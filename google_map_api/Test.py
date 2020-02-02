import requests
api_key="AIzaSyAFmw_VG4XC4-_qvpiM1VgkszKv88pz4JM"
url="https://maps.googleapis.com/maps/api/staticmap?"
center="Nanyang Technological University"
zoom=10
r = requests.get(url + "center =" + center + "&zoom =" + str(zoom) + "&size = 400x400&key =" + api_key + "sensor = false") 
f = open('address of the file location ', 'wb') 
f.write(r.content) 
f.close() 
