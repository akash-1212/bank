from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from decimal import Decimal

class customer(models.Model) :
    GENDER_CHOICES =( ('M','Male'),('F','Female'),)
    cust_id=models.CharField(max_length=15,primary_key=True)
    cust_name=models.CharField(max_length=100)
    cust_addr=models.CharField(max_length=100)
    cust_phone=models.CharField(max_length=13)
    cust_dob=models.DateField()
    cust_gender=models.CharField(max_length=1,choices=GENDER_CHOICES)
    cust_email=models.EmailField()

class account(models.Model) :
    ACCOUNT_TYPE = ( ('S','Saving'),('F','Fixed'),)
    account_no=models.CharField(primary_key=True,max_length=12)
    cust_id=models.ForeignKey(customer)
    account_type=models.CharField(max_length=1,choices=ACCOUNT_TYPE)
    balance=models.DecimalField(decimal_places=10,default=Decimal("0.00"),max_digits=18)

class atm_card(models.Model) :
    atm_card_no=models.CharField(max_length=16)
    account_no=models.ForeignKey(account)

class transaction(models.Model) :
    TRANSACTION_TYPE= ( ('W','Withdraw'),('D','Deposit'),('F','Fund-Transfer'))
    TRANSACTION_STATUS = ( ('0','Executed'),('1','Pending'),('2','Success'),('3','Cancelled'),)
    date=models.DateField(auto_now=True)
    account_from=models.ForeignKey(account)
    account_to=models.CharField(max_length=12)
    transaction_type=models.CharField(max_length=1,choices=TRANSACTION_TYPE)
    transaction_status=models.CharField(max_length=1,choices=TRANSACTION_STATUS,default=None)
    transaction_id=models.CharField(max_length=15,unique=True)

class garbage(models.Model) :
    account_no=models.ForeignKey(account)
    user=models.ForeignKey(User)

class temporary(models.Model) :
    uuid=models.CharField(max_length=25)
    account_no=models.ForeignKey(account)
    fees=models.CharField(max_length=8)
    user=models.ForeignKey(User)


