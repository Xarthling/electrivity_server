import requests

def hello():
    id = int(input('Enter  id: '))
    val = int(input('Enter switch id: '))
    
    response = requests.post('http://192.168.1.81:8000/touch/', data={'switchId': val, 'id': id})

    if response.status_code == 200:
        return 'Signal sent successfully'
    else:
        return 'Failed to send signal'

while True:
    hello()
