
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.school import School

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

    # School is required for School Clearance
    if data.clearance_unit_id == 2:

        if data.school_id is None:
            raise HTTPException(
                status_code=400,
                detail="School is required for School Clearance assignment."
            )

        school = (
            db.query(School)
            .filter(
                School.id == data.school_id,
                School.is_active == True
            )
            .first()
        )

        if not school:
            raise HTTPException(
                status_code=404,
                detail="School not found."
            )

    else:
        # Other clearance units should not have a school
        data.school_id = None

    # Check for existing assignment
    assignment_query = (
        db.query(OfficerAssignment)
        .filter(
            OfficerAssignment.user_id == data.user_id,
            OfficerAssignment.clearance_unit_id == data.clearance_unit_id
        )
    )

    if data.school_id is None:
        assignment_query = assignment_query.filter(
            OfficerAssignment.school_id.is_(None)
        )
    else:
        assignment_query = assignment_query.filter(
            OfficerAssignment.school_id == data.school_id
        )

    existing_assignment = assignment_query.first()


    if existing_assignment:
        raise HTTPException(
            status_code=400,
            detail="Officer is already assigned to this clearance unit."
        )

    # Create assignment
    assignment = OfficerAssignment(
        user_id=data.user_id,
        clearance_unit_id=data.clearance_unit_id,
        school_id=data.school_id
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return assignment