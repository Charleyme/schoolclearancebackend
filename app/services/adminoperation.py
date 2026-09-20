
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User

from app.models.clearance_units import ClearanceUnit


from app.schemas.officer_assigment import OfficerAssignmentCreate
from app.models.officer_assignment import OfficerAssignment

def assign_officer(
    data: OfficerAssignmentCreate,
    db: Session,
    current_user: User
):
    # Find officer
    officer = (
        db.query(User)
        .filter(User.id == data.user_id)
        .first()
    )

    if not officer:
        raise HTTPException(
            status_code=404,
            detail="Officer not found."
        )

    # Make sure the user is actually an officer
    if officer.role != "officer":
        raise HTTPException(
            status_code=400,
            detail="Selected user is not an officer."
        )

    # Find clearance unit
    clearance_unit = (
        db.query(ClearanceUnit)
        .filter(
            ClearanceUnit.id == data.clearance_unit_id,
            ClearanceUnit.is_active == True
        )
        .first()
    )

    if not clearance_unit:
        raise HTTPException(
            status_code=404,
            detail="Clearance unit not found."
        )

    # Check for existing assignment
    existing_assignment = (
        db.query(OfficerAssignment)
        .filter(
            OfficerAssignment.user_id == data.user_id,
            OfficerAssignment.clearance_unit_id
            == data.clearance_unit_id
        )
        .first()
    )

    if existing_assignment:
        raise HTTPException(
            status_code=400,
            detail="Officer is already assigned to this clearance unit."
        )

    # Create assignment
    assignment = OfficerAssignment(
        user_id=data.user_id,
        clearance_unit_id=data.clearance_unit_id
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return assignment