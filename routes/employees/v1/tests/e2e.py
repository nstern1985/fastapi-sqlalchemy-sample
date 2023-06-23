import random
from datetime import datetime
from typing import Optional
from uuid import uuid4
import pytest
from unittest.mock import patch, MagicMock
from async_asgi_testclient import TestClient
from faker import Faker
from sqlalchemy.exc import IntegrityError
from fastapi import status as http_status
from infra.general import generate_random_date
from infra.messages.error_messages import ErrorMessages
from infra.models.employee import Employee as EmployeeDTO

from main import app
from routes.employees.v1.schemas import EmployeeGetResponse, EmployeesGetResponse, EmployeePostRequest, \
    EmployeePostResponse, Employee as EmployeeSchema, EmployeePutResponse, DeleteResponse

fake = Faker()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def generate_dto_employee(creation_datetime: Optional[datetime] = None) -> EmployeeDTO:
    employee = MagicMock(EmployeeDTO)
    employee.id = random.randint(1, 1000)
    employee.identification_code = str(uuid4())
    employee.create_time = creation_datetime or datetime.now()
    employee.birth_date = generate_random_date()
    employee.first_name = fake.first_name()
    employee.last_name = fake.last_name()
    employee.email = fake.email()
    employee.city = fake.city()
    employee.country = fake.country()
    employee.street = fake.street_name()
    employee.building_number = fake.building_number()
    return employee


def generate_employee_schema_obj() -> EmployeeSchema:
    return EmployeeSchema(identificationCode=str(uuid4()), birthDate=generate_random_date(), firstName=fake.first_name(),
                          lastName=fake.last_name(), email=fake.email(), city=fake.city(), country=fake.country(),
                          street=fake.street_name(), buildingNumber=fake.building_number())


def generate_dto_employee_from_schema_obj(employee_schema: EmployeeSchema) -> EmployeeDTO:
    employee = MagicMock(EmployeeDTO)
    employee.id = random.randint(1, 10000)
    employee.identification_code = employee_schema.identificationCode
    employee.create_time = datetime.now()
    employee.birth_date = employee_schema.birthDate
    employee.first_name = employee_schema.firstName
    employee.last_name = employee_schema.lastName
    employee.email = employee_schema.email
    employee.city = employee_schema.city
    employee.country = employee_schema.country
    employee.street = employee_schema.street
    employee.building_number = employee_schema.buildingNumber
    return employee


# region GET single Employee


@pytest.mark.asyncio
async def test_get_employee_not_exist(client: TestClient):
    with patch("routes.employees.v1.get.employees_crud.get_by_id", return_value=None):
        response = await client.get("/api/v1/employees/1")
        response_obj = EmployeeGetResponse(**response.json())
        assert response_obj.errorMessage == ErrorMessages.ENTRY_NOT_EXIST


@pytest.mark.asyncio
async def test_get_employee_exist(client: TestClient):
    employee = generate_dto_employee()
    with patch("routes.employees.v1.get.employees_crud.get_by_id", return_value=employee):
        response = await client.get("/api/v1/employees/1")
        response_obj = EmployeeGetResponse(**response.json())
        assert response_obj.entry.identificationCode == employee.identification_code
        assert response_obj.entry.birthDate == employee.birth_date
        assert response_obj.entry.firstName == employee.first_name
        assert response_obj.entry.lastName == employee.last_name
        assert response_obj.entry.email == employee.email
        assert response_obj.entry.city == employee.city
        assert response_obj.entry.country == employee.country
        assert response_obj.entry.street == employee.street
        assert response_obj.entry.buildingNumber == employee.building_number


@pytest.mark.asyncio
async def test_get_employee_raises_error(client: TestClient):
    async def raise_error(*_):
        raise Exception("blah")

    with patch("routes.employees.v1.get.employees_crud.get_by_id", side_effect=raise_error):
        response = await client.get("/api/v1/employees/1")
        response_obj = EmployeeGetResponse(**response.json())
        assert response_obj.errorMessage == ErrorMessages.INTERNAL_ERROR

# endregion

# region GET multiple Employees


@pytest.mark.asyncio
async def test_get_employee_empty_employee_list(client: TestClient):
    with patch("routes.employees.v1.get.employees_crud.get_all", return_value=[]):
        response = await client.get("/api/v1/employees")
        response_obj = EmployeesGetResponse(**response.json())
        assert response_obj.errorMessage is None
        assert not response_obj.entries


@pytest.mark.asyncio
async def test_get_employee_with_employees(client: TestClient):
    number_of_entries = random.randint(2, 20)
    employees = []
    for _ in range(number_of_entries):
        employees.append(generate_dto_employee())
    with patch("routes.employees.v1.get.employees_crud.get_all", return_value=employees):
        response = await client.get("/api/v1/employees")
        response_obj = EmployeesGetResponse(**response.json())
        assert response_obj.errorMessage is None
        assert response_obj.entries
        assert len(response_obj.entries) == number_of_entries


@pytest.mark.asyncio
async def test_get_employee_raises_error(client: TestClient):
    async def raise_error(*_):
        raise Exception("blah")
    with patch("routes.employees.v1.get.employees_crud.get_all", side_effect=raise_error):
        response = await client.get("/api/v1/employees")
        response_obj = EmployeesGetResponse(**response.json())
        assert response_obj.errorMessage == ErrorMessages.INTERNAL_ERROR

# endregion

# region POST Employee


@pytest.mark.asyncio
async def test_post_employee_already_exists(client: TestClient):
    async def raise_integrity_error(session, **kwargs):
        raise IntegrityError("statement", ["x"], BaseException)

    employee = generate_employee_schema_obj()
    employee.birthDate = employee.birthDate.isoformat()
    with patch("routes.employees.v1.post.employees_crud.create", side_effect=raise_integrity_error):
        response = await client.post("/api/v1/employees", json=employee.dict())
        response_obj = EmployeePostResponse(**response.json())
        assert response_obj.errorMessage == ErrorMessages.ENTRY_ALREADY_EXIST


@pytest.mark.asyncio
async def test_post_employee_internal_error(client: TestClient):
    async def raise_integrity_error(session, **kwargs):
        raise Exception

    employee = generate_employee_schema_obj()
    employee.birthDate = employee.birthDate.isoformat()
    with patch("routes.employees.v1.post.employees_crud.create", side_effect=raise_integrity_error):
        response = await client.post("/api/v1/employees", json=employee.dict())
        response_obj = EmployeePostResponse(**response.json())
        assert response_obj.errorMessage == ErrorMessages.INTERNAL_ERROR


@pytest.mark.asyncio
async def test_post_employee_valid_response(client: TestClient):
    employee = generate_employee_schema_obj()
    employee_dto = generate_dto_employee_from_schema_obj(employee)
    employee.birthDate = employee.birthDate.isoformat()
    with patch("routes.employees.v1.post.employees_crud.create", return_value=employee_dto):
        response = await client.post("/api/v1/employees", json=employee.dict())
        response_obj = EmployeePostResponse(**response.json())
        assert response_obj.errorMessage is None
        assert response_obj.entry.identificationCode == employee.identificationCode
        assert response_obj.entry.birthDate.isoformat() == employee.birthDate
        assert response_obj.entry.firstName == employee.firstName
        assert response_obj.entry.lastName == employee.lastName
        assert response_obj.entry.email == employee.email
        assert response_obj.entry.city == employee.city
        assert response_obj.entry.country == employee.country
        assert response_obj.entry.street == employee.street
        assert response_obj.entry.buildingNumber == employee.buildingNumber

# endregion

# region PUT Employee


@pytest.mark.asyncio
async def test_put_employee_valid_response(client: TestClient):
    employee = generate_employee_schema_obj()
    employee_dto = generate_dto_employee_from_schema_obj(employee)
    old_employee_dto = generate_dto_employee()
    old_employee_dto.id = employee_dto.id
    old_employee_dto.identification_code = employee_dto.id
    employee.birthDate = employee.birthDate.isoformat()

    with patch("routes.employees.v1.put.employees_crud.get_by_id", return_value=None):
        with patch("routes.employees.v1.put.employees_crud.get_by_identification_code", return_value=old_employee_dto):
            with patch("routes.employees.v1.put.employees_crud.update", return_value=employee_dto):
                response = await client.put("/api/v1/employees", json=employee.dict())
                response_obj = EmployeePostResponse(**response.json())
                assert response_obj.errorMessage is None
                assert response_obj.entry.identificationCode == employee.identificationCode
                assert response_obj.entry.birthDate.isoformat() == employee.birthDate
                assert response_obj.entry.firstName == employee.firstName
                assert response_obj.entry.lastName == employee.lastName
                assert response_obj.entry.email == employee.email
                assert response_obj.entry.city == employee.city
                assert response_obj.entry.country == employee.country
                assert response_obj.entry.street == employee.street
                assert response_obj.entry.buildingNumber == employee.buildingNumber


@pytest.mark.asyncio
async def test_post_employee_not_exist(client: TestClient):
    employee = generate_employee_schema_obj()
    employee.birthDate = employee.birthDate.isoformat()
    with patch("routes.employees.v1.put.employees_crud.get_by_id", return_value=None):
        with patch("routes.employees.v1.put.employees_crud.get_by_identification_code", return_value=None):
            response = await client.put("/api/v1/employees", json=employee.dict())
            response_obj = EmployeePutResponse(**response.json())
            assert response_obj.errorMessage == ErrorMessages.ENTRY_NOT_EXIST

# endregion

# region DELETE Employee


@pytest.mark.asyncio
async def test_delete_not_exist_employee(client: TestClient):
    with patch("routes.employees.v1.delete.employees_crud.get_by_id", return_value=None):
        with patch("routes.employees.v1.delete.employees_crud.get_by_identification_code", return_value=None):
            response = await client.delete("/api/v1/employees/1")
            response_obj = DeleteResponse(**response.json())
            assert response.status_code == http_status.HTTP_400_BAD_REQUEST
            assert response_obj.errorMessage == ErrorMessages.ENTRY_NOT_EXIST


@pytest.mark.asyncio
async def test_delete_existing_employee(client: TestClient):
    employee_dto = generate_dto_employee()
    employee_dto.id = random.randint(1, 1000)
    with patch("routes.employees.v1.delete.employees_crud.get_by_id", return_value=employee_dto):
        with patch("routes.employees.v1.delete.employees_crud.delete", return_value=None):
            response = await client.delete(f"/api/v1/employees/{employee_dto.id}")
            assert response.status_code == http_status.HTTP_200_OK
            response_obj = DeleteResponse(**response.json())
            assert response_obj.errorMessage is None
            assert response_obj.entry.identificationCode == employee_dto.identification_code
            assert response_obj.entry.birthDate == employee_dto.birth_date
            assert response_obj.entry.firstName == employee_dto.first_name
            assert response_obj.entry.lastName == employee_dto.last_name
            assert response_obj.entry.email == employee_dto.email
            assert response_obj.entry.city == employee_dto.city
            assert response_obj.entry.country == employee_dto.country
            assert response_obj.entry.street == employee_dto.street
            assert response_obj.entry.buildingNumber == employee_dto.building_number

# endregion
