from payments_paymaster import settings
from payments_paymaster.utils import calculate_hash


def test_hash_test_site():
    qs = {
        'LMI_CURRENCY': 'RUB',
        'LMI_HASH': 'm8bC0NMnyUrcr/XZXe4HaT0OkKjDLqLG2Rqo9GZZ0ys=',
        'LMI_MERCHANT_ID': '2902fb4a-d618-4b6b-aade-793b95e10c59',
        'LMI_PAID_AMOUNT': '6000.00',
        'LMI_PAID_CURRENCY': 'RUB',
        'LMI_PAYER_COUNTRY': 'RU',
        'LMI_PAYER_IDENTIFIER': '712769976071',
        'LMI_PAYER_IP_ADDRESS': '93.187.185.237',
        'LMI_PAYER_PASSPORT_COUNTRY': 'RU',
        'LMI_PAYMENT_AMOUNT': '6000.00',
        'LMI_PAYMENT_DESC': '\xd0\x9f\xd1\x80\xd0\xb5\xd0\xb4\xd0\xbe\xd0\xbf\xd0\xbb\xd0\xb0\xd1\x82\xd0\xb0 \xd0\xb7\xd0\xb0 \xd0\xb7\xd0\xb0\xd0\xba\xd0\xb0\xd0\xb7 \xe2\x84\x9641034 610434. \xd0\x94\xd0\xb5\xd0\xb4 \xd0\x9c\xd0\xbe\xd1\x80\xd0\xbe\xd0\xb7 \xd0\xb8 \xd0\xa1\xd0\xbd\xd0\xb5\xd0\xb3\xd1\x83\xd1\x80\xd0\xbe\xd1\x87\xd0\xba\xd0\xb0',
        'LMI_PAYMENT_METHOD': 'Test',
        'LMI_PAYMENT_NO': '41034-20151217-e8a416ef',
        'LMI_PAYMENT_REF': '999',
        'LMI_PAYMENT_SYSTEM': '3',
        'LMI_SIM_MODE': '0',
        'LMI_SYS_PAYMENT_DATE': '2015-12-17T12:14:10',
        'LMI_SYS_PAYMENT_ID': '40599192',
    }

    result = calculate_hash(
        qs,
        hashed_fields=settings.HASH_FIELDS,
        password='YOUR_MOMMY_SECRET',
        hash_method='sha256'
    )

    assert result == 'm8bC0NMnyUrcr/XZXe4HaT0OkKjDLqLG2Rqo9GZZ0ys='
