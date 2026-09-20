from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.student import StudentResponse, StudentCreate
from app.models.user import User
from app.models.student import Student
from app.models.department import Department
from app.models.clearance_units import ClearanceUnit
from app.models.officer_assignment import OfficerAssignment
from app.models.clearance_record import ClearanceRecord
from datetime import datetime, timezone
from app.schemas.officer import ClearanceDecision
from app.models.clearance_request import ClearanceRequest
from app.models.clearance_requirement import ClearanceRequirement
from app.models.clearance_document import ClearanceDocument
from app.schemas.document_verification import DocumentVerificationRequest
from app.schemas.payment_verification import PaymentVerificationRequest
from app.services.clearance import update_clearance_unit_status, update_overall_clearance_status
from app.models.clearance_payment import ClearancePayment

def update_clearance_status(db: Session, clearance_request_id: int):
    clearance_request = db.query(ClearanceRequest).filter(ClearanceRequest.id == clearance_request_id).first()
    if not clearance_request:
        return 
    records = (
        db.query(ClearanceRecord)
        .filter(ClearanceRecord.clearance_request_id == clearance_request_id).all()
    )
    if not records:
        return
    if all(record.status == "approved" for record in records):
        clearance_request.status = "completed"
    elif any(record.status == "rejected" for record in records):
        clearance_request.status = "rejected"
    else:
        clearance_request.status = "in_progress"
    db.commit()

def get_pending_clearances(db:Session, current_user: User):
    query = (
        db.query(
            ClearanceRecord.id.label("record_id"),
            ClearanceRecord.status,
            ClearanceRecord.created_at,
            ClearanceRequest.id.label("clearance_request_id"),
            ClearanceRequest.submitted_at,
            Student.full_name,
            Student.matric_number,
            Department.name.label("department"),
            ClearanceUnit.name.label("clearance_unit")
        )
        .join(
            ClearanceRequest,
            ClearanceRecord.clearance_request_id ==
            ClearanceRequest.id
        )
        .join(
            Student,
            ClearanceRequest.student_id ==
            Student.id
        )
        .join(
            Department,
            Student.department_id ==
            Department.id
        )
        .join(
            ClearanceUnit,
            ClearanceRecord.clearance_unit_id ==
            ClearanceUnit.id
        )
        .filter(
            ClearanceRecord.status == "pending"
        )
    )

    # Officers only see their assigned units
    if current_user == "officer":

        assignments = (
            db.query(OfficerAssignment)
            .filter(
                OfficerAssignment.user_id ==
                current_user.id
            )
            .all()
        )

        unit_ids = [
            assignment.clearance_unit_id
            for assignment in assignments
        ]

        query = query.filter(
            ClearanceRecord.clearance_unit_id.in_(unit_ids)
        )

    records = query.order_by(
        ClearanceRecord.created_at.asc()
    ).all()

    return [
        {
            "record_id": record.record_id,
            "clearance_request_id": record.clearance_request_id,
            "student_name": record.full_name,
            "matric_number": record.matric_number,
            "department": record.department,
            "clearance_unit": record.clearance_unit,
            "status": record.status,
            "submitted_at": record.submitted_at
        }
        for record in records
    ]

def approve_clearance(
    db: Session,
    record_id: int,
    decision: ClearanceDecision,
    current_user: User
):
    record = (
        db.query(ClearanceRecord)
        .filter(ClearanceRecord.id == record_id)
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Clearance Record not found"
        )

    # Check officer assignment
    if current_user.role == "officer":
        assignment = (
            db.query(OfficerAssignment)
            .filter(
                OfficerAssignment.user_id == current_user.id,
                OfficerAssignment.clearance_unit_id == record.clearance_unit_id
            )
            .first()
        )

        if not assignment:
            raise HTTPException(
                status_code=403,
                detail="You are not assigned to this clearance unit"
            )

    # Validate decision
    if decision.status not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be approved or rejected"
        )

    # School Clearance rule
    if record.clearance_unit_id == 2 and current_user.role == "officer":

       student = (
         db.query(Student)
         .filter(Student.id == record.clearance_request.student_id)
         .first()
       )

       if not student:
            raise HTTPException(
            status_code=404,
            detail="Student not found"
            )
       department = (
        db.query(Department)
        .filter(Department.id == student.department_id)
        .first()
       )

       if not department or not department.school_id:
          raise HTTPException(
            status_code=400,
            detail="Student is not assigned to a school"
          )

       school_assignment = (
          db.query(OfficerAssignment)
          .filter(
            OfficerAssignment.user_id == current_user.id,
            OfficerAssignment.clearance_unit_id == 2,
            OfficerAssignment.school_id == department.school_id
          )
          .first()
        )

       if not school_assignment:
           raise HTTPException(
            status_code=403,
            detail="You are not assigned to this student's school"
        )
    # Department Clearance rule
    if record.clearance_unit_id == 1 and decision.status == "approved":
        if decision.amount_owed is not None and decision.amount_owed > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Student has an outstanding miscellaneous fee of ₦{decision.amount_owed}"
            )
    
    # Update clearance record
    record.status = decision.status
    record.amount_owed = decision.amount_owed
    record.remark = decision.remark

    if decision.status == "approved":
        record.approved_by = current_user.id
        record.approved_at = datetime.now(timezone.utc)
    else:
        record.approved_by = current_user.id
        record.approved_at = None

    # Update overall clearance status
    update_clearance_status(
        db,
        record.clearance_request_id
    )

    db.commit()
    db.refresh(record)

    return {
        "message": "Clearance updated successfully",
        "record_id": record.id,
        "status": record.status
    }

def get_clearance_record(db: Session, record_id: int, current_user: User):
    record= db.query(ClearanceRecord).filter(ClearanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=404,
            detail= "Clearance record not found"
        )
    if current_user.role == "officer":
            assignment = db.query(OfficerAssignment).filter(
                OfficerAssignment.user_id == current_user.id,
                OfficerAssignment.clearance_unit_id == record.clearance_unit_id
                ).first()
            if not assignment:
                raise HTTPException(
                  status_code=403,
                  detail="You are not assigned to this clearance unit"
            )
    clearance_request = record.clearance_request
    student = clearance_request.student
    unit = record.clearance_unit

    return {
        "record_id": record.id,
        "clearance_request_id": clearance_request.id,
        "student": {
            "id": student.id,
            "full_name": student.full_name,
            "matric_number": student.matric_number,
            "level": student.level,
            "graduation_session": student.graduation_session
        },
        "clearance_unit": {
            "id": unit.id,
            "name": unit.name,
            "code": unit.code
        },
        "status": record.status,
        "student_response": record.student_response,
        "amount_owed": record.amount_owed,
        "reason": record.reason,
        "remark": record.remark,
        "approved_by": record.approved_by,
        "approved_at": record.approved_at
    }


def get_document_for_review(
    document_id: int,
    db: Session ,
    current_user: User 
):
    document = (
        db.query(ClearanceDocument)
        .join(ClearanceRecord)
        .join(ClearanceUnit)
        .filter(
            ClearanceDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    # Check that this officer is assigned to this clearance unit
    assignment = (
        db.query(OfficerAssignment)
        .filter(
            OfficerAssignment.user_id == current_user.id,
            OfficerAssignment.clearance_unit_id ==
            document.clearance_record.clearance_unit_id
        )
        .first()
    )

    if not assignment:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned to this clearance unit."
        )

    student = document.clearance_record.clearance_request.student
    requirement = document.requirement

    return {
        "document_id": document.id,
        "student_name": student.full_name,
        "matric_number": student.matric_number,
        "clearance_unit": document.clearance_record.clearance_unit.name,
        "requirement": requirement.name,
        "file_name": document.file_name,
        "file_path": document.file_path,
        "verification_status": document.verification_status,
        "verification_remark": document.verification_remark,
        "uploaded_at": document.uploaded_at
    }

def verify_document(document_id: int, data: DocumentVerificationRequest, db: Session, current_user: User):

    document = (
        db.query(ClearanceDocument)
        .filter(ClearanceDocument.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    # Check officer assignment
    assignment = (
        db.query(OfficerAssignment)
        .filter(
            OfficerAssignment.user_id == current_user.id,
            OfficerAssignment.clearance_unit_id ==
            document.clearance_record.clearance_unit_id
        )
        .first()
    )

    if not assignment:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned to this clearance unit."
        )

    # Validate action
    if data.action not in ["approve", "reject"]:
        raise HTTPException(
            status_code=400,
            detail="Action must be either 'approve' or 'reject'."
        )

    # Rejection must have a remark
    if data.action == "reject" and not data.remark:
        raise HTTPException(
            status_code=400,
            detail="A remark is required when rejecting a document."
        )

    # Update document
    if data.action == "approve":
        document.verification_status = "approved"
        document.verification_remark = data.remark

    else:
        document.verification_status = "rejected"
        document.verification_remark = data.remark

    document.verified_by = current_user.id
    document.verified_at = datetime.now(timezone.utc)
    update_clearance_unit_status(db, clearance_record = document.clearance_record)
    update_overall_clearance_status(db, clearance_record = document.clearance_record)


    db.commit()
    db.refresh(document)

    return {
        "message": f"Document {data.action}d successfully.",
        "document_id": document.id,
        "verification_status": document.verification_status,
        "verification_remark": document.verification_remark,
        "verified_by": document.verified_by,
        "verified_at": document.verified_at
    }

def verify_payment(
    payment_id: int,
    data: PaymentVerificationRequest,
    db: Session,
    current_user: User 
):
    # Find payment
    payment = (
        db.query(ClearancePayment)
        .filter(
            ClearancePayment.id == payment_id
        )
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found."
        )

    # Make sure this is actually a payment requirement
    requirement = (
        db.query(ClearanceRequirement)
        .filter(
            ClearanceRequirement.id == payment.requirement_id
        )
        .first()
    )

    if not requirement:
        raise HTTPException(
            status_code=404,
            detail="Payment requirement not found."
        )

    if requirement.requirement_type != "payment":
        raise HTTPException(
            status_code=404,
            detail="This is not a payment requirement."
        )

    # Check officer assignment
    assignment = (
        db.query(OfficerAssignment)
        .filter(
            OfficerAssignment.user_id == current_user.id,
            OfficerAssignment.clearance_unit_id ==
            payment.clearance_record.clearance_unit_id
        )
        .first()
    )

    if not assignment:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned to this clearance unit."
        )

    # Validate action
    if data.action not in ["approve", "reject"]:
        raise HTTPException(
            status_code=400,
            detail="Action must be either 'approve' or 'reject'."
        )

    # Rejection requires a remark
    if data.action == "reject" and not data.remark:
        raise HTTPException(
            status_code=400,
            detail="A remark is required when rejecting a payment."
        )

    # Update payment
    payment.verification_status = (
        "approved"
        if data.action == "approve"
        else "rejected"
    )

    payment.verification_remark = data.remark
    payment.verified_by = current_user.id
    payment.verified_at = datetime.now(timezone.utc)
    update_clearance_unit_status(db, clearance_record=payment.clearance_record)
    update_overall_clearance_status(db,clearance_request=payment.clearance_record.clearance_request)

    db.commit()
    db.refresh(payment)

    return {
        "message": f"Payment {data.action}d successfully.",
        "payment_id": payment.id,
        "requirement": requirement.name,
        "amount": float(payment.amount),
        "verification_status": payment.verification_status,
        "verification_remark": payment.verification_remark,
        "verified_by": payment.verified_by,
        "verified_at": payment.verified_at
    }


def get_officer_payments(
    db: Session,
    current_user: User
):
    assignments = (
        db.query(OfficerAssignment)
        .filter(
            OfficerAssignment.user_id == current_user.id
        )
        .all()
    )

    if not assignments:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned to any clearance unit."
        )

    unit_ids = [
        assignment.clearance_unit_id
        for assignment in assignments
    ]

    payments = (
        db.query(ClearancePayment)
        .join(
            ClearanceRecord,
            ClearancePayment.clearance_record_id == ClearanceRecord.id
        )
        .filter(
            ClearanceRecord.clearance_unit_id.in_(unit_ids),
            ClearancePayment.verification_status == "pending"
        )
        .all()
    )

    result = []

    for payment in payments:

        record = payment.clearance_record
        request = record.clearance_request
        student = request.student

        requirement = (
            db.query(ClearanceRequirement)
            .filter(
                ClearanceRequirement.id == payment.requirement_id
            )
            .first()
        )

        result.append({
            "payment_id": payment.id,
            "clearance_record_id": record.id,
            "student_name": student.full_name,
            "matric_number": student.matric_number,
            "requirement_id": requirement.id,
            "requirement_name": requirement.name,
            "amount": float(payment.amount),
            "receipt_file_name": payment.receipt_file_name,
            "verification_status": payment.verification_status,
            "created_at": payment.created_at
        })

    return result