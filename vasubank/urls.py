from django.conf.urls import url

from vasubank.views import LoginRequest, LogoutRequest, Payment, TransactionDetails, TransactionInitialise, \
    CancelPayment, print_history

urlpatterns = [
    url(r'^login/$', LoginRequest),
    url(r'^logout/$', LogoutRequest),
    url(r'^connectbank/$', TransactionInitialise, name="details"),
    url(r'^details/$', TransactionDetails, name="details"),
    url(r'^payment/$', Payment, name="pay"),
    url(r'^cancelpayment/$', CancelPayment, name="cancel pay"),
    url(r'^history/$', print_history, name="pay"),
]
