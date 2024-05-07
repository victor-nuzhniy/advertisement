"""App exceptions."""

from fastapi import status as http_status
from typing_extensions import Any

from apps.common.enum import JSENDStatus


class BackendError(Exception):
    """Used for custom output organization for fails and errors in a view.

    {
    status: some_status
    data: some_data
    message: error or fail message
    code: http_status_code
    }
    """

    def __init__(
        self,
        *,
        status: JSENDStatus = JSENDStatus.FAIL,
        data_value: None | int | str | list | dict = None,
        message: str,
        code: int = http_status.HTTP_400_BAD_REQUEST,
    ) -> None:
        """
        Initialize class instance.

        :param status: JSENDStatus Message status - 'success', 'fail', 'error'.
        :param data_value: type Message data, if it is.
        :param message: str Message itself.
        :param code: int Http code.
        """
        self.status = status
        self.data_value = data_value
        self.message = message
        self.code = code

    def __repr__(self) -> str:
        """Represent class instance."""
        return ''.join(
            (
                '{name}(status={status}, data={data}, '.format(
                    name=self.__class__.__name__,
                    status=self.status,
                    data=self.data_value,
                ),
                'message={message}, code={code}'.format(
                    message=self.message,
                    code=self.code,
                ),
            ),
        )

    def __str__(self) -> str:
        """Represent class instance."""
        return self.__repr__()

    def dict(self) -> dict[str, Any]:
        """Convert BackendException to python dict."""
        return {
            'status': self.status.value,
            'data': self.data_value,
            'message': self.message,
            'code': self.code,
        }
