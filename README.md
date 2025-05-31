##cHome Price Predictor App running on Browser and Physical device


## 📦How to connect Flutter frontend with FastAPI backend and run in a physical device
# 📱 Home Price Prediction App (Flutter + FastAPI)

This project is a mobile-based home price prediction system using a **Flutter frontend** and a **FastAPI backend**. The app allows users to log in, input property details, and receive a predicted price for the home.

---

## 🚀 Features

- 🔐 User authentication (Login/Signup)
- 🧠 Predict house prices using trained ML models
- 📋 Form-based UI for entering property details
- 📱 Works on physical mobile devices
- 🌐 Communicates with FastAPI backend via local Wi-Fi network

---

## 🧰 Tech Stack

- **Frontend:** Flutter (Dart)
- **Backend:** FastAPI (Python)
- **ML Model:** Trained with Scikit-learn / Pandas
- **Deployment:** Localhost (for development)

---



step 1
Start FastAPI server to listen on all devices in the network
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

step 2
Find Your Computer's Local IP Address
IPv4 Address e.g: 192.168.1.100

step 3
Update Flutter App to Use Backend IP
final String baseUrl = 'http://192.168.1.100:8000'; // Replace localhost with your IP

step 4

Enable CORS in FastAPI
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["use your ip here "],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

step 5
Allow FastAPI Port Through Windows Firewall (Important for Access from Phone)
Press Windows + R → type wf.msc → press Enter

Go to Inbound Rules → click New Rule...

Select Port → click Next

Choose TCP, and enter port 8000 → click Next

Choose Allow the connection → click Next

Select all profiles (Domain, Private, Public) → click Next

Name it (e.g., FastAPI 8000) → click Finish

Now your FastAPI server can receive requests from other devices on the network.

step 6
make sure both laptop and mobile using same wifi internet
Run Flutter App on Your Phone
flutter run

step 7
Test Backend from Phone
http://192.168.1.100:8000/docs


## Thanks
 




