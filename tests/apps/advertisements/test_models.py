"""Test models."""

from apps.advertisements.models import Advertisement
from tests.apps.advertisements.factories import AdvertisementFactory
from tests.bases import BaseModelFactory


class TestAdvertisement:
    """Class for testing Advertisement model."""

    def test_factory(self) -> None:
        """Test model factory."""
        BaseModelFactory.check_factory(
            factory_class=AdvertisementFactory,
            model=Advertisement,
        )

    def test_repr(self) -> None:
        """Test __repr__ method."""
        adv_object: Advertisement = AdvertisementFactory()
        expected_result: str = ''.join(
            (
                '{cname}(id={id}, name={name}, price={price}, model={model}, '.format(
                    cname=adv_object.__class__.name,
                    id=adv_object.id,
                    name=adv_object.name,
                    price=adv_object.price,
                    model=adv_object.model,
                ),
                'region={region}, run={run}, color={color}, salon={salon}, '.format(
                    region=adv_object.region,
                    run=adv_object.run,
                    color=adv_object.color,
                    salon=adv_object.salon,
                ),
                'seller={seller}, adv_date={adv_date}, created_at={created_at}'.format(
                    seller=adv_object.seller,
                    adv_date=adv_object.adv_date,
                    created_at=adv_object.created_at,
                ),
            ),
        )
        actual_result = adv_object.__repr__()  # noqa
        assert expected_result == actual_result
