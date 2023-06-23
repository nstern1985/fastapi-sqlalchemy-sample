from sqlalchemy import Column, Integer, DateTime, String, func, Date, Index

from infra.models.base import Base


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    identification_code = Column(String, unique=True)
    create_time = Column(DateTime, server_default=func.now())
    birth_date = Column(Date)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    city = Column(String)
    country = Column(String)
    street = Column(String)
    building_number = Column(String)
    
    __table_args__ = (
        Index('idx_employee_identification_code', identification_code),
    )
