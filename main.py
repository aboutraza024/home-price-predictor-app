# main.py
from models import app,SessionLocal
from auth import send_verification_code
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
import pandas as pd
from models import get_user_by_email, get_user_by_email_google, get_user_by_github, create_user_with_github, \
    create_user_with_google, create_user
from models import UserCreate, LoginUser, Register_With_Email, PredictHouse
from auth import send_verification_code
from models import app, SessionLocal
import uvicorn
from fastapi import FastAPI, Form, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
import random
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx
from authlib.integrations.starlette_client import OAuth, OAuthError


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
get_email = {}
get_email_forget = {}
data = {}

def v_code():
    return random.randint(100000, 999999)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

verification_code = v_code()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





@app.post("/register")
def reg_user( user: UserCreate, backgroundtask: BackgroundTasks,db: Session = Depends(get_db),request: Request=None):
    get_email["f_name"] = user.first_name
    get_email["l_name"] = user.last_name
    get_email["email"] = user.email
    hashed_passowrd=hash_password(user.password)
    get_email["password"] = hashed_passowrd
    print("Hello", user)
    existing_user = get_user_by_email(db, email=user.email)
    if existing_user:
        return {
        "status": 409,
        "message": "User already registered with this email."
        }
    backgroundtask.add_task(send_verification_code, user.email, verification_code)
    return {
    "status": 200
    }




@app.post("/login")
def login_user(user: LoginUser,request: Request=None, db: Session = Depends(get_db)):
    print("HELLO ", user.email)
    request.session.pop("user_email_with_google", None)
    request.session.pop("user_name_with_google", None)
    request.session.pop("user_email_with_github", None)
    request.session.pop("user_name_with_github", None)
    request.session["user_email"] = user.email
    print(user.email)
    print(user.password)
    mail = get_user_by_email(db, email=user.email)
    print(mail)
    if not mail:
        raise HTTPException(status_code=404, detail="User not found")

    verify=verify_password(user.password,mail.password)
    if not verify:
        raise HTTPException(status_code=401, detail="Incorrect password")
    return {"message": "Login Successfully!"}



#dummy verification
# @app.post("/verification", response_class=HTMLResponse)
# def verify_code(request: Request, backgroundtask: BackgroundTasks, vcode1: str = Form(...),
#                 db: Session = Depends(get_db)):
#     email = get_email.get("email")
#     first_name = get_email.get("f_name")
#     last_name = get_email.get("l_name")
#     password = get_email.get("password")
#     newpassword = get_email_forget.get("newpassword")
#     password1 = get_email_forget.get("password")
#     email2 = get_email_forget.get("email")
#     print(email)
#     print("mail", email, "fname", first_name, "lname", last_name, "password", password)
#     print(f"Verification code received: {vcode1}")
#     vcode2 = int(vcode1)
#     verification_code2 = int(verification_code)
#     if newpassword:
#         if verification_code2 == vcode2:
#             user = db.query(Register_With_Email).filter(
#                 Register_With_Email.email == email2).first()  # Fetch the user instance
#             if user:
#                 user.password = newpassword
#                 db.commit()
#                 db.refresh(user)
#                 message2 = True
#             else:
#                 message2 = False
#         else:
#             message3 = True
#             return templates.TemplateResponse("verification.html", {"request": request, "message3": message3})
#         return templates.TemplateResponse("verification.html", {"request": request, "message2": message2})
#     if verification_code2 == vcode2:
#         print("account created")
#         message = True
#         create_user(db=db, email=email, first_name=first_name, last_name=last_name, password=password)
#     return templates.TemplateResponse("verification.html", {"request": request, "message": message})





@app.post("/verification", response_class=HTMLResponse)
def verify_code(request: Request, backgroundtask: BackgroundTasks, vcode1: str = Form(...),
                db: Session = Depends(get_db)):
    email = get_email.get("email")
    first_name = get_email.get("f_name")
    last_name = get_email.get("l_name")
    password = get_email.get("password")
    newpassword = get_email_forget.get("newpassword")
    password1 = get_email_forget.get("password")
    email2 = get_email_forget.get("email")
    print(email)
    print("mail", email, "fname", first_name, "lname", last_name, "password", password)
    print(f"Verification code received: {vcode1}")
    vcode2 = int(vcode1)
    verification_code2 = int(verification_code)
    if newpassword:
        if verification_code2 == vcode2:
            user = db.query(Register_With_Email).filter(
                Register_With_Email.email == email2).first()  # Fetch the user instance
            if user:
                user.password = newpassword
                db.commit()
                db.refresh(user)
            else:
                raise HTTPException(status_code=404, detail="User not found")
        else:
            return {
                "status": 400,
                "message": "Incorrect Verification Code."
            }
        return {
        "status": 204,
        "message": "Password Updated Successfully."
        }
    if verification_code2 == vcode2:
        print("account created")
        create_user(db=db, email=email, first_name=first_name, last_name=last_name, password=password)
    return {
                "status": 200,
                "message": "Account Created."
            }


if __name__=="__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)