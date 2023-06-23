from fastapi import APIRouter, Depends, Response, status as http_status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_session
from infra.crud.employee import EmployeesCrud
from infra.logger import get_logger
from infra.messages.error_messages import ErrorMessages
from routes.employees.v1.schemas import EmployeePostResponse, EmployeePostRequest, Employee, EmployeeEntry

logger = get_logger(__file__)
router = APIRouter(prefix="/api/v1")
employees_crud = EmployeesCrud()


@router.post("/employees", response_model=EmployeePostResponse)
async def create_new_employee(request: EmployeePostRequest, response: Response, session: AsyncSession = Depends(get_session)) -> EmployeePostResponse:
    try:
        new_employee = dict(
            identification_code=request.identificationCode, email=request.email,
            birth_date=request.birthDate, first_name=request.firstName, last_name=request.lastName,
            city=request.city, country=request.country, street=request.street, building_number=request.buildingNumber
        )
        employee = await employees_crud.create(session, **new_employee)
        employee_to_return = EmployeeEntry(id=employee.id, identificationCode=employee.identification_code, birthDate=employee.birth_date,
                                           firstName=employee.first_name, lastName=employee.last_name, email=employee.email,
                                           city=employee.city, country=employee.country, street=employee.street,
                                           buildingNumber=employee.building_number)
        create_employee_response = EmployeePostResponse(entry=employee_to_return)
    except IntegrityError:
        logger.exception("error at create_new_user, user with current identification_code already exists!", extra=request.dict())
        create_employee_response = EmployeePostResponse(errorMessage=ErrorMessages.ENTRY_ALREADY_EXIST)
        response.status_code = http_status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        create_employee_response = EmployeePostResponse(errorMessage=ErrorMessages.INTERNAL_ERROR)
        await session.rollback()
        response.status_code = http_status.HTTP_500_INTERNAL_SERVER_ERROR
    return create_employee_response
