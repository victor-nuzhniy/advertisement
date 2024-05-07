"""Statements for db data manipulation for user apps."""

from apps.common.base_statements import BaseCRUDStatements
from apps.user.models import User

user_crud_statements = BaseCRUDStatements(model=User)
