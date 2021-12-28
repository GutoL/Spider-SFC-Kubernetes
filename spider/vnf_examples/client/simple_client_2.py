import requests

files = {
    'file': ('image.jpg', open('image.jpg', 'rb')),
}


url = 'http://192.168.0.209:5000/'

response = requests.post(url, files=files)
print(response.content)
