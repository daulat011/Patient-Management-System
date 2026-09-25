# Patient Management System API

A RESTful API built with **FastAPI** for managing patient records. The
application supports CRUD operations, patient searching, sorting,
pagination, BMI calculation, health-verdict classification, validation,
and JSON-file persistence.

## Features

-   Health-check endpoint
-   Welcome and about endpoints
-   Retrieve all patients
-   Retrieve a patient by ID
-   Search patients by:
    -   City
    -   Gender
    -   Name
    -   Health verdict
-   Sorting by patient fields and BMI
-   Ascending and descending sorting
-   Pagination
-   Create a new patient
-   Update an existing patient
-   Delete a patient
-   Pydantic-based request validation
-   BMI calculation
-   Health-verdict classification
-   Duplicate patient-ID validation
-   HTTP exception handling
-   Persistent storage using `patients.json`

## Technology Stack

-   Python
-   FastAPI
-   Pydantic
-   Uvicorn
-   JSON file storage
-   Swagger UI / OpenAPI documentation

## Project Structure

``` text
Patient-Management-System/
│
├── main.py
├── models.py
├── patients.json
├── README.md
└── .venv/
```

### File Description

  -----------------------------------------------------------------------
  File                                Description
  ----------------------------------- -----------------------------------
  `main.py`                           Contains the FastAPI application,
                                      endpoints, business logic, BMI
                                      calculation, filtering, sorting,
                                      pagination, and CRUD operations

  `models.py`                         Contains Pydantic models used for
                                      request and response validation

  `patients.json`                     Stores patient records

  `.venv/`                            Python virtual environment used for
                                      project dependencies

  `README.md`                         Project documentation
  -----------------------------------------------------------------------

## Installation and Setup

### 1. Clone or open the project

Open the project folder in VS Code.

### 2. Create a virtual environment

``` bash
python -m venv .venv
```

### 3. Activate the virtual environment

#### Windows PowerShell

``` powershell
.venv\Scripts\Activate.ps1
```

#### Windows Command Prompt

``` cmd
.venv\Scripts\activate
```

### 4. Install dependencies

``` bash
pip install "fastapi[standard]"
```

If a `requirements.txt` file is available, install dependencies using:

``` bash
pip install -r requirements.txt
```

### 5. Start the application

``` bash
python -m uvicorn main:app --reload
```

The API will normally be available at:

``` text
http://127.0.0.1:8000
```

## API Documentation

FastAPI automatically generates interactive documentation.

### Swagger UI

``` text
http://127.0.0.1:8000/docs
```

### ReDoc

``` text
http://127.0.0.1:8000/redoc
```

## API Endpoints

  Method   Endpoint                   Description
  -------- -------------------------- ----------------------------------------------
  GET      `/`                        Returns the API welcome message
  GET      `/about`                   Returns information about the API
  GET      `/health`                  Checks whether the API is running
  GET      `/patients`                Returns patients with sorting and pagination
  GET      `/patients/search`         Searches patients using optional filters
  GET      `/patients/{patient_id}`   Returns one patient by ID
  POST     `/patients`                Creates a new patient
  PUT      `/patients/{patient_id}`   Updates an existing patient
  DELETE   `/patients/{patient_id}`   Deletes a patient

> The `/patients/search` route is defined before
> `/patients/{patient_id}` so that the word `search` is handled by the
> intended search endpoint.

## Patient Data Model

A patient record contains the following fields:

  Field      Type      Description
  ---------- --------- ---------------------------------------------
  `id`       string    Unique patient identifier
  `name`     string    Patient name
  `city`     string    Patient's city
  `age`      integer   Patient age, from 0 to 120
  `gender`   string    Patient gender
  `height`   float     Height in meters; must be greater than 0
  `weight`   float     Weight in kilograms; must be greater than 0

BMI and health verdict are calculated dynamically in the API response.

## BMI Calculation

The API calculates BMI using this formula:

``` text
BMI = weight / (height ** 2)
```

Where:

-   Weight is measured in kilograms.
-   Height is measured in meters.

The calculated BMI is rounded to two decimal places.

### Health Verdict Categories

  BMI Range              Verdict
  ---------------------- -------------
  Less than 18.5         Underweight
  18.5 to less than 25   Normal
  25 to less than 30     Overweight
  30 or higher           Obese

This classification is a simplified BMI-based categorization and is not
a medical diagnosis.

## Example Patient Request

### Create a Patient

**Request**

``` http
POST /patients
```

**JSON body**

``` json
{
    "id": "P016",
    "name": "Aarav Sharma",
    "city": "Jaipur",
    "age": 24,
    "gender": "Male",
    "height": 1.75,
    "weight": 70
}
```

**Example response**

``` json
{
    "id": "P016",
    "name": "Aarav Sharma",
    "city": "Jaipur",
    "age": 24,
    "gender": "Male",
    "height": 1.75,
    "weight": 70,
    "bmi": 22.86,
    "health_verdict": "Normal"
}
```

## Retrieve Patients

### Get the first page

``` http
GET /patients?page=1&page_size=10
```

### Sort by age

``` http
GET /patients?sort_by=age&order=asc
```

### Sort by BMI in descending order

``` http
GET /patients?sort_by=bmi&order=desc
```

Supported sorting fields:

``` text
id
name
city
age
gender
height
weight
bmi
```

Supported sorting orders:

``` text
asc
desc
```

## Search and Filtering

The search endpoint accepts optional query parameters.

### Search by city

``` http
GET /patients/search?city=Jaipur
```

### Search by gender

``` http
GET /patients/search?gender=Male
```

### Search by name

``` http
GET /patients/search?name=aar
```

The name search supports partial and case-insensitive matching.

### Search by health verdict

``` http
GET /patients/search?health_verdict=Normal
```

### Combine multiple filters

``` http
GET /patients/search?city=Jaipur&gender=Male
```

Available search parameters:

  -----------------------------------------------------------------------
  Parameter                           Description
  ----------------------------------- -----------------------------------
  `city`                              Exact, case-insensitive city match

  `gender`                            Exact, case-insensitive gender
                                      match

  `name`                              Partial, case-insensitive name
                                      match

  `health_verdict`                    Filters by Underweight, Normal,
                                      Overweight, or Obese
  -----------------------------------------------------------------------

## Update a Patient

The `PUT` endpoint replaces the complete patient record.

``` http
PUT /patients/P016
```

**JSON body**

``` json
{
    "id": "P016",
    "name": "Aarav Sharma",
    "city": "Delhi",
    "age": 25,
    "gender": "Male",
    "height": 1.75,
    "weight": 72
}
```

The patient ID in the URL and request body must match.

## Delete a Patient

``` http
DELETE /patients/P016
```

The response includes a confirmation message and the deleted patient's
calculated BMI and health verdict.

## Validation and Error Handling

The API uses Pydantic and FastAPI validation.

Common responses include:

  Status Code                  Meaning
  ---------------------------- -------------------------------------------------
  `200 OK`                     Request completed successfully
  `201 Created`                New patient created successfully
  `400 Bad Request`            Invalid sorting field, order, or health verdict
  `404 Not Found`              Patient or requested page does not exist
  `409 Conflict`               Patient ID already exists
  `422 Unprocessable Entity`   Request data failed validation

Examples of validation rules:

-   Age must be between 0 and 120.
-   Height must be greater than 0.
-   Weight must be greater than 0.
-   Patient ID must be unique when creating a patient.
-   Sorting order must be `asc` or `desc`.
-   Health verdict must be one of the supported categories.
-   The patient ID in an update URL must match the ID in the request
    body.

## Data Persistence

Patient data is stored in `patients.json`.

The application:

1.  Reads the current records from the JSON file.
2.  Performs the requested operation.
3.  Saves the updated list back to the same JSON file.

The following operations update the JSON file:

-   Create
-   Update
-   Delete

BMI and health verdict are calculated dynamically and are not required
to be stored in the JSON dataset.

## Testing Checklist

The following functionality should be tested through Swagger UI:

-   [ ] Health-check endpoint
-   [ ] Welcome endpoint
-   [ ] About endpoint
-   [ ] Retrieve patients
-   [ ] Pagination
-   [ ] Sorting by normal fields
-   [ ] Sorting by BMI
-   [ ] Invalid sorting field
-   [ ] Invalid sorting order
-   [ ] Search by city
-   [ ] Search by gender
-   [ ] Search by name
-   [ ] Search by health verdict
-   [ ] Combined search filters
-   [ ] Retrieve a patient by ID
-   [ ] Retrieve a missing patient
-   [ ] Create a patient
-   [ ] Duplicate patient ID
-   [ ] Invalid patient data
-   [ ] Update a patient
-   [ ] Mismatched update IDs
-   [ ] Delete a patient
-   [ ] Delete a missing patient
-   [ ] JSON persistence after create, update, and delete

## Known Project Limitations

-   Data is stored in a JSON file instead of a database.
-   The API does not currently include authentication or authorization.
-   Search results do not currently include pagination.
-   BMI classification is based only on BMI values and should not be
    treated as a complete medical assessment.
-   Concurrent writes to the JSON file are not designed for high-traffic
    production use.

## Learning Outcomes

Through this project, the following concepts were practiced:

-   FastAPI application setup
-   REST API design
-   HTTP methods and status codes
-   Path parameters
-   Query parameters
-   Pydantic models
-   Request validation
-   Response models
-   CRUD operations
-   JSON file handling
-   Filtering and searching
-   Sorting
-   Pagination
-   Exception handling
-   Code reusability
-   BMI calculation
-   API documentation using Swagger UI

## Future Improvements

Possible future improvements include:

-   Replace JSON storage with PostgreSQL or MySQL.
-   Add SQLAlchemy or SQLModel integration.
-   Add authentication using JWT.
-   Add role-based access control.
-   Add automated tests using Pytest.
-   Add logging.
-   Add structured project configuration.
-   Add Docker support.
-   Add database migrations.
-   Add pagination to search results.
-   Add more detailed patient statistics.

## Author

**Daulat Singh**

BCA - Artificial Intelligence and Machine Learning

Jaipur National University
