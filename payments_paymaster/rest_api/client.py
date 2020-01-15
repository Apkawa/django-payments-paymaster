import base64
import datetime
import hashlib
import logging
import re
from collections import OrderedDict, namedtuple
from urllib.parse import urljoin
from uuid import uuid4

import requests

from .exceptions import PAYMASTER_ERROR_CODES, ApiError
from ..constants import INVOICE_REJECTED
from ..utils import parse_datetime

logger = logging.getLogger('paymaster.rest_client')


class APIClient(object):
    endpoint = None

    def _compose_url(self, path):
        return urljoin(self.endpoint, path)

    def _get_request_kwargs(self, path, data, params, method):
        """
        Can be override. Kwargs is requests kwargs
        :param path:
        :param data:
        :param method:
        :return:
        """
        return {
            'data': data,
            'params': params,
        }

    def _handle_error(self, response):
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            logger.exception(response.content)
            raise e

    def _request(self, path, params=None, data=None, method='GET', **kwargs):
        method_call = getattr(requests, method.lower())
        _url = self._compose_url(path)

        call_kwargs = self._get_request_kwargs(path=path, data=data, params=params, method=method)
        call_kwargs.update(kwargs)
        response = method_call(_url, **call_kwargs)
        self._handle_error(response)
        return response

    def _get(self, path, params=None):
        return self._request(path, params=params, method='GET')

    def _post(self, path, data=None):
        return self._request(path, data=data, method='POST')


PaymentState = namedtuple('PaymentState', [
    'INITIATED',
    'PROCESSING',
    'COMPLETE',
    'CANCELLED',
])(
    'INITIATED',
    'PROCESSING',
    'COMPLETE',
    'CANCELLED',
)


class PaymasterApiClient(APIClient):
    endpoint = 'https://paymaster.ru/partners/rest/'

    PaymentState = PaymentState

    def __init__(self, login, password):
        self.login = login
        self.password = password

    def _handle_error(self, response):
        super(PaymasterApiClient, self)._handle_error(response)
        code = response.json()['ErrorCode']
        if code < 0:
            raise PAYMASTER_ERROR_CODES.get(code, ApiError(code=code))

    def _gen_nonce(self):
        return str(uuid4())

    def _calculate_hash(self, data, fields):
        """
        хеш полей запроса. В описании каждого запроса написано, какие поля подлежат хешированию.
        Значения этих полей записываются в одну строчку через точку с запятой,
        затем от полученной UTF8-строки считается SHA1-хеш, который затем кодируется base64.
        PHP код формирования хеша: $hash = base64_encode(sha1($str, true)), где $str - строка параметров
        :param data:
        :param fields:
        :return:
        """
        _line = u';'.join(map(str, [data.get(key) or '' for key in fields]))
        _hash = hashlib.sha1(bytes(_line.encode('utf-8')))
        _hash = base64.b64encode(_hash.digest()).replace('\n', '')
        return _hash.encode('utf-8')

    def _auth_params(self, params, fields=None):
        fields = fields or []
        params['nonce'] = self._gen_nonce()
        params['login'] = self.login
        fields = ['login', 'password', 'nonce'] + fields

        hash_params = dict(params)
        hash_params['password'] = self.password

        params['hash'] = self._calculate_hash(hash_params, fields)
        return params

    def _prepare_payment_data(self, payment_data):
        del payment_data['LastUpdate']
        if payment_data['LastUpdateTime']:
            payment_data['LastUpdateTime'] = parse_datetime(payment_data['LastUpdateTime'])
        return payment_data

    def _prepare_refund_data(self, payment_data):
        if payment_data['LastUpdate']:
            payment_data['LastUpdate'] = parse_datetime(payment_data['LastUpdate'])
        return payment_data

    def _normalize_date(self, date_obj):
        if date_obj is None:
            return date_obj

        if isinstance(date_obj, str):
            date_obj = parse_datetime(date_obj)

        if isinstance(date_obj, datetime.datetime):
            date_obj = date_obj.date()

        if isinstance(date_obj, datetime.date):
            return date_obj.isoformat()

    def get_payment(self, payment_id):
        """
        Проверка статуса по идентификатору платежа

        Этот запрос используется для получения информации о платеже по его номеру в системе PayMaster.

        URL: https://paymaster.ru/partners/rest/getPayment

        Параметры запроса:
            paymentID - идентификатор платежа в системе PayMaster (поле LMI_SYS_PAYMENT_ID)
            Хешируемые параметры: login;password;nonce;paymentID
        Параметры ответа:
            State - состояние платежа. Допустимые значения:
                INITIATED: платеж начат,
                PROCESSING: платеж проводится
                COMPLETE: платеж завершен успешно
                CANCELLED: платеж завершен неуспешно
            Amount - сумма платежа
            CurrencyCode - 3-буквенный ISO код валюты
            IsTestPayment - признак тестового платежа (платеж совершен в тестовом режиме)
            LastUpdate (LastUpdateTime для JSON) - время последнего обновления статуса. Для завершенных платежей - время завершения платежа.
            PaymentAmount - сумма оплаты
            PaymentCurrencyCode - валюта оплаты
            PaymentID - идентификатор платежа
            PaymentSystemID - идентификатор платежной системы
            Purpose - примечание к платежу
            SiteID - идентификатор сайта - получателя платежа
            SiteInvoiceID - номер счета (параметр LMI_PAYMENT_NO)
            UserIdentifier - идентификатор пользователя в платежной системе
            UserPhoneNumber - номер телефона плательщика.

        :param payment_id:
        :return:
        """
        params = self._auth_params(
            {'paymentID': payment_id}, ['paymentID']
        )
        response = self._get('getPayment', params=params)
        return self._prepare_payment_data(response.json()['Payment'])

    def get_payment_by_invoice_id(self, invoice_id, merchant_id):
        """
        Проверка статуса по номеру счета
        Этот запрос используется для получения информации о платеже по его номеру в системе учета продавца.
            URL: https://paymaster.ru/partners/rest/getPaymentByInvoiceID
        Параметры запроса:
            invoiceID - номер счета (поле LMI_PAYMENT_NO)
            siteAlias - идентификатор сайта (поле LMI_MERCHANT_ID)
        Хешируемые параметры: login;password;nonce;invoiceID;siteAlias
        Параметры ответа: те же, что и для getPayment
        :param invoice_id:
        :param merchant_id:
        :return:
        """
        params = OrderedDict((
            ('invoiceID', invoice_id),
            ('siteAlias', merchant_id),
        ))
        params = self._auth_params(params, fields=params.keys())
        response = self._get('getPaymentByInvoiceID', params=params)
        return self._prepare_payment_data(response.json()['Payment'])

    def get_payments(self,
                     period_from=None,
                     period_to=None,
                     invoice_id=None,
                     state=None,
                     account_id=None,
                     merchant_id=None,
                     ):
        """
        Получение списка платежей
        Этот запрос используется для получения списка платежей, удовлетворяющих условиям поиска.
        URL: https://paymaster.ru/partners/rest/listPaymentsFilter
        Параметры запроса:
            accountID - номер учетной записи в системе PayMaster. Его можно узнать из URL страницы "Учетная запись" в личном кабинете. Параметр accountID можно не указывать, если у вас всего одна учетная запись.
            siteAlias - идентификатор сайта (LMI_MERCHANT_ID). Если указан, то будут возвращены только платежи данного сайта.
            periodFrom - начало периода (yyyy-MM-dd), часовой пояс UTC. Если указан, то будут возвращены платежи только после указанной даты.
            periodTo - конец периода (yyyy-MM-dd), часовой пояс UTC. Если указан, то будут возвращены платежи только до указанной даты.
            invoiceID - номер счета. Если указан, то будут возвращены платежи только с таким номером счета.
            state - состояние платежа. Если указано, то будут возвращены только платежи с указанным состоянием. Допустимые значения:
                INITIATED: платеж начат
                PROCESSING: платеж проводится
                COMPLETE: платеж завершен успешно
                CANCELLED: платеж завершен неуспешно
        Хешируемые параметры: login;password;nonce;accountID;siteAlias;periodFrom;periodTo;invoiceID;state. Учтите, что, если параметр не передается, в хеше нужно писать вместо него пустую строку.
        Параметры ответа:
            Response.Overflow - "true", если в ответе приведены не все платежи, удовлетворяющие фильтру. Если вам нужны все платежи, сузьте область поиска.
            Response.Payments - массив объектов, каждый из которых аналогичен объекту, возвращаемому по запросу getPayment.

        :param account_id:
        :return:
        """
        assert state is None or state in PaymentState

        params = OrderedDict((
            ('accountID', account_id),
            ('siteAlias', merchant_id),
            ('periodFrom', self._normalize_date(period_from)),
            ('periodTo', self._normalize_date(period_to)),
            ('invoiceID', invoice_id),
            ('state', state)
        ))
        params = self._auth_params(params, fields=params.keys())

        response = self._get('listPaymentsFilter', params=params)

        result = response.json()['Response']
        result['Payments'] = map(self._prepare_payment_data, result['Payments'])
        return result

    def refund_payment(self, payment_id, amount, external_id=None):
        """
        Возврат платежа
        Этот запрос используется для осуществления возврата по платежу.
        URL: https://paymaster.ru/partners/rest/refundPayment
        Параметры запроса:
            paymentID - идентификатор платежа в системе PayMaster
            amount - сумма возврата
            externalID - идентификатор возврата в системе продавца, не обязательный (допускается не уникальное значение)
        Хешируемые параметры: login;password;nonce;paymentID;amount;externalID.
        Параметры ответа:
            Response.ExternalID - идентификатор операции возврата;
            Response.PaymentID - идентификатор платежа;
            Response.Status - статус возврата:
                    "PENDING" - поставлен в очередь на совершение операции возврата
                    "EXECUTING" - проведение транзакции возврата платежа
                    "SUCCESS" - возврат средств успешно завершен
                    "FAILURE" - возврат средств не осуществлен
            Response.Amount - сумма возврата;
            Response.ErrorCode - код ошибки, если возврат неуспешен (может отсутствовать);
            Response.ErrorDesc - текстовое описание ошибки, если код ошибки отсутствует. В свою очередь описание также может отсутствовать, если о причинах отказа ничего не известно.

        :param payment_id:
        :param amount:
        :param external_id:
        :return:
        """
        params = OrderedDict((
            ('paymentID', payment_id),
            ('amount', amount),
            ('externalID', external_id),
        ))
        params = self._auth_params(params, fields=params.keys())

        response = self._get('refundPayment', params=params)

        return response.json()['Refund']

    def list_refunds(self,
                     period_from=None,
                     period_to=None,
                     payment_id=None,
                     account_id=None,
                     external_id=None,
                     ):
        """
        Получение списка возвратов
        Этот запрос используется для получения списка возвратов за период
            URL: https://paymaster.ru/partners/rest/listRefunds
        Параметры запроса:
            accountID - номер учетной записи в системе PayMaster
            paymentID - идентификатор платежа. Если присутствует, то выводятся возвраты только по этому платежу.
            periodFrom - начало периода (yyyy-mm-dd). Если отсутствует, то ограничения снизу нет.
            periodTo - конец периода, включительно (yyyy-mm-dd). Если отсутствует, то ограничения сверху нет.
            externalID - идентификатор возврата в системе продавца, не обязательный
        Хешируемые параметры: login;password;nonce;accountID;paymentID;periodFrom;periodTo;externalID. При этом, если параметр отсутствует, то в хешируемую строку вставляется пустая строка (т.е. будут две подряд точки с запятыми).
        Параметры ответа:
            Response.ErrorCode - код ошибки запроса (см. Коды ошибок )
            Response.Overflow: true, если выдан не весь список возвратов. В этом случае следует указать более узкий диапазон для поиска.
            Response.Refunds: список возвратов. Каждый объект - такой же, как и объект Response первого запроса.

        :param period_from: начало периода (yyyy-mm-dd). Если отсутствует, то ограничения снизу нет.
        :param period_to: конец периода, включительно (yyyy-mm-dd). Если отсутствует, то ограничения сверху нет.
        :param payment_id: идентификатор платежа. Если присутствует, то выводятся возвраты только по этому платежу.
        :param account_id: номер учетной записи в системе PayMaster
        :param external_id: идентификатор возврата в системе продавца, не обязательный
        :return:
        """
        params = OrderedDict((
            ('accountID', account_id),
            ('paymentID', payment_id),
            ('periodFrom', self._normalize_date(period_from)),
            ('periodTo', self._normalize_date(period_to)),
            ('externalID', external_id),
        ))
        params = self._auth_params(params, fields=params.keys())

        response = self._get('listRefunds', params=params)

        result = response.json()['Response']
        result['Refunds'] = map(self._prepare_refund_data, result['Refunds'])
        return result

    def confirm_payment(self, payment_id, amount=None):
        """
        Подтверждение платежа.
            Этот метод используется для успешного завершения платежа. В случае платежа на открытую сумму можно указать реальную сумму списания с пользователя.
            URL: https://paymaster.ru/partners/rest/ConfirmPayment
            Параметры запроса:
                paymentID - идентификатор платежа в системе PayMaster (поле LMI_SYS_PAYMENT_ID)
                amount  - реальная сумма списания
            Хешируемые параметры:
                login;password;nonce;paymentID;amount
        :param payment_id:
        :param amount:
        :return:
        """
        params = OrderedDict((
            ('paymentID', payment_id),
            ('amount', amount),
        ))
        params = self._auth_params(params, fields=params.keys())
        response = self._get('ConfirmPayment', params=params)
        return self._prepare_payment_data(response.json()['Payment'])

    def cancel_payment(self, payment_id, error=INVOICE_REJECTED):
        """
        Отмена платежа
            Этот запрос используется для отмены холда.
            URL: https://paymaster.ru/partners/rest/CancelPayment
        Параметры запроса:
            paymentID - идентификатор платежа в системе PayMaster (поле LMI_SYS_PAYMENT_ID)
            error - опциональный параметр. Код ошибки из списка ErrorCode.
        Хешируемые параметры:
            login;password;nonce;paymentID;error

        :param payment_id:
        :param error:
        :return:
        """
        params = OrderedDict((
            ('paymentID', payment_id),
            ('error', error),
        ))
        params = self._auth_params(params, fields=params.keys())
        response = self._get('CancelPayment', params=params)
        return self._prepare_payment_data(response.json()['Payment'])

    def documents(self, account_id=None, period_from=None, period_to=None):
        """
        Получение списка документов
        Этот запрос используется для получения списка документов за период:
            URL: https://paymaster.ru/partners/rest/listDocuments

        Параметры запроса:
            accountID - номер учетной записи в системе PayMaster. Его можно узнать из URL страницы "Учетная запись" в личном кабинете.
            periodFrom -начало периода (yyyy-MM-dd), часовой пояс UTC. Если указан, то будут возвращены документы, созданные только после указанной даты.
            periodTo - начало периода (yyyy-MM-dd), часовой пояс UTC. Если указан, то будут возвращены документы, созданные только до указанной даты.

        Хешируемые параметры:
            login;password;nonce;accountID;periodFrom;periodTo

        Параметры ответа:
            Created - дата создания документа
            Description - описание документа
            DocumentID - идентификатор для выгрузки содержимого
            FileName - имя файла

        :param account_id:
        :param period_from:
        :param period_to:
        :return:
        """
        params = OrderedDict((
            ('accountID', account_id),
            ('periodFrom', self._normalize_date(period_from)),
            ('periodTo', self._normalize_date(period_to)),
        ))
        params = self._auth_params(params, fields=params.keys())

        response = self._get('listDocuments', params=params)

        result = response.json()['Response']['Documents']
        for document in result:
            try:
                ts = float(re.findall("/Date\((\d+)\)/", document['Created'])[0]) / 1000
                document['Created'] = datetime.datetime.fromtimestamp(ts)
            except (IndexError, ValueError):
                pass
        return result

    def fetch_document(self, document_id):
        """
        Скачивание документа
        Этот запрос используется для скачивания документа по его идентификатору:
            URL: https://paymaster.ru/partners/rest/getDocumentContent
        Парметры запроса:
            documentID - идентификатор документа
         Хешируемые параметры:
            login;password;nonce;documentID
        :param document_id:
        :return: instance of requests.Response
        """
        params = OrderedDict((
            ('documentID', document_id),
        ))
        params = self._auth_params(params, fields=params.keys())
        response = self._get('getDocumentContent', params=params)
        return response
