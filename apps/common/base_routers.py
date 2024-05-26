"""Base routers for admin interface."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import Executable
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import TYPE_CHECKING, Annotated, Any, Sequence, TypeAlias

from apps.common.base_statements import BaseCRUDStatements
from apps.common.common_types import ModelType, SchemaType
from apps.common.common_utilities import change_docstring, checkers
from apps.common.dependencies import get_async_session
from apps.common.orm_services import statement_executor as executor
from apps.common.schemas import JSENDErrorOutSchema, JSENDFailOutSchema, JSENDOutSchema
from apps.common.user_dependencies import get_current_admin_user
from apps.user.models import User

if TYPE_CHECKING:
    LocalModelType: TypeAlias = ModelType
else:
    LocalOutSchema: TypeAlias = SchemaType


base_responses = {
    401: {
        'description': 'Not authenticated.',
        'model': JSENDFailOutSchema,
    },
    403: {
        'description': 'User is not an admin user.',
        'model': JSENDFailOutSchema,
    },
    500: {'description': 'Internal server error.', 'model': JSENDErrorOutSchema},
}
validation_response = {
    422: {'model': JSENDFailOutSchema, 'description': 'ValidationError'},
}


class BaseRouterKwargs:
    """Base router kwargs for admin interface."""

    def __init__(
        self,
        name: str,
        out_schema: SchemaType,
    ) -> None:
        """Initialize BaseRouter instance."""
        self.name = name
        self.tags = ['{name}s application'.format(name=name.capitalize())]
        self.instance_path = ''.join(
            ('/admin/{name}/'.format(name=name), '{instance_id}/'),
        )
        if TYPE_CHECKING:
            self.response_model = JSENDOutSchema
            self.response_model_many = JSENDOutSchema
        else:
            self.response_model = JSENDOutSchema[out_schema]
            self.response_model_many = JSENDOutSchema[Sequence[out_schema]]

    def get_post_router_kwargs(self) -> dict:
        """Get post router kwargs."""
        responses: dict = {
            200: {
                'description': 'Successful create {name} response'.format(
                    name=self.name,
                ),
            },
        }
        responses.update(base_responses)
        responses.update(validation_response)
        return {
            'path': '/admin/{name}/'.format(name=self.name),
            'name': 'create_{name}_admin'.format(name=self.name),
            'response_model': self.response_model,
            'summary': 'Create {name} by admin'.format(name=self.name),
            'responses': responses,
            'tags': self.tags,
        }

    def get_update_router_kwargs(self) -> dict:
        """Get update router kwargs."""
        responses: dict = {
            200: {
                'description': 'Successful update {name} response'.format(
                    name=self.name,
                ),
            },
        }
        responses.update(base_responses)
        return {
            'path': self.instance_path,
            'name': 'update_{name}'.format(name=self.name),
            'response_model': self.response_model,
            'summary': 'Update {name} by admin'.format(name=self.name),
            'responses': responses,
            'tags': self.tags,
        }

    def get_partially_update_router_kwargs(self) -> dict:
        """Get update router kwargs."""
        responses: dict = {
            200: {
                'description': 'Successful partially update {name} response'.format(
                    name=self.name,
                ),
            },
        }
        responses.update(base_responses)
        return {
            'path': self.instance_path,
            'name': 'partially update_{name}'.format(name=self.name),
            'response_model': self.response_model,
            'summary': 'Partially update {name} by admin'.format(name=self.name),
            'responses': responses,
            'tags': self.tags,
        }

    def get_read_router_kwargs(self) -> dict:
        """Get read router kwargs."""
        responses: dict = {
            200: {
                'description': 'Successful get {name} response'.format(
                    name=self.name,
                ),
            },
        }
        responses.update(base_responses)
        return {
            'path': self.instance_path,
            'name': 'read_{name}'.format(name=self.name),
            'response_model': self.response_model,
            'summary': 'Get {name} with id by admin'.format(name=self.name),
            'responses': responses,
            'tags': self.tags,
        }

    def get_delete_router_kwargs(self) -> dict:
        """Get delete router kwargs."""
        responses: dict = {
            200: {
                'description': 'Successful delete {name} response'.format(
                    name=self.name,
                ),
            },
        }
        responses.update(base_responses)
        responses.update(validation_response)
        return {
            'path': self.instance_path,
            'name': 'delete_{name}'.format(name=self.name),
            'response_model': JSENDOutSchema,
            'summary': 'Delete {name} by admin'.format(name=self.name),
            'responses': responses,
            'tags': self.tags,
        }

    def get_list_router_kwargs(self) -> dict:
        """Get list router kwargs."""
        responses: dict = {
            200: {
                'description': 'Successful {name} list response'.format(
                    name=self.name,
                ),
            },
        }
        responses.update(base_responses)
        return {
            'path': '/admin/list/{name}/'.format(name=self.name),
            'name': 'read_{name}_list'.format(name=self.name),
            'response_model': self.response_model_many,
            'summary': 'Get {name} list by admin'.format(name=self.name),
            'responses': responses,
            'tags': self.tags,
        }


class BaseInitializer:
    """Base initializer class for BaseRouterInitializer."""

    def __init__(
        self,
        router: APIRouter,
        in_schemas: tuple[SchemaType, ...],
        out_schema: SchemaType,
        model: ModelType,
    ) -> None:
        """Initialize BaseRouterDecorators instance."""
        self.router = router
        self._in_create_schema = in_schemas[0]
        self._in_update_schema = in_schemas[1]
        self._in_part_update_schema = in_schemas[2]
        self.out_schema = out_schema
        self.statements = BaseCRUDStatements(model=model)
        self.model = model
        self._kwargs_generator = BaseRouterKwargs(model.__name__.lower(), out_schema)

    def get_schema_fields_doc_description(
        self,
        schema: SchemaType,  # type: ignore
        required: str = '',
    ) -> str:
        """Get given schemas fields description."""
        result_list = []
        for key, key_val in schema.model_fields.items():
            result_list.append(
                '- **{key}**: {type} {desc}{required}'.format(
                    key=key,
                    type=key_val.annotation,
                    desc=key_val.description,
                    required=required,
                ),
            )
        return '\n'.join(result_list)

    def create_router_docstring(
        self,
        router_type: str,
        has_path: bool = True,
        has_return: bool = True,
        ending: str = '',
    ) -> str:
        """Create create_router docstring."""
        title = '**{type} {model} record{ending}.**\n'.format(
            type=router_type.title(),
            model=self.model.__name__.lower(),
            ending=ending,
        )
        path_section = ''
        if has_path:
            path_section = '**Path**\n- **instance_id**: int {n} id to {a}\n'.format(
                n=self.model.__name__,
                a=router_type,
            )
        input_section = ''
        if router_type in {'create', 'update', 'partially update'}:
            required = ''
            if router_type in {'create', 'update'}:
                required = ', required'
            input_section = '**Body**\n{schema}\n'.format(
                schema=self.get_schema_fields_doc_description(
                    self._in_create_schema,
                    required,
                ),
            )
        return_section = ''
        if has_return:
            return_section = '**Return schema{ending}**\n{schema}\n'.format(
                ending=ending,
                schema=self.get_schema_fields_doc_description(self.out_schema),
            )
        return '\n'.join([title, path_section, input_section, return_section])


class BaseRouterInitializer(BaseInitializer):
    """Base router initializer for admin interface."""

    def get_create_router(self) -> None:
        """Get create router."""
        if TYPE_CHECKING:
            schema_type: TypeAlias = SchemaType
        else:
            schema_type = self._in_create_schema
        docstring = self.create_router_docstring(
            'create',
            has_path=False,
        )

        @self.router.post(**self._kwargs_generator.get_post_router_kwargs())
        @change_docstring(docstring)
        async def create_instance(  # noqa: WPS430
            request: Request,
            schema: schema_type,
            user: Annotated[User, Depends(get_current_admin_user)],
            session: Annotated[AsyncSession, Depends(get_async_session)],
        ) -> dict:
            """Create post router."""
            statement = self.statements.create_statement(schema=schema)
            created_instance: (
                LocalModelType | Sequence[LocalModelType | None] | None
            ) = await executor.execute_return_statement(
                session,
                statement,
                commit=True,
            )
            checked_instance = checkers.check_created_instance(
                created_instance,
                self.model.__name__,
            )
            output_instance: schema_type = self.out_schema.model_validate(
                checked_instance,
            )
            return {
                'data': output_instance,
                'message': 'Created {name} with id {id}'.format(
                    name=self.model.__name__.lower(),
                    id=output_instance.id,
                ),
            }

    def get_read_router(self) -> None:
        """Get create router."""
        if TYPE_CHECKING:
            schema_type: TypeAlias = SchemaType
        else:
            schema_type = self._in_create_schema
        docstring = self.create_router_docstring('read')

        @self.router.get(**self._kwargs_generator.get_read_router_kwargs())
        @change_docstring(docstring)
        async def get_instance(  # noqa: WPS430
            request: Request,
            instance_id: int,
            user: Annotated[User, Depends(get_current_admin_user)],
            session: Annotated[AsyncSession, Depends(get_async_session)],
        ) -> dict:
            """Create post router."""
            statement = self.statements.read_statement(obj_data={'id': instance_id})
            read_instance: LocalModelType | Sequence[LocalModelType | None] | None = (
                await executor.execute_return_statement(session, statement)
            )
            checked_instance = checkers.check_created_instance(
                read_instance,
                self.model.__name__,
            )
            output_instance: schema_type = self.out_schema.model_validate(
                checked_instance,
            )
            return {
                'data': output_instance,
                'message': 'Read {name} with id {id}'.format(
                    name=self.model.__name__.lower(),
                    id=output_instance.id,
                ),
            }

    def get_update_router(self) -> None:
        """Get create router."""
        if TYPE_CHECKING:
            schema_type: TypeAlias = SchemaType
        else:
            schema_type = self._in_update_schema
        docstring = self.create_router_docstring(
            'update',
        )

        @self.router.put(**self._kwargs_generator.get_update_router_kwargs())
        @change_docstring(docstring)
        async def update_instance(  # noqa: WPS430
            request: Request,
            instance_id: int,
            schema: schema_type,
            user: Annotated[User, Depends(get_current_admin_user)],
            session: Annotated[AsyncSession, Depends(get_async_session)],
        ) -> dict:
            """Create post router."""
            statement = self.statements.update_statement(
                schema=schema,
                where_data={'id': instance_id},
            )
            updated_instance: (
                LocalModelType | Sequence[LocalModelType | None] | None
            ) = await executor.execute_return_statement(
                session,
                statement,
                commit=True,
            )
            checked_instance = checkers.check_created_instance(
                updated_instance,
                self.model.__name__,
            )
            output_instance: schema_type = self.out_schema.model_validate(
                checked_instance,
            )
            return {
                'data': output_instance,
                'message': 'Updated {name} with id {id}'.format(
                    name=self.model.__name__.lower(),
                    id=output_instance.id,
                ),
            }

    def get_partially_update_router(self) -> None:
        """Get create router."""
        if TYPE_CHECKING:
            schema_type: TypeAlias = SchemaType
        else:
            schema_type = self._in_part_update_schema
        docstring = self.create_router_docstring('partially update')

        @self.router.patch(
            **self._kwargs_generator.get_partially_update_router_kwargs(),
        )
        @change_docstring(docstring)
        async def partially_update_instance(  # noqa: WPS430
            request: Request,
            instance_id: int,
            schema: schema_type,
            user: Annotated[User, Depends(get_current_admin_user)],
            session: Annotated[AsyncSession, Depends(get_async_session)],
        ) -> dict:
            """Create post router."""
            statement = self.statements.update_statement(
                schema=schema,
                where_data={'id': instance_id},
            )
            updated_instance: (
                LocalModelType | Sequence[LocalModelType | None] | None
            ) = await executor.execute_return_statement(
                session,
                statement,
                commit=True,
            )
            checked_instance = checkers.check_created_instance(
                updated_instance,
                self.model.__name__,
            )
            output_instance: schema_type = self.out_schema.model_validate(
                checked_instance,
            )
            return {
                'data': output_instance,
                'message': 'Updated {name} with id {id}'.format(
                    name=self.model.__name__.lower(),
                    id=output_instance.id,
                ),
            }

    def get_delete_router(self) -> None:
        """Get create router."""
        docstring = self.create_router_docstring('delete', has_return=False)

        @self.router.delete(**self._kwargs_generator.get_delete_router_kwargs())
        @change_docstring(docstring)
        async def delete_instance(  # noqa: WPS430
            request: Request,
            instance_id: int,
            user: Annotated[User, Depends(get_current_admin_user)],
            session: Annotated[AsyncSession, Depends(get_async_session)],
        ) -> dict:
            """Create post router."""
            statement = self.statements.delete_statement(obj_data={'id': instance_id})
            await executor.execute_delete_statement(session, statement)
            return {
                'data': None,
                'message': 'Deleted {name} with id {id}'.format(
                    name=self.model.__name__.lower(),
                    id=instance_id,
                ),
            }

    def get_list_router(self) -> None:
        """Get list router."""
        docstring = self.create_router_docstring(
            'read',
            has_path=False,
            ending='s list',
        )

        @self.router.get(**self._kwargs_generator.get_list_router_kwargs())
        @change_docstring(docstring)
        async def read_instance_list(  # noqa: WPS430
            request: Request,
            user: Annotated[User, Depends(get_current_admin_user)],
            session: Annotated[AsyncSession, Depends(get_async_session)],
        ) -> dict:
            """Get instance list."""
            statement: Executable = self.statements.list_statement()
            instance_list: (
                Sequence[Any | None] | Sequence[Sequence[Any | None]] | None
            ) = await executor.execute_return_statement(
                session,
                statement,
                many=True,
            )
            return {
                'data': instance_list,
                'message': 'Got {name} instances list'.format(name=self.model.__name__),
            }

    def initialize_routers(self) -> None:
        """Initialize all routers."""
        self.get_create_router()
        self.get_read_router()
        self.get_update_router()
        self.get_partially_update_router()
        self.get_delete_router()
        self.get_list_router()
