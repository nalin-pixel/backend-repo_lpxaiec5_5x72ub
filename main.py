import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from database import create_document
from schemas import Lead as LeadSchema

app = FastAPI(title="SPEED OF MASTRY API", description="Public API powering the SPEED OF MASTRY website")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LeadIn(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    message: Optional[str] = None
    country: Optional[str] = None


@app.get("/")
def read_root():
    return {
        "name": "SPEED OF MASTRY",
        "tagline": "Building high-performance technology for the Gulf.",
        "region": "Gulf Cooperation Council",
        "hq": "Saudi Arabia",
    }


@app.get("/api/company")
def company_info():
    return {
        "name": "SPEED OF MASTRY",
        "headline": "The leading technology partner across the Gulf and Saudi Arabia",
        "subheadline": "From strategy to delivery, we engineer scalable platforms, cloud-native systems, and AI solutions that power regional leaders.",
        "stats": [
            {"label": "Projects Delivered", "value": "+120"},
            {"label": "Enterprise Uptime", "value": "99.99%"},
            {"label": "Avg. Launch Time", "value": "8 weeks"},
        ],
        "awards": [
            "Top Technology Innovator – KSA",
            "Best Cloud Modernization Partner – GCC",
        ],
    }


@app.get("/api/services")
def services() -> List[dict]:
    return [
        {
            "title": "Custom Software",
            "desc": "High-performance web and mobile applications tailored to your business.",
            "bullets": ["Product engineering", "Microservices", "API platforms"],
        },
        {
            "title": "Cloud & DevOps",
            "desc": "Secure, scalable cloud on AWS, Azure, and GCP with modern DevOps.",
            "bullets": ["Kubernetes", "CI/CD", "Observability"],
        },
        {
            "title": "AI & Data",
            "desc": "Applied AI, analytics, and data platforms for real impact.",
            "bullets": ["LLM apps", "MLOps", "Data lakes"],
        },
        {
            "title": "Digital Transformation",
            "desc": "From legacy to modern, accelerate delivery across the enterprise.",
            "bullets": ["Cloud migration", "ERP integrations", "Governance"],
        },
    ]


@app.post("/api/leads")
def create_lead(lead: LeadIn):
    try:
        # Validate against schema and insert
        lead_doc = LeadSchema(**lead.model_dump())
        inserted_id = create_document("lead", lead_doc)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
