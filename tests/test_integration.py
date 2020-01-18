import os
from urllib.parse import urlparse

import pytest
from payments import PaymentStatus
from payments.core import provider_factory

from payments_paymaster import PaymasterProvider
from tests.models import Payment


def test_hidden_fields(settings):
    settings.LIVE_PAYMENT_HOST = 'example.com'
    payment = Payment.objects.create(
        variant='paymaster',
        total='1234.50',
        currency='RUB',
    )
    provider: PaymasterProvider = provider_factory(payment.variant)
    hidden_data = provider.get_hidden_fields(payment)

    assert hidden_data['PAYMENT_TOKEN'] == payment.token
    assert settings.LIVE_PAYMENT_HOST in hidden_data['LMI_SUCCESS_URL']


def test_settings(settings):
    assert os.environ.get('PAYMASTER_CLIENT_ID')
    assert os.environ.get('PAYMASTER_SECRET')
    assert settings.PAYMENT_VARIANTS['paymaster'][1]['client_id'] is not None
    assert settings.PAYMENT_VARIANTS['paymaster'][1]['secret'] is not None


@pytest.mark.webtest()
def test_payment(browser, live_server_ngrok, settings):
    remote_url = live_server_ngrok.url
    host = urlparse(remote_url).netloc
    settings.DEBUG = True
    settings.ALLOWED_HOSTS = [
        'localhost',
        host
    ]
    settings.LIVE_PAYMENT_HOST = host
    payment = Payment.objects.create(
        variant='paymaster',
        total='1234.50',
        currency='RUB',
    )
    browser.visit(remote_url + f'/init/{payment.id}/')
    browser.find_by_css("input[type='submit']").first.click()
    browser.wait_for_condition(lambda b: b.find_by_name('card_pan'))
    browser.fill('card_pan', '4100000000000010')
    browser.fill('card_month', '01')
    browser.fill('card_year', '25')
    browser.fill('card_cvv', '000')
    browser.fill('notificationSink', 'example@example.com')
    browser.find_by_css('#proceed').first.click()
    browser.wait_for_condition(
        lambda b: b.find_by_css('#returnToMerchant').visible,
        timeout=30
    )
    browser.find_by_css('#returnToMerchant').first.click()
    browser.wait_for_condition(
        lambda b: urlparse(b.url).netloc == 'example.com',
        timeout=30)
    payment.refresh_from_db()
    assert payment.status == PaymentStatus.CONFIRMED
    assert payment.captured_amount == payment.total
