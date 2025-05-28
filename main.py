from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
import pandas as pd
from models import get_user_by_email, get_user_by_email_google, get_user_by_github, create_user_with_github, \
    create_user_with_google, create_user
from models import UserCreate, LoginUser, Register_With_Email, PredictHouse, Forget,PasswordUpdate
from auth import send_verification_code
from models import app, SessionLocal
import uvicorn
from fastapi import FastAPI, Form, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
import random
import joblib


from starlette.middleware.sessions import SessionMiddleware



app.add_middleware(SessionMiddleware, secret_key="Home_Price_App")  # keep this consistent



model, feature_names = joblib.load("home_price_model.pkl")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
get_email = {}
get_email_forget = {}
data = {}


def v_code():
    return random.randint(100000, 999999)


verification_code = v_code()


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
def reg_user(user: UserCreate, backgroundtask: BackgroundTasks, db: Session = Depends(get_db), request: Request = None):
    get_email["f_name"] = user.first_name
    get_email["l_name"] = user.last_name
    get_email["email"] = user.email
    hashed_passowrd = hash_password(user.password)
    get_email["password"] = hashed_passowrd
    print("Hello", user)
    existing_user = get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="User already registered with this email.")

    backgroundtask.add_task(send_verification_code, user.email, verification_code)
    return {
        "status": 200,
        "message": "Account Created ."
    }


@app.post("/login")
def login_user(user: LoginUser, request: Request = None, db: Session = Depends(get_db)):

    request.session["user_email"] = user.email
    mail = get_user_by_email(db, email=user.email)
    print(request.session["user_email"])
    if not mail:
        raise HTTPException(status_code=404, detail="User not found")

    verify = verify_password(user.password, mail.password)
    if not verify:
        raise HTTPException(status_code=401, detail="Incorrect password")
    return {"message": "Login Successfully!"}


@app.post("/verification")
async def verify_code(request: Request = None,
                      db: Session = Depends(get_db)):
    vcode = await request.body()
    vcode1 = vcode.decode("utf-8")
    print(vcode1)
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
                return {
                    "status": 20,
                    "message": "Password Updated Successfully."
                }
            else:
                return {
                    "status": 404,
                    "message": "Password Not Updated Successfully. Try Again User not Exist"
                }
        else:
            return {
                "status": 204,
                "message": "INVALID CODE."
            }
    if verification_code2 == vcode2:
        print("account created")
        create_user(db=db, email=email, first_name=first_name, last_name=last_name, password=password)
        return {
            "status": 200,
            "message": "Account Created."
        }
    else:
        return {
            "status": 205,
            "message": "Invalid Code."
        }


@app.post("/forget")
def gen_response(Pass: Forget, backgroundtask: BackgroundTasks, request: Request = None):
    print(Pass.email, Pass.password, Pass.cpassword)
    backgroundtask.add_task(send_verification_code, Pass.email, verification_code)
    get_email_forget["email"] = Pass.email
    get_email_forget["newpassword"] = hash_password(Pass.password)
    # return RedirectResponse(url="/verification", status_code=303)



@app.post("/predict")
def get_form_data1(Predict: PredictHouse,request: Request):
    print("hello predict", Predict.Purpose)
    data["TYPE"] = Predict.home
    data["AREA"] = Predict.Size
    data["PURPOSE"] = Predict.Purpose
    data["LOCATION"] = Predict.Location
    data["BUILD IN YEAR"] = Predict.Built_in_Year
    data["BEDROOMS"] = Predict.Bedrooms
    data["BATHROOMS"] = Predict.Washrooms
    data["PARKING SPACES"] = Predict.Parking
    new_data = pd.DataFrame([data])
    print(new_data)
    print(data)
    predicted_price = model.predict(new_data)

    print(predicted_price)
    return {"status":200,"estimated_price":float(predicted_price[0])}


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return {"status": 200,
            "User":"Logged Out"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
