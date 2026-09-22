from pydantic import BaseModel, ConfigDict


class OfficerAssignmentCreate(BaseModel):
    user_id: int
    clearance_unit_id: int
    school_id: int | None = None


class OfficerAssignmentResponse(BaseModel):
    id: int
    user_id: int
    clearance_unit_id: int
    model_config = ConfigDict(from_attributes=True) 