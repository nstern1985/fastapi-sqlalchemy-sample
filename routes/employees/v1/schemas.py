from datetime import date
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class Employee(BaseModel):
    identificationCode: str
    birthDate: date
    firstName: str
    lastName: str
    email: EmailStr
    city: str
    country: str
    street: str
    buildingNumber: str


class EmployeePostRequest(Employee):
    pass


class EmployeeEntry(Employee):
    id: int


class EmployeePostResponse(BaseModel):
    entry: Optional[EmployeeEntry] = None
    errorMessage: Optional[str] = None


class EmployeePutRequest(Employee):
    id: Optional[int]


class EmployeePutResponse(EmployeePostResponse):
    pass


class EmployeeGetResponse(BaseModel):
    entry: Optional[EmployeeEntry] = None
    errorMessage: Optional[str] = None


class EmployeesGetResponse(BaseModel):
    entries: Optional[List[EmployeeEntry]] = None
    errorMessage: Optional[str] = None


class DeleteResponse(BaseModel):
    entry: Optional[EmployeeEntry] = None
    errorMessage: Optional[str] = None
