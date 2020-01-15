from django.conf.urls import url, include

from .views import init_payment

urlpatterns = [
    url(r'^payments/', include('payments.urls')),
    url(r'^init/(?P<payment_id>\d+)/$', init_payment)
]
