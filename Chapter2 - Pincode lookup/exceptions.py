from fastapi.responses import JSONResponse
from fastapi import Request


# Define Custom Exceptions for the API

class PinCodeNotFoundError(Exception):
    def __init__(self, pincode: str):
        self.pincode = pincode

class InvalidPinCodeError(Exception):
    def __init__(self, pincode: str, reason: str = "Invalid format"):
        self.pincode = pincode
        self.reason = reason

# Create a Custom handler for handling the custom exceptions

async def pincode_not_found_handler(request: Request, exc: PinCodeNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "pincode_not_found",
            "message": f"No location for the Pincode: {exc.pincode}",
            "pincode": exc.pincode
        }
    )

async def invalid_pincode_handler(request: Request, exc: InvalidPinCodeError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "invalid_pincode",
            "message": f"Pincode '{exc.pincode}' is invalid: {exc.reason}",
            "pincode": exc.pincode
        }
    )
