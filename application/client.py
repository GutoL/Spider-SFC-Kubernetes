import requests

files = {
    'file': ('image.jpg', open('image.jpg', 'rb')),
}

url = 'http://127.0.0.1:5000/compress'
url = 'http://127.0.0.1:4500/compress'
response = requests.post(url, files=files)
print(response.content)
