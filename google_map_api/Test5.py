# Python program to get a google map  
# image of specified location using  
# Google Static Maps API 
  
# importing required modules 
import requests 
  
# Enter your api key here 
api_key = " AIzaSyCMw47C5XfGqpJD_WoB37sO6DwRyO3i5l4"
  
# url variable store url 
url = "https://maps.googleapis.com/maps/api/staticmap?"
  
# center defines the center of the map, 
# equidistant from all edges of the map.  
center = "Nanyang Technological University"
  
# zoom defines the zoom 
# level of the map 
zoom = 10
  
# get method of requests module 
# return response object 
r = requests.get(url + "center =" + center + "&zoom =" +
                   str(zoom) + "&size = 400x400&key =" +
                             api_key + "sensor = false") 
  
# wb mode is stand for write binary mode 
f = open('address of the file location ', 'wb') 
  
# r.content gives content, 
# in this case gives image 
f.write(r.content) 
  
# close mthod of file object 
# save and close the file 
f.close()