from django.conf.urls import url

from vasubank.views import LoginRequest,LogoutRequest,Payment,TransactionDetails

urlpatterns = [
    url(r'^login/$', LoginRequest),
    url(r'^logout/$', LogoutRequest),
    url(r'^details/$', TransactionDetails,name="details"),
    url(r'^payment/$', Payment,name="pay"),
]
