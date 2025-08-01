from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def get_cors_middleware(app: FastAPI):
    allowed_origins = [
        "https://amin-travels-hajj-frontend.vercel.app",  # ✅ Actual deployed frontend
        "http://localhost:3000",  # ✅ For local development
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,           # ❌ DO NOT use ["*"]
        allow_credentials=True,                  # ✅ Safe now
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],  # ❌ Don't use ["*"] here if credentials used
    )
