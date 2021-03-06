from fastapi import FastAPI, Request, status
import requests
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import hashlib
import datetime
import json

app = FastAPI()
app.counter_id = 1
app.patients = []



def sha512(password):
    sha512_hash = hashlib.sha512()
    sha512_hash.update(bytes(password, encoding="ASCII"))
    return sha512_hash.hexdigest()

def addDayToDateYMD(date, days:int, seperator:str = '-'):
    date_str = str(date)
    YMD = [int(ele) for ele in date_str.split(seperator)]
    date = datetime.date(YMD[0],YMD[1],YMD[2])
    date += datetime.timedelta(days=days)
    return date

class Item(BaseModel):
    name: str
    surname: str

class Patient:

    def __init__(self, name, surname, tday=datetime.date.today()):
        self.id = app.counter_id
        app.counter_id+=1
        self.name = name
        self.surname = surname
        l_name = self.size_letters(self.name)
        l_surname = self.size_letters(self.surname)
        self.register_date = tday
        self.vaccination_date = addDayToDateYMD(tday,l_name+l_surname)
    
    def size_letters(self,inscription:str):
        count = 0
        for char in inscription:
            if char.isalpha():
                count+=1
        return count

    def dataInDict(self):
        return {
        "id": self.id,
        "name": self.name,
        "surname": self.surname,
        "register_date": str(self.register_date),
        "vaccination_date": str(self.vaccination_date)
        }
    
    def __str__(self):
        ans = [ele for ele in self.dataInDict().values()]
        return str(ans)

# endpoint:
# zad 1.1

@app.get("/")
def root():
    return {"message": "Hello world!"}

# zad 1.2

@app.get("/method")
def method():
    return JSONResponse(content={"method": "GET"},status_code=200)

@app.put("/method")
def method():
    return JSONResponse(content={"method": "PUT"},status_code=200)

@app.options("/method")
def method():
    return JSONResponse(content={"method": "OPTIONS"},status_code=200)

@app.delete("/method")
def method():
    return JSONResponse(content={"method": "DELETE"},status_code=200)

@app.post("/method")
def method():
    return JSONResponse(content={"method": "POST"},status_code=201)

# end-zad 1.2
# zad 1.3

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=401)

@app.get("/auth")
def auth(password,password_hash):
    if password == "" or password_hash == "":
        return HTMLResponse(status_code=401)
    
    if sha512(password) == password_hash:
        return HTMLResponse(status_code=204)
    else:
        return HTMLResponse(status_code=401)

# end-zad 1.3
# zad 1.4
@app.post("/register")
async def register(item: Item):
    patient = Patient(item.name,item.surname)
    app.patients.append(patient)
    return JSONResponse(content=patient.dataInDict(),status_code=201)

# end zad 1.4
# zad 1.5

@app.get("/patient/{id}")
def get_patient_id(id: int):
    if id<1: return JSONResponse(status_code=400)

    for patient in app.patients:
        if patient.id == id:
            return JSONResponse(content=patient.dataInDict(),status_code=200)
    
    return JSONResponse(status_code=404)