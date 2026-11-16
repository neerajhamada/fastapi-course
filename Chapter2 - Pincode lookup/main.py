from fastapi import FastAPI
from exceptions import (
    PinCodeNotFoundError,
    pincode_not_found_handler,
    InvalidPinCodeError,
    invalid_pincode_handler
)
from models import LocationResponse, BulkRequest, BulkResponse
from data import pincode_db


app = FastAPI(
    title="Pincode Lookup API",
    description="Autofill city and state from Indian Pincode during checkout"
)

# Register your Custom Exception Handler
app.add_exception_handler(PinCodeNotFoundError, pincode_not_found_handler)
app.add_exception_handler(InvalidPinCodeError, invalid_pincode_handler)

@app.get("/")
def home():
    return {"message": "Pincode lookup API"}


# /pincode/{code} -> path params

@app.get("/pincode/{code}", response_model=LocationResponse)
def pincode_lookup(code: str):
    if len(code) != 6 or not code.isdigit():
        raise InvalidPinCodeError(code, "Must be exactly 6 digits")

    if code not in pincode_db:
        raise PinCodeNotFoundError(code)

    return pincode_db[code]

@app.post("/pincode/bulk", response_model=BulkResponse)
def bulk_pincode_lookup(request: BulkRequest):
    results = []
    missing = []

    for code in request.pincodes:
        if code in pincode_db:
            results.append(pincode_db[code])
        else:
            missing.append(code)

    return BulkResponse(
        found=len(results),
        not_found=len(missing),
        results=results,
        missing=missing
    )

        