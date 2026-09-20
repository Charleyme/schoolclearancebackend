from fastapi import HTTPException, File, UploadFile, status
from sqlalchemy.orm import Session
from app.schemas.student import StudentResponse, StudentCreate
from app.models.user import User
from app.models.student import Student
from app.models.clearance_requirement import ClearanceRequirement
from app.models.clearance_document import ClearanceDocument
from app.models.clearance_units import ClearanceUnit
from datetime import datetime, timedelta, timezone
from app.models.clearance_request import ClearanceRequest
from app.models.clearance_record import ClearanceRecord
import os
import uuid
from pathlib import Path

BASE_UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".docx"
}
MAX_FILE_SIZE = 5 * 1024 * 1024

def validate_file(file: UploadFile):
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code= 400,
            detail= "File type not allowed. Upload PDF, JPG, JPEG or PNG"
        )
    return extension
def save_upload_file(file: UploadFile, folder: str, extension: str):
    upload_dir = BASE_UPLOAD_DIR / folder
    upload_dir.mkdir(parents = True, exist_ok = True)
    safe_filename = f"{uuid.uuid4().hex}{extension}"
    file_path = upload_dir / safe_filename
    file.file.seek(0)
    file_size = 0
    with open(file_path, "wb") as buffer:
        while chunk := file.file.read(1024 * 1024):
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code= 400,
                    detail= "File size exceeds the maximum limit of 5MB"
                )
            buffer.write(chunk)
    return str(file_path), safe_filename


def upload_document(
    db: Session,
    current_user: User,
    clearance_record_id: int,
    requirement_id: int,
    file: UploadFile

    ):
    # Get clearance record
    record = (
        db.query(ClearanceRecord)
        .join(ClearanceRequest)
        .filter(
            ClearanceRecord.id == clearance_record_id,
            ClearanceRequest.student.has(
                user_id=current_user.id
            )
        )
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clearance record not found."
        )

    # Get requirement
    requirement = (
        db.query(ClearanceRequirement)
        .filter(
            ClearanceRequirement.id == requirement_id,
            ClearanceRequirement.clearance_unit_id == record.clearance_unit_id,
            ClearanceRequirement.is_active == True
        )
        .first()
    )

    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found for this clearance unit."
        )

    # Make sure this is a document requirement
    if requirement.requirement_type != "document":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This requirement requires a payment receipt."
        )

    extension = validate_file(file)

    file_path, safe_filename = save_upload_file(
        file,
        "documents",
        extension
    )

    document = ClearanceDocument(
        clearance_record_id=clearance_record_id,
        requirement_id=requirement_id,
        file_name=file.filename,
        file_path=file_path,
        verification_status="pending"
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "message": "Document uploaded successfully.",
        "document_id": document.id,
        "requirement": requirement.name,
        "file_name": document.file_name,
        "verification_status": document.verification_status
    }