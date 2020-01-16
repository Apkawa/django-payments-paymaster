import datetime
import json
import logging
import time
from base64 import b64encode

from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.encoding import smart_bytes, smart_str
from payments import PaymentStatus
from payments.core import BasicProvider
from payments.models import BasePayment

from . import settings
from .rest_api.client import PaymasterApiClient
from .utils import calculate_hash

logger = logging.getLogger(__name__)


class PaymasterProvider(BasicProvider):
    """
    Provider for https://paymaster.ru
    """

    _action = "https://paymaster.ru/Payment/Init"

    def __init__(self, client_id, secret, shop_id=None, **kwargs):
        # CIN
        self.client_id = client_id
        # Secret
        self.secret = secret
        self.shop_id = shop_id

        self.api_login = kwargs.pop('api_login')
        self.api_password = kwargs.pop('api_password')
        self.api_verify = kwargs.pop('api_verify', False)

        self.sim_mode = kwargs.pop('sim_mode', None)
        self.payment_method = kwargs.pop('payment_method', None)

        self.hash_fields = kwargs.pop('hash_fields', settings.HASH_FIELDS)
        self.hash_method = kwargs.pop('hash_method', settings.HASH_METHOD)
        self.hash_fail_http_code = kwargs.pop('hash_fail_http_code', settings.HASH_FAIL_HTTP_CODE)
        super().__init__(**kwargs)

    def get_action(self, payment):
        return self._action

    def get_payment_number(self, payment: BasePayment):
        return payment.token

    def get_payer_phone(self, payment: BasePayment):
        return None

    def get_payer_email(self, payment: BasePayment):
        return payment.billing_email

    def get_description(self, payment: BasePayment):
        description = payment.description
        if not description:
            return 'Payment'
        return description

    def get_hidden_fields(self, payment: BasePayment):
        return_url = self.get_return_url(payment)
        expire = datetime.datetime.now() + datetime.timedelta(days=1)
        description = self.get_description(payment)
        data = {
            'LMI_MERCHANT_ID': self.client_id,
            'LMI_SHOP_ID': self.shop_id,
            'LMI_CURRENCY': payment.currency,
            'LMI_SIM_MODE': self.sim_mode,
            'LMI_PAYMENT_AMOUNT': str(payment.total),
            'LMI_PAYMENT_NO': self.get_payment_number(payment),
            'LMI_PAYMENT_DESC': description,
            'LMI_PAYMENT_DESC_BASE64': smart_str(b64encode(smart_bytes(description))),
            'LMI_PAYER_PHONE_NUMBER': self.get_payer_phone(payment),
            'LMI_PAYER_EMAIL': self.get_payer_email(payment),
            'LMI_EXPIRES': f'{expire:%Y-%m-%dT%H:%M:%S}',
            'LMI_PAYMENT_METHOD': self.payment_method,
            'LMI_SUCCESS_URL': return_url,
            'LMI_FAILURE_URL': return_url,
            'LMI_INVOICE_CONFIRMATION_URL': return_url,
            'LMI_PAYMENT_NOTIFICATION_URL': return_url,
            'PAYMENT_TOKEN': payment.token,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return data

    def get_token_from_request(self, payment, request):
        return request.POST.get('PAYMENT_TOKEN')

    def verify_hash(self, data):
        """ Проверка ключа безопасности """
        _hash = calculate_hash(data,
                               password=self.secret,
                               hashed_fields=self.hash_fields,
                               hash_method=self.hash_method)
        return _hash == data.get('LMI_HASH')

    def invoice_confirmation(self, payment: BasePayment, request):
        payment.change_status(PaymentStatus.WAITING)
        return HttpResponse('YES', content_type='text/plain')

    def process_data(self, payment: BasePayment, request):
        data = request.POST.copy()
        if data.get('LMI_PREREQUEST'):
            return self.invoice_confirmation(payment, request)

        if 'LMI_HASH' in data:
            if not self.verify_hash(data):
                logger.debug(u'NotificationPaid error. Data: %s, hashed_fields: %s',
                             request.POST.dict(), self.hash_fields)
                logger.error(
                    u'Invoice {0} payment failed by reason: HashError'.format(
                        request.POST.get('LMI_PAYMENT_NO')))

                return HttpResponse('HashError', status=self.hash_fail_http_code)

            if payment.status == PaymentStatus.WAITING:
                payment.extra_data = json.dumps(data, indent=2)
                payment.captured_amount = data['LMI_PAID_AMOUNT']
                payment.transaction_id = data['LMI_SYS_PAYMENT_ID']
                api_client = PaymasterApiClient(
                    login=self.api_login,
                    password=self.api_password
                )
                if self.api_verify:
                    response = api_client.get_payment(payment.transaction_id)
                    if response['State'] == PaymasterApiClient.PaymentState.COMPLETE:
                        payment.change_status(PaymentStatus.CONFIRMED)
                    elif response['State'] == PaymasterApiClient.PaymentState.CANCELLED:
                        payment.change_status(PaymentStatus.REJECTED)
                else:
                    payment.change_status(PaymentStatus.CONFIRMED)
                return HttpResponse('')

        if payment.status == PaymentStatus.WAITING:
            # Ждем оплаты
            time.sleep(3)
            return redirect('.')

        success_url = payment.get_success_url()
        failure_url = payment.get_failure_url()
        if payment.status == PaymentStatus.CONFIRMED:
            return redirect(success_url)
        return redirect(failure_url)
