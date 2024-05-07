"""Models for user apps."""

from sqlalchemy import Boolean, Column, Integer, String, func
from sqlalchemy.orm import relationship

from apps.common.common_utilities import AwareDateTime
from apps.common.db import Base


class User(Base):
    """User model."""

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(120), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    is_active = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(AwareDateTime, default=func.now(), nullable=False)
    updated_at = Column(
        AwareDateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_visit_at = Column(AwareDateTime, default=func.now(), nullable=False)
    last_request_at = Column(AwareDateTime, default=func.now(), nullable=False)
    posts = relationship('Post', back_populates='user')
    likes = relationship('Like', back_populates='user')

    def __repr__(self) -> str:
        """Represent class instance."""
        return ''.join(
            (
                '{name}(id={id}, username={username}, email={email}, '.format(
                    name=self.__class__.__name__,
                    id=self.id,
                    username=self.username,
                    email=self.email,
                ),
                'is_active={is_active}, is_admin={is_admin}, '.format(
                    is_active=self.is_active,
                    is_admin=self.is_admin,
                ),
                'created_at={created_at}, updated_at={updated_at}, '.format(
                    created_at=self.created_at,
                    updated_at=self.updated_at,
                ),
                'last_visit_at={last_visit_at})'.format(
                    last_visit_at=self.last_visit_at,
                ),
            ),
        )
