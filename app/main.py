from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text

from app.database import Base, engine
from app.models import user, department, student, school, clearance_units, clearance_record, clearance_request, officer_assignment, clearance_requirement,clearance_document, clearance_payment
from app.routes.auth import router as auth_router
from app.routes.student import router as students_router
from app.routes.clearance import router as clearance_router
from app.routes.officer import router as officer_router
from app.routes.clearance_upload import router as clearance_upload_router
from app.routes.admin import router as admin_router
from app.routes.departments import router as departments_router 
     
app = FastAPI()

app.include_router(auth_router)
app.include_router(students_router)
app.include_router(clearance_router)
app.include_router(officer_router)
app.include_router(clearance_upload_router)
app.include_router(admin_router)
app.include_router(departments_router)  
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get('/')
def home():
    return{
        "message":"Digital Clearance System"
    }

