"""Project constants."""

from re import compile, escape

specials = escape("!#$%&'*+-/=?^_`{|?.")

EMAIL_REGEX = compile(  # noqa: WPS421
    ''.join(
        (
            '^(?![',
            specials,
            '])(?!.*[',
            specials,
            ']{2})(?!.*[',
            specials,
            ']$)[A-Za-z0-9',
            specials,
            ']+(?<![',
            specials,
            '])@[A-Za-z0-9.-]+[.][A-Za-z]{2,4}$',
        ),
    ),
)
