import requests

files = {
    'file': ('image.jpg', open('image.jpg', 'rb')),
}

url = 'http://127.0.0.1:5000/compress'
url = 'http://192.168.255.109:5000/'
response = requests.post(url, files=files)
print(response.content)
