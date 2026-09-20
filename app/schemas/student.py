from pydantic import BaseModel, ConfigDict

class StudentCreate(BaseModel):
    matric_number: str
    full_name: str
    department_id: int
    level: str
    graduation_session: str

class StudentResponse(BaseModel):
    id: int
    user_id:int
    matric_number: str
    full_name: str
    department_id:int
    level: str
    graduation_session: str
    model_config = ConfigDict(from_attributes=True)
