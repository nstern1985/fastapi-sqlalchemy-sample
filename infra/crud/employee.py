from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infra.crud.base import BaseCrud
from infra.models.employee import Employee


class EmployeesCrud(BaseCrud):
    @property
    def datetime_creation_field_name(self):
        return "create_time"

    def __init__(self):
        super().__init__(Employee)

    async def get_by_identification_code(self, session: AsyncSession, identification_code: str) -> Optional[Employee]:
        query = select(self.model).where(self.model.identification_code == identification_code)
        result = await session.execute(query)
        return result.scalars().first()
