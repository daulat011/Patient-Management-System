from pydantic import BaseModel, Field


class Patient(BaseModel):
    #basic patient information and validation rules
    id: str
    name: str
    city: str

    #age must be bet 0 and 120
    age: int = Field(..., ge=0, le=120)     #... - means, field is required
    gender: str

    #both are must be greater than 0
    height: float = Field(..., gt=0)
    weight: float = Field(..., gt=0)

class PatientResponse(Patient):
    bmi: float
    health_verdict: str

class DeletePatientResponse(BaseModel):
    message: str
    deleted_patient: PatientResponse