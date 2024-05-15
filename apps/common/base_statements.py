"""Project Base SQLAlchemy statements."""

from sqlalchemy import Executable, and_, delete, select, update
from sqlalchemy.dialects.postgresql import insert
from typing_extensions import Optional, Type, Union

from apps.common.common_types import ModelType, SchemaType


class BaseCRUDStatements:
    """Base model CRUD statements."""

    def __init__(self, *, model: Type[ModelType]) -> None:
        """Initialize class instance."""
        self.model = model

    def create_statement(
        self,
        *,
        schema: Optional[SchemaType] = None,
        obj_data: Optional[dict] = None,
    ) -> Executable:
        """Create statement for creating and returning model."""
        obj_data = obj_data if obj_data else {}
        obj_in_data = schema.model_dump(exclude_unset=True) if schema else {}
        insert_statement = (
            insert(self.model).values(**obj_data, **obj_in_data).returning(self.model)
        )
        return (
            select(self.model)
            .from_statement(insert_statement)
            .execution_options(populate_existing=True)
        )

    def create_many_statement(
        self,
        schemas: SchemaType,  # type: ignore
    ) -> Executable:
        """Create statement for creating and returning models with given args."""
        insert_statement = (
            insert(self.model)
            .values(
                [
                    schema.model_dump(exclude_unset=True)
                    for schema in schemas.item_list  # type: ignore
                ],
            )
            .returning(self.model)
        )
        return (
            select(self.model)
            .from_statement(insert_statement)
            .execution_options(populate_existing=True)
        )

    def read_statement(
        self,
        *,
        schema: Optional[SchemaType] = None,
        obj_data: Optional[dict] = None,
    ) -> Executable:
        """Create statement for model reading."""
        obj_data = obj_data if obj_data else {}
        obj_in_data = schema.model_dump(exclude_unset=True) if schema else {}
        statement = select(self.model)
        for key, value_data in {**obj_data, **obj_in_data}.items():
            statement = statement.where(getattr(self.model, key) == value_data)
        return statement

    def update_statement(
        self,
        *,
        schema: Union[SchemaType, dict, None] = None,
        where_data: Optional[dict] = None,
    ) -> Executable:
        """Create statement for updating and returning model instance."""
        if isinstance(schema, dict):
            schema_values = schema
        elif schema is None:
            schema_values = {}
        else:
            schema_values = schema.model_dump(exclude_unset=True, exclude_none=True)
        where_expr = []
        if where_data:
            for key, value_data in where_data.items():
                where_expr.append(getattr(self.model, key) == value_data)
        update_statement = (
            update(self.model)
            .where(and_(*where_expr))
            .values(**schema_values)
            .returning(self.model)
            .execution_options(synchronize_session='fetch')
        )
        return (
            select(self.model)
            .from_statement(statement=update_statement)
            .execution_options(populate_existing=True)
        )

    def delete_statement(
        self,
        *,
        schema: Optional[SchemaType] = None,
        obj_data: Optional[dict] = None,
    ) -> Executable:
        """Create statement for deleting model."""
        obj_data = obj_data if obj_data else {}
        schema_dict = schema.model_dump(exclude_unset=True) if schema else {}
        statement = delete(self.model)
        for key, value_data in {**obj_data, **schema_dict}.items():
            statement = statement.where(getattr(self.model, key) == value_data)
        return statement

    def list_statement(
        self,
        *,
        filters: Optional[dict] = None,
    ) -> Executable:
        """Create statement for read models list."""
        select_statement = select(self.model)
        if filters:
            select_statement = select_statement.filter_by(**filters)
        return select_statement.execution_options(populate_existing=True)
