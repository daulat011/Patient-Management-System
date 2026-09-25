from fastapi import FastAPI, HTTPException, status, Query
from models import Patient, DeletePatientResponse, PatientResponse
import json


app = FastAPI(
    title="Patient Management System API",
    description="A RESTful API for managing patient records",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Patient Management System API is running"
    }


def load_data():
    with open("patients.json", "r") as file:
        data = json.load(file)

    return data


def calculate_bmi(height: float, weight: float) -> float:
    #calculate bmi using weight in kg and height in mtr
    bmi = weight / (height ** 2)
    #rounding the bmi
    return round(bmi, 2)


def get_health_verdict(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"

    return "Obese"


def create_patient_response(patient: dict) -> dict:
    #calculate bmi using height and weight
    bmi = calculate_bmi(
        height=patient["height"],
        weight=patient["weight"]
    )

    health_verdict = get_health_verdict(bmi)

    #separate response dictionary
    return {
        **patient,
        "bmi": bmi,
        "health_verdict": health_verdict
    }


@app.get("/")
def home():
    return {
        "message": "Patient Management System API"
    }

@app.get("/about")
def about():
    return {
        "message": "An API for managing patient records"
    }

#returns all patients
@app.get("/patients", response_model=list[PatientResponse])
def get_patients(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort_by: str = Query(default="id"),
    order: str = Query(default="asc")
):
    data = load_data()

    #allow sorting only by these feilds
    allowed_sort_fields = {
        "id",
        "name",
        "city",
        "age",
        "gender",
        "height",
        "weight",
        "bmi"
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort field"
        )


    #allow only asc and desc order
    if order.lower() not in {"asc", "desc"}:
        raise HTTPException(
            status_code=400,
            detail="Order must be asc or desc"
        )

    #sorting patient records
    if sort_by == "bmi":
        #calculate bmi dynamically
        data.sort(
            key=lambda patient: calculate_bmi(
                height=patient["height"],
                weight=patient["weight"]
            ),
            reverse=order.lower() == "desc"
        )

    else:
        #sort using selected fields stored in patient record
        data.sort(
        key=lambda patient: patient[sort_by],
        reverse=order.lower() == "desc"
        )


    #calculates the strting position for requested page
    start = (page - 1) * page_size

    #calculates the ending position for requested page
    end = start + page_size

    #select only the requested aprt in records
    paginated_data = data[start:end]

    #return an error if the requested page has no patients
    if not paginated_data:
        raise HTTPException(
            status_code=404,
            detail="No patients found for the requested page"
        )


    return [
        create_patient_response(patient)
        for patient in paginated_data
    ]




#patient search API
@app.get("/patients/search", response_model=list[PatientResponse])
def search_patients(
    # | None - can be absent;  default=None - optional;  min_length - must contain least charac
    city: str | None = Query(default=None, min_length=2),
    gender: str | None = Query(default=None, min_length=1),
    name: str | None = Query(default=None, min_length=1),
    health_verdict: str | None = Query(default=None, min_length=1)
):
    data = load_data()

    #start with all available patients
    filtered_patients = data

    #filter patient by city
    if city is not None:
        filtered_patients = [
            patient
            for patient in filtered_patients
            #case-insensitive search; like Jaipur or jaipur, JAIPUR
            #converts these into lowercase before comparing them
            if patient["city"].lower() == city.lower()
        ]

    #filter pateinnt by gender
    if gender is not None:
        filtered_patients = [
            patient 
            for patient in filtered_patients
            if patient["gender"].lower() == gender.lower()
        ]

    #filter patient by name
    if name is not None:
        filtered_patients = [
            patient 
            for patient in filtered_patients
            if name.lower() in patient["name"].lower()
        ]


    #filter pateint by calculated health
    if health_verdict is not None:
        #allow only these four
        allowed_verdicts = {
            "underweight",
            "normal",
            "overweight",
            "obese"
        }

        #convert user input to lowercase
        requested_verdict = health_verdict.lower()

        if requested_verdict not in allowed_verdicts:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid health verdict"
                    "Use Underweight, Normal, Overweight, Obese"
                )
            )

        #keep only patients whose verdict matches
        filtered_patients = [
            patient
            for patient in filtered_patients
            if get_health_verdict(
                calculate_bmi(
                    height=patient["height"],
                    weight=patient["weight"]
                )
            ).lower() == requested_verdict
        ]



    # Add BMI and health verdict to every matching patient
    return [
        create_patient_response(patient)
        for patient in filtered_patients
    ]


#returns a single patient
@app.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: str):
    #load all patients records from json
    data = load_data()

    #search for patient using requested id
    for patient in data:
        if patient["id"] == patient_id:
            return create_patient_response(patient)

    #if not found, return 404 error
    raise HTTPException(
        status_code=404,
        detail="Patient not found"
    )


#To create new data(patient)
@app.post("/patients",
          response_model=PatientResponse,
          status_code=status.HTTP_201_CREATED
          )
def create_patient(patient: Patient):
    data = load_data()

    for existing_patient in data:
        if existing_patient["id"] == patient.id:
            raise HTTPException(
                #409 for duplicate patient ID(already exisits)
                status_code=status.HTTP_409_CONFLICT,
                detail="Patient ID already exists"
            )

    #convert the validated Pydantic model into Dictionary
    patient_data = patient.model_dump()

    #add new patient to the existing record
    data.append(patient_data)

    #save the updated patient record to existing records
    with open("patients.json", "w") as file:
        json.dump(data, file, indent=4)       #indent=4 formats the JSON in a readable way

    #return newly created patient
    return create_patient_response(patient_data)


@app.put("/patients/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: str, updated_patient: Patient):
    data = load_data()

    #search for patient that needs to be updated
    for index, patient in enumerate(data):
        if patient["id"] == patient_id:

            #ensure the id in URL matches the id in request body
            if updated_patient.id != patient_id:
                raise HTTPException(
                    status_code=400,
                    detail="Patient ID in the URL and request body must match"
                )

            data[index] = updated_patient.model_dump()

            with open("patients.json", "w") as file:
                json.dump(data, file, indent=4)

            return create_patient_response(data[index])

    raise HTTPException(
        status_code=404,
        detail="Patient not found"
    )



@app.delete(
        "/patients/{patient_id}",
        response_model=DeletePatientResponse
)
def delete_patient(patient_id: str):
    data = load_data()

    for index, patient in enumerate(data):
        if patient["id"] == patient_id:
            deleted_patient = data.pop(index)

            with open("patients.json", "w") as file:
                json.dump(data, file, indent=4)

            #calculate bmi and health verdict for response
            deleted_patient_response = create_patient_response(
                deleted_patient
            )
            

            return {
                "message":"Patient deleted successfully",
                "deleted_patient": deleted_patient_response
            }

    raise HTTPException(
        status_code=404,
        detail="Patient not found"
    )