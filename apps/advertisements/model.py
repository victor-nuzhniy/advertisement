"""Advertisement apps models."""

from sqlalchemy import Column, Date, Integer, String, func

from apps.common.common_utilities import AwareDateTime
from apps.common.db import Base


class Advertisement(Base):
    """Advertisement model."""

    __tablename__ = 'advertisement'

    id = Column(Integer, primary_key=True, nullable=False)
    url = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)
    model = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    run = Column(Integer, nullable=False)
    color = Column(String(100))
    salon = Column(String(50))
    seller = Column(String(255), nullable=False)
    adv_date = Column(Date, default=func.now(), nullable=True)
    created_at = Column(AwareDateTime, default=func.now(), nullable=False)

    def __repr__(self) -> str:
        """Represent class instance."""
        return ''.join(
            (
                '{cname}(id={id}, name={name}, price={price}, model={model}, '.format(
                    cname=self.__class__.name,
                    id=self.id,
                    name=self.name,
                    price=self.price,
                    model=self.model,
                ),
                'region={region}, run={run}, color={color}, salon={salon}, '.format(
                    region=self.region,
                    run=self.run,
                    color=self.color,
                    salon=self.salon,
                ),
                'seller={seller}, adv_date={adv_date}, created_at={created_at}'.format(
                    seller=self.seller,
                    adv_date=self.adv_date,
                    created_at=self.created_at,
                ),
            ),
        )
