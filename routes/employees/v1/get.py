from typing import Union
from fastapi import APIRouter, Depends, Response, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_session
from infra.crud.employee import EmployeesCrud
from infra.logger import get_logger
from infra.messages.error_messages import ErrorMessages
from routes.employees.v1.schemas import EmployeeGetResponse, EmployeesGetResponse, EmployeeEntry

logger = get_logger(__file__)
router = APIRouter(prefix="/api/v1")
employees_crud = EmployeesCrud()


@router.get("/employees", response_model=EmployeesGetResponse)
async def get_all_employees(response: Response, offset: int = 0, limit: int = 500,
                            session: AsyncSession = Depends(get_session)) -> EmployeesGetResponse:
    try:
        employees = await employees_crud.get_all(session, offset=offset, limit=limit)
        entries = []
        for employee in employees:
            entries.append(EmployeeEntry(
                id=employee.id, identificationCode=employee.identification_code,
                birthDate=employee.birth_date, firstName=employee.first_name, email=employee.email,
                lastName=employee.last_name, city=employee.city, country=employee.country,
                street=employee.street, buildingNumber=employee.building_number))
        employee_response = EmployeesGetResponse(entries=entries)
    except Exception:
        response.status_code = http_status.HTTP_500_INTERNAL_SERVER_ERROR
        employee_response = EmployeeGetResponse(errorMessage=ErrorMessages.INTERNAL_ERROR)
    return employee_response


@router.get("/employees/{employee_id}")
async def get_employee_by_id(employee_id: Union[int, str], response: Response,
                             session: AsyncSession = Depends(get_session)) -> EmployeeGetResponse:
    try:
        employee = await employees_crud.get_by_id(session, employee_id) if type(employee_id) is int \
            else await employees_crud.get_by_identification_code(session, employee_id)
        if employee:
            employee_response = EmployeeGetResponse(entry=EmployeeEntry(
                id=employee.id, identificationCode=employee.identification_code,
                birthDate=employee.birth_date, firstName=employee.first_name,
                lastName=employee.last_name, city=employee.city, email=employee.email,
                country=employee.country, street=employee.street, buildingNumber=employee.building_number)
            )
        else:
            employee_response = EmployeeGetResponse(errorMessage=ErrorMessages.ENTRY_NOT_EXIST)
    except Exception as ex:
        response.status_code = http_status.HTTP_500_INTERNAL_SERVER_ERROR
        employee_response = EmployeeGetResponse(errorMessage=ErrorMessages.INTERNAL_ERROR)
    return employee_response
