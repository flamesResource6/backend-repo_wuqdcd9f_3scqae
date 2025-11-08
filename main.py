import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
from database import create_document
from schemas import Lead

app = FastAPI(title="Nocode Saarthi API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Nocode Saarthi Backend Running"}

class LeadIn(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    description: str
    branding: Optional[str] = 'No'
    service: Optional[str] = None

@app.post("/leads")
def create_lead(payload: LeadIn):
    try:
        # store in DB
        doc_id = create_document('lead', payload.dict())
        # attempt email notification (no-op if not configured)
        try:
            import smtplib
            from email.mime.text import MIMEText

            to_email = "shivageethikarao2007@gmail.com"
            subject = "New Lead - Nocode Saarthi"
            body = (
                f"Service: {payload.service or 'General Inquiry'}\n"
                f"Name: {payload.name}\n"
                f"Email: {payload.email}\n"
                f"Phone: {payload.phone or '-'}\n\n"
                f"Description:\n{payload.description}\n\n"
            )
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = os.getenv('NOTIFY_FROM_EMAIL', 'no-reply@nocodesaarthi.com')
            msg['To'] = to_email

            smtp_host = os.getenv('SMTP_HOST')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER')
            smtp_pass = os.getenv('SMTP_PASS')

            if smtp_host and smtp_user and smtp_pass:
                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
        except Exception:
            # Silent fail for email in sandbox
            pass

        return {"status": "ok", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    """Test endpoint to check database connectivity"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
    }
    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Connected"
            response["collections"] = db.list_collection_names()
        else:
            response["database"] = "❌ Not Configured"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
