from typing import Union
from fastapi import APIRouter, Depends, Response, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_session
from infra.crud.employee import EmployeesCrud
from infra.logger import get_logger
from infra.messages.error_messages import ErrorMessages
from routes.employees.v1.schemas import DeleteResponse, EmployeeEntry

logger = get_logger(__file__)
router = APIRouter(prefix="/api/v1")
employees_crud = EmployeesCrud()


@router.delete("/employees/{employee_id}", response_model=DeleteResponse)
async def delete_employee(employee_id: Union[str, int], response: Response, session: AsyncSession = Depends(get_session)) -> DeleteResponse:
    try:
        employee_id = int(employee_id) if type(employee_id) is str and employee_id.isnumeric() else employee_id
        employee = await employees_crud.get_by_id(session, employee_id) if type(employee_id) is int \
            else await employees_crud.get_by_identification_code(session, employee_id)
        if employee:
            await employees_crud.delete(session, employee)
            return DeleteResponse(entry=EmployeeEntry(id=employee.id, identificationCode=employee.identification_code,
                                                      city=employee.city, country=employee.country,
                                                      email=employee.email, buildingNumber=employee.building_number,
                                                      birthDate=employee.birth_date, firstName=employee.first_name,
                                                      lastName=employee.last_name, street=employee.street))
        else:
            response.status_code = http_status.HTTP_400_BAD_REQUEST
            return DeleteResponse(errorMessage=ErrorMessages.ENTRY_NOT_EXIST)
    except Exception:
        logger.exception("error at delete_employee", extra=dict(employeeID=employee_id))
        response.status_code = http_status.HTTP_500_INTERNAL_SERVER_ERROR
        return DeleteResponse(errorMessage=ErrorMessages.INTERNAL_ERROR)
