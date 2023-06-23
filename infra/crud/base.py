from abc import abstractmethod, ABC
from datetime import datetime
from typing import TypeVar, Generic, List, Union
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from infra.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseCrud(Generic[ModelType], ABC):
    def __init__(self, model: ModelType):
        self.model = model

    @property
    @abstractmethod
    def datetime_creation_field_name(self):
        pass

    async def get_by_id(self, session: AsyncSession, id: int) -> Union[ModelType, None]:
        query = select(self.model).where(self.model.id == id)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_by_foreign_key(self, session: AsyncSession, foreign_key: str, value: int) -> Union[ModelType, None]:
        query = (
            select(self.model)
            .options(selectinload(getattr(self.model, foreign_key)))
            .where(getattr(self.model, foreign_key).id == value)
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def get_all(self, session: AsyncSession, after_datetime: datetime = None, offset: int = None,
                      limit: int = None, **kwargs) -> List[ModelType]:
        query = select(self.model)
        for key, value in kwargs.items():
            query = query.where(getattr(self.model, key) == value)
        if after_datetime:
            query = query.where(getattr(self.model, self.datetime_creation_field_name) >= after_datetime)
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    async def create(self, session: AsyncSession, **kwargs) -> ModelType:
        obj = self.model(**kwargs)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def update(self, session: AsyncSession, obj: ModelType, **kwargs) -> ModelType:
        for key, value in kwargs.items():
            setattr(obj, key, value)
        await session.merge(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def delete(self, session: AsyncSession, obj: ModelType):
        await session.delete(obj)
        await session.commit()
