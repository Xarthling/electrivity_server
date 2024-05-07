import requests

def hello():
    # Get the switch ID from user input
    id = int(input('Enter  id: '))
    val = int(input('Enter switch id: '))
    
    # Sending a POST request to the API endpoint with form data
    response = requests.post('http://192.168.1.81:8000/touch/', data={'switchId': val, 'id': id})

    # Checking if the request was successful (status code 200)
    if response.status_code == 200:
        return 'Signal sent successfully'
    else:
        return 'Failed to send signal'

while True:
    hello()
