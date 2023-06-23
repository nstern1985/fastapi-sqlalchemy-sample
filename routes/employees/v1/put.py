from fastapi import APIRouter, Response, Depends, status as http_status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_session
from infra.crud.employee import EmployeesCrud
from infra.logger import get_logger
from infra.messages.error_messages import ErrorMessages
from routes.employees.v1.schemas import EmployeePutResponse, EmployeePutRequest, EmployeeEntry

logger = get_logger(__file__)
router = APIRouter(prefix="/api/v1")
employees_crud = EmployeesCrud()


@router.put("/employees", response_model=EmployeePutResponse)
async def update_employee(request: EmployeePutRequest, response: Response,
                          session: AsyncSession = Depends(get_session)) -> EmployeePutResponse:
    try:
        employee = await employees_crud.get_by_id(session, request.id) if request.id else \
            await employees_crud.get_by_identification_code(session, request.identificationCode)
        if employee:
            employee = await employees_crud.update(session, employee, identification_code=request.identificationCode,
                                                   email=request.email, birth_date=request.birthDate,
                                                   first_name=request.firstName, last_name=request.lastName,
                                                   city=request.city, country=request.country, street=request.street,
                                                   building_number=request.buildingNumber)
            r = EmployeePutResponse(entry=EmployeeEntry(id=employee.id, firstName=employee.first_name,
                                                               identificationCode=employee.identification_code,
                                                               birthDate=employee.birth_date, email=employee.email,
                                                               lastName=employee.last_name, city=employee.city,
                                                               country=employee.country,
                                                               street=employee.street,
                                                               buildingNumber=employee.building_number))
        else:
            r = EmployeePutResponse(errorMessage=ErrorMessages.ENTRY_NOT_EXIST)
            response.status_code = http_status.HTTP_400_BAD_REQUEST
    except IntegrityError:
        r = EmployeePutResponse(errorMessage=ErrorMessages.INTEGRITY_ERROR)
        response.status_code = http_status.HTTP_500_INTERNAL_SERVER_ERROR
    except Exception:
        r = EmployeePutResponse(errorMessage=ErrorMessages.INTERNAL_ERROR)
        response.status_code = http_status.HTTP_500_INTERNAL_SERVER_ERROR
    return r
