from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.clearance_payment import ClearancePayment
from app.models.clearance_record import ClearanceRecord
from app.models.clearance_request import ClearanceRequest
from app.models.clearance_requirement import ClearanceRequirement
from app.models.user import User


def get_school_fee_summary(
    db: Session,
    current_user: User,
    clearance_record_id: int
):
    # Make sure this clearance belongs to the logged-in student
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

    # Get school-fee payment requirements for this financial unit
    requirements = (
        db.query(ClearanceRequirement)
        .filter(
            ClearanceRequirement.clearance_unit_id
            == record.clearance_unit_id,
            ClearanceRequirement.requirement_type == "payment",
            ClearanceRequirement.is_active == True
        )
        .all()
    )

    result = []

    for requirement in requirements:

        payments = (
            db.query(ClearancePayment)
            .filter(
                ClearancePayment.clearance_record_id == record.id,
                ClearancePayment.requirement_id == requirement.id
            )
            .all()
        )

        approved_amount = sum(
            (
                payment.amount
                for payment in payments
                if payment.verification_status == "approved"
            ),
            Decimal("0")
        )

        pending_amount = sum(
            (
                payment.amount
                for payment in payments
                if payment.verification_status == "pending"
            ),
            Decimal("0")
        )

        rejected_amount = sum(
            (
                payment.amount
                for payment in payments
                if payment.verification_status == "rejected"
            ),
            Decimal("0")
        )

        expected_amount = requirement.expected_amount

        if expected_amount is not None:
            balance = max(
                expected_amount - approved_amount,
                Decimal("0")
            )

            if approved_amount >= expected_amount:
                payment_status = "paid"
            elif approved_amount > 0:
                payment_status = "partially_paid"
            elif pending_amount > 0:
                payment_status = "pending"
            else:
                payment_status = "not_paid"
        else:
            balance = None

            if approved_amount > 0:
                payment_status = "paid"
            elif pending_amount > 0:
                payment_status = "pending"
            else:
                payment_status = "not_paid"

        result.append({
            "requirement_id": requirement.id,
            "requirement_name": requirement.name,
            "expected_amount": expected_amount,
            "approved_amount": approved_amount,
            "pending_amount": pending_amount,
            "rejected_amount": rejected_amount,
            "balance": balance,
            "receipt_count": len(payments),
            "status": payment_status
        })

    return result