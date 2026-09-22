from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.student import Student
from app.models.clearance_units import ClearanceUnit
from datetime import datetime, timezone
from app.models.clearance_request import ClearanceRequest
from app.models.clearance_record import ClearanceRecord
from app.models.clearance_document import ClearanceDocument
from app.models.clearance_requirement import ClearanceRequirement
from app.models.clearance_document import ClearanceDocument
from decimal import Decimal
from app.models.clearance_payment import ClearancePayment


def clearance_application(db: Session, current_user: User):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )
    existing_application = db.query(ClearanceRequest).filter(
        ClearanceRequest.student_id == student.id,
        ClearanceRequest.status.in_(["pending", "in_progress"])
        ).first()
    if existing_application:
        raise HTTPException(
            status_code=400,
            detail="You already have an active clearance application"
        )

    clearance_units = db.query(ClearanceUnit).filter(ClearanceUnit.is_active == True).order_by(ClearanceUnit.id).all()
    if not clearance_units:
        raise HTTPException(
            status_code=404,
            detail="No active clearance unit available"
        )
    clearance_request = ClearanceRequest(
        student_id = student.id,
        status="pending",
        submitted_at= datetime.now(timezone.utc)
    )
    db.add(clearance_request)
    db.flush()

    for unit in clearance_units:
        record = ClearanceRecord(
            clearance_request_id=clearance_request.id,
            clearance_unit_id = unit.id,
            status="pending"

        )
        db.add(record)
    db.commit()
    db.refresh(clearance_request)
    return clearance_request


def get_clearance_info(db:Session, current_user: User):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )
    clearance = db.query(ClearanceRequest).filter(ClearanceRequest.student_id == student.id).order_by(ClearanceRequest.id.desc()).first()
    if not clearance:
        raise HTTPException(
            status_code= 404,
            detail="No clearance application found"
        )
    
    records = (
        db.query(ClearanceRecord)
        .filter(
            ClearanceRecord.clearance_request_id ==
            clearance.id
        )
        .order_by(ClearanceRecord.id)
        .all()
    )

    approved = sum(
        1 for record in records
        if record.status == "approved"
    )

    pending = sum(
        1 for record in records
        if record.status == "pending"
    )

    rejected = sum(
        1 for record in records
        if record.status == "rejected"
    )

    units = []

    for record in records:
        units.append({
            "record_id": record.id,
            "unit_id": record.clearance_unit_id,
            "unit_name": record.clearance_unit.name,
            "unit_code": record.clearance_unit.code,
            "status": record.status,
            "student_response": record.student_response,
            "amount_owed": record.amount_owed,
            "reason": record.reason,
            "remark": record.remark,
            "approved_at": record.approved_at
        })

    return {
        "clearance_id": clearance.id,
        "overall_status": clearance.status,
        "student_name": student.full_name,
        "matric_number": student.matric_number,
        "total_units": len(records),
        "approved": approved,
        "pending": pending,
        "rejected": rejected,
        "units": units
    }


def get_clearance_record(db: Session, record_id: int, current_user: User):
    record = (db.query(ClearanceRecord)
              .filter(ClearanceRecord.id == record_id)
              .first()
              )
    if not record:
        raise HTTPException(
            status_code=404,
            detail="Clearance record not found"
        )
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )
    if record.clearance_request.student_id != student.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this clearance record"
        )
    requirements = (
        db.query(ClearanceRequirement)
        .filter(
            ClearanceRequirement.clearance_unit_id == record.clearance_unit_id,
            ClearanceRequirement.is_required == True,
            ClearanceRequirement.is_active == True
        )
        .all()
    )
    result = []
    for requirement in requirements:
        documents = (
            db.query(ClearanceDocument)
            .filter(
                ClearanceDocument.requirement_id == requirement.id,
                ClearanceDocument.clearance_record_id == record.id
            )
            .all()
        )
        payments = (
            db.query(ClearancePayment)
            .filter(
                ClearancePayment.clearance_record_id == record.id,
                ClearancePayment.requirement_id == requirement.id
            )
            .all()
        )
        result.append({
            "id": requirement.id,
            "name": requirement.name,
            "description": requirement.description,
            "requirement_type": requirement.requirement_type,
            "expected_amount": requirement.expected_amount,
            "is_required": requirement.is_required,
            "documents": [
                {
                    "id": document.id,
                    "file_name": document.file_name,
                    "verification_status": document.verification_status,
                    "verification_remark": document.verification_remark,
                    "uploaded_at": document.uploaded_at
                }
                for document in documents
            ],
            "payments": [
                {
                    "id": payment.id,
                    "amount": payment.amount,
                    "verification_status": payment.verification_status,
                    "verification_remark": payment.verification_remark,
                }
                for payment in payments
            ]
        })
    return {
        "record_id": record.id,
        "unit_id": record.clearance_unit_id,
        "unit_name": record.clearance_unit.name,
        "status": record.status,
        "student_response": record.student_response,
        "amount_owed": record.amount_owed,
        "remark": record.remark,
        "approved_at": record.approved_at,
        "requirements": result
    }

def get_my_documents(db:Session, current_user: User):

    documents = (
        db.query(ClearanceDocument)
        .join(ClearanceRecord)
        .join(ClearanceRequest)
        .join(ClearanceRequirement)
        .filter(
            ClearanceRequest.student.has(
                user_id=current_user.id
            )
        )
        .all()
    )

    result = []

    for document in documents:
        requirement = (
            db.query(ClearanceRequirement)
            .filter(
                ClearanceRequirement.id == document.requirement_id
            )
            .first()
        )

        result.append({
            "id": document.id,
            "requirement_id": document.requirement_id,
            "requirement_name": requirement.name,
            "file_name": document.file_name,
            "verification_status": document.verification_status,
            "verification_remark": document.verification_remark,
            "uploaded_at": document.uploaded_at
        })

    return result



def update_clearance_unit_status(
    db: Session,
    clearance_record: ClearanceRecord
):
    requirements = (
        db.query(ClearanceRequirement)
        .filter(
            ClearanceRequirement.clearance_unit_id
            == clearance_record.clearance_unit_id,
            ClearanceRequirement.is_required == True,
            ClearanceRequirement.is_active == True
        )
        .all()
    )

    # No requirements means this unit is handled
    # directly by the officer.
    if not requirements:
        return

    for requirement in requirements:

        # -----------------------------------------
        # DOCUMENT REQUIREMENT
        # -----------------------------------------
        if requirement.requirement_type == "document":

            documents = (
                db.query(ClearanceDocument)
                .filter(
                    ClearanceDocument.clearance_record_id
                    == clearance_record.id,
                    ClearanceDocument.requirement_id
                    == requirement.id
                )
                .order_by(
                    ClearanceDocument.uploaded_at.desc()
                )
                .all()
            )

            # No document uploaded
            if not documents:
                clearance_record.status = "pending"
                return

            # Look for an approved document
            approved_document = next(
                (
                    document
                    for document in documents
                    if document.verification_status == "approved"
                ),
                None
            )

            if approved_document:
                continue

            # Latest document was rejected
            latest_document = documents[0]

            if latest_document.verification_status == "rejected":
                clearance_record.status = "rejected"
                return

            # Still waiting for officer verification
            clearance_record.status = "pending"
            return

        # -----------------------------------------
        # PAYMENT REQUIREMENT
        # -----------------------------------------
        elif requirement.requirement_type == "payment":

            payments = (
                db.query(ClearancePayment)
                .filter(
                    ClearancePayment.clearance_record_id
                    == clearance_record.id,
                    ClearancePayment.requirement_id
                    == requirement.id
                )
                .all()
            )

            # No payment receipt uploaded
            if not payments:
                clearance_record.status = "pending"
                return

            approved_amount = sum(
                (
                    payment.amount
                    for payment in payments
                    if payment.verification_status == "approved"
                ),
                Decimal("0")
            )

            expected_amount = requirement.expected_amount

            # If an expected amount has not been configured,
            # don't automatically approve the requirement.
            if expected_amount is None:
                clearance_record.status = "pending"
                return

            # Fully paid
            if approved_amount >= expected_amount:
                continue

            # Not fully paid yet
            clearance_record.status = "pending"
            return

    # Every required document and payment requirement
    # has been satisfied.
    clearance_record.status = "approved"


def update_overall_clearance_status(db: Session, clearance_request):
    records = (
        db.query(ClearanceRecord)
        .filter(
            ClearanceRecord.clearance_request_id == clearance_request.id
        )
        .all()
    )

    total_units = len(records)

    approved = sum(
        1 for record in records
        if record.status == "approved"
    )

    rejected = sum(
        1 for record in records
        if record.status == "rejected"
    )

    if rejected > 0:
        clearance_request.status = "rejected"

    elif total_units > 0 and approved == total_units:
        clearance_request.status = "completed"

    elif approved > 0:
        clearance_request.status = "in_progress"

    else:
        clearance_request.status = "pending"

