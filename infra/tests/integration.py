import datetime
from dataclasses import dataclass, asdict
from typing import Optional
from uuid import uuid4
from faker import Faker
from sqlalchemy.orm import clear_mappers
from infra.crud.employee import EmployeesCrud
from infra.general import generate_random_date
from infra.models.base import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import pytest

fake = Faker()
employees_crud = EmployeesCrud()


@pytest.fixture(scope="session")
async def db_generator():
    DATABASE_URL = "sqlite+aiosqlite:///test_db.sqlite"
    engine = create_async_engine(DATABASE_URL)
    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        # setup code for populating database goes here
        yield session
        # teardown code goes here, if any
    clear_mappers()  # clear mappers after session


@dataclass
class Employee:
    identification_code: str
    birth_date: datetime.date
    first_name: str
    last_name: str
    city: str
    country: str
    street: str
    building_number: str
    email: str
    id: Optional[int] = None


def generate_random_employee_metadata() -> Employee:
    identification_code = str(uuid4())
    birth_date = generate_random_date()
    first_name = fake.first_name()
    last_name = fake.last_name()
    city = fake.city()
    country = fake.country()
    street = fake.street_name()
    building_number = fake.building_number()
    email = fake.email()
    employee_data = dict(identification_code=identification_code, birth_date=birth_date, first_name=first_name,
                         last_name=last_name, city=city, country=country, street=street,
                         building_number=building_number, email=email)
    return Employee(**employee_data)


@pytest.mark.asyncio
async def test_create_employee(db_generator):
    async for obj in db_generator:
        db = obj
        employee_data = generate_random_employee_metadata()
        employee = await employees_crud.create(db, **asdict(employee_data))
        assert employee_data.identification_code == employee.identification_code
        assert employee_data.birth_date == employee.birth_date
        assert employee_data.first_name == employee.first_name
        assert employee_data.last_name == employee.last_name
        assert employee_data.city == employee.city
        assert employee_data.country == employee.country
        assert employee_data.street == employee.street
        assert employee_data.building_number == employee.building_number
        assert employee_data.email == employee.email


@pytest.mark.asyncio
async def test_update_employee(db_generator):
    async for obj in db_generator:
        db = obj
        employee_data = generate_random_employee_metadata()
        employee = await employees_crud.create(db, **asdict(employee_data))
        updated_employee_data = generate_random_employee_metadata()
        updated_employee_data.id = employee.id
        updated_employee = await employees_crud.update(db, employee, **asdict(updated_employee_data))
        assert updated_employee.id == employee.id
        assert updated_employee.identification_code == updated_employee_data.identification_code
        assert updated_employee.birth_date == updated_employee_data.birth_date
        assert updated_employee.first_name == updated_employee_data.first_name
        assert updated_employee.last_name == updated_employee_data.last_name
        assert updated_employee.city == updated_employee_data.city
        assert updated_employee.country == updated_employee_data.country
        assert updated_employee.street == updated_employee_data.street
        assert updated_employee.building_number == updated_employee_data.building_number
        assert updated_employee.email == updated_employee_data.email


@pytest.mark.asyncio
async def test_delete_employee(db_generator):
    async for obj in db_generator:
        db = obj
        employee_data = generate_random_employee_metadata()
        employee = await employees_crud.create(db, **asdict(employee_data))
        await employees_crud.delete(db, employee)
        extracted_employee = await employees_crud.get_by_id(db, employee.id)
        assert extracted_employee is None


@pytest.mark.asyncio
async def test_get_employee(db_generator):
    async for obj in db_generator:
        db = obj
        employee_data = generate_random_employee_metadata()
        employee = await employees_crud.create(db, **asdict(employee_data))
        extracted_employee = await employees_crud.get_by_id(db, employee.id)
        assert extracted_employee == employee


@pytest.mark.asyncio
async def test_get_employee_by_identification_code(db_generator):
    async for obj in db_generator:
        db = obj
        employee_data = generate_random_employee_metadata()
        employee = await employees_crud.create(db, **asdict(employee_data))
        extracted_employee = await employees_crud.get_by_identification_code(db, employee.identification_code)
        assert extracted_employee == employee


@pytest.mark.asyncio
async def test_employee_get_all(db_generator):
    async for obj in db_generator:
        db = obj
        created_employees_ids = set()
        for _ in range(20):
            employee_data = generate_random_employee_metadata()
            employee = await employees_crud.create(db, **asdict(employee_data))
            created_employees_ids.add(employee.id)
        extracted_employees = await employees_crud.get_all(db)
        extracted_employees_ids = {e.id for e in extracted_employees}
        assert created_employees_ids == extracted_employees_ids
