from tests.models import Payment


def test_payment(browser, live_server):
    payment = Payment.objects.create(
        variant='paymaster',
        total='1234.50',
        currency='RUB',
    )
    browser.visit(live_server.url + f'/init/{payment.id}/')
    assert payment
