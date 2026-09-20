from pathlib import Path
import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.clearance_payment import ClearancePayment
from app.models.clearance_record import ClearanceRecord
from app.models.clearance_request import ClearanceRequest
from app.models.clearance_requirement import ClearanceRequirement
from app.models.user import User


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
}

MAX_FILE_SIZE = 5 * 1024 * 1024


def validate_payment_file(file: UploadFile):
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed. Upload PDF, JPG, JPEG or PNG."
        )

    return extension


def save_payment_file(
    file: UploadFile,
    extension: str
):
    upload_dir = Path("uploads/payments")
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_filename = f"{uuid.uuid4().hex}{extension}"
    file_path = upload_dir / safe_filename

    file.file.seek(0)

    file_size = 0

    with open(file_path, "wb") as buffer:
        while chunk := file.file.read(1024 * 1024):
            file_size += len(chunk)

            if file_size > MAX_FILE_SIZE:
                file_path.unlink(missing_ok=True)

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File size exceeds the maximum limit of 5MB."
                )

            buffer.write(chunk)

    return str(file_path), safe_filename


def upload_school_fee_payment(
    db: Session,
    current_user: User,
    clearance_record_id: int,
    requirement_id: int,
    amount: float,
    file: UploadFile 
):
    # Find student's clearance record
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

    # Find the requirement
    requirement = (
        db.query(ClearanceRequirement)
        .filter(
            ClearanceRequirement.id == requirement_id,
            ClearanceRequirement.clearance_unit_id
            == record.clearance_unit_id,

            
            ClearanceRequirement.is_active == True
        )
        .first()
    )

    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment requirement not found."
        )

    # Make sure this is actually a payment requirement
    if requirement.requirement_type != "payment":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This requirement is not a payment requirement."
        )

    # Amount must be greater than zero
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must be greater than zero."
        )

    extension = validate_payment_file(file)

    file_path, safe_filename = save_payment_file(
        file,
        extension
    )

    payment = ClearancePayment(
        clearance_record_id=record.id,
        requirement_id=requirement.id,
        amount=amount,
        receipt_file_name=file.filename,
        receipt_file_path=file_path,
        verification_status="pending"
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "message": "School fee payment uploaded successfully.",
        "payment_id": payment.id,
        "requirement": requirement.name,
        "amount": float(payment.amount),
        "receipt_file_name": payment.receipt_file_name,
        "verification_status": payment.verification_status
    }