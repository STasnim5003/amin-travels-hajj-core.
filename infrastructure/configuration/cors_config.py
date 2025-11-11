from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def get_cors_middleware(app: FastAPI):
    allowed_origins = [
        "https://amin-travels-hajj-frontend.vercel.app",
        "http://localhost:3001",
        "http://localhost:3000",
        "https://devusion.io",
        "https://amintravels.com.bd",
        "https://www.amintravels.com.bd",
        "http://192.168.1.40:3000",
        "http://205.147.200.78:3004",  # staging frontend
        "http://127.0.2.2:3000",
        "https://dev.amintravels.com.bd"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],  # ❌ Don't use ["*"] here if credentials used
    )
