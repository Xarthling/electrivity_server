from fastapi import FastAPI, Form
import requests

app = FastAPI()

FASTAPI_BASE_URL = "http://192.168.1.81:8000"

@app.get('/')
@app.post('/')
async def root():
    print("Hello World")
    return {"message": "Hello World"}

@app.post('/login')
async def client_login(email: str = Form(...), password: str = Form(...)):
    data = {'email': email, 'password': password}

    response = requests.post(f"{FASTAPI_BASE_URL}/login", data=data)  

    if response.status_code == 200:
        resp = response.json()
        print(resp)
        return {"message": "Login successful", 'user_id': resp['user_id'], 'username': resp['username'] }
    else:
        return {"error": "Login Failed", "details": response.json()}
    

@app.post('/register')
async def client_register(email: str = Form(...), username: str = Form(...), password: str = Form(...)):
    data = {
        'email': email, 
        'username': username, 
        'password': password
        }

    response = requests.post(f"{FASTAPI_BASE_URL}/register", data=data)  

    if response.status_code == 200:
    
        return {"message": "registered successful"}
    else:
        return {"error": "Login Failed", "details": response.json()}
    





