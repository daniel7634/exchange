import re
from decimal import Decimal, ROUND_HALF_UP

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


_CUR_MAP = {
    'TWD': {
        'TWD': Decimal('1'),
        'JPY': Decimal('3.669'),
        'USD': Decimal('0.03281'),
    },
    'JPY': {
        'TWD': Decimal('0.26956'),
        'JPY': Decimal('1'),
        'USD': Decimal('0.00885'),
    },
    'USD': {
        'TWD': Decimal('30.444'),
        'JPY': Decimal('111.801'),
        'USD': Decimal('1'),
    }
}

_SYMBOL_MAP = {
    'TWD': '$',
    'JPY': '¥',
    'USD': '$',
}


AMOUNT_PATTERN = re.compile(r'^([¥$])?(\d{1,3}(,\d{3})*)(\.\d+)?$')


def _get_exchange_rate(source: str, target: str) -> Decimal:
    return _CUR_MAP[source][target]


def _validate_currency(source: str, target: str):
    if not source or source not in _CUR_MAP:
        raise ValueError("The source currency is not supported")
    if not target or target not in _CUR_MAP:
        raise ValueError("The target currency is not supported")


def _parse_amount_string(amount_str: str, source: str) -> Decimal:
    match = AMOUNT_PATTERN.match(amount_str)
    if not match:
        raise ValueError("Invalid amount format")

    currency_symbol, integer_part, _, decimal_part = match.groups()
    if currency_symbol != _SYMBOL_MAP[source]:
        raise ValueError("Currency symbol is not match source currency")

    integer_part = Decimal(integer_part.replace(',', ''))
    if decimal_part:
        decimal_part = Decimal(decimal_part)
        amount_decimal = integer_part + decimal_part
    else:
        amount_decimal = integer_part

    return amount_decimal


@api_view(['GET'])
def get_rate_exchange_api(request):
    source: str = request.GET.get('source')
    target: str = request.GET.get('target')
    amount_str: str = request.GET.get('amount')

    try:
        _validate_currency(source, target)
        amount_decimal = _parse_amount_string(amount_str, source)
    except ValueError as e:
        return Response({'msg': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    rate = _get_exchange_rate(source, target)
    converted_amount = amount_decimal * rate
    round_amount = converted_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    formatted_amount = _SYMBOL_MAP.get(target) + '{:,.2f}'.format(round_amount)

    return Response({
        'msg': 'success',
        'amount': formatted_amount,
    })
