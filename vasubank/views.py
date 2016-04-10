from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, render_to_response
from django import forms
from django.template import RequestContext,Context
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from vasubank.models import account,garbage,transaction,temporary


class LoginForm(forms.Form):
    username = forms.CharField(label=(u'username'))
    password = forms.CharField(label=(u'password'), widget=forms.PasswordInput(render_value=False))

@csrf_exempt
def LoginRequest(request):
    if request.user.is_authenticated():
        return HttpResponse('<script type="text/javascript">window.opener.location.reload(false);</script>')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponse(
                    '<script type="text/javascript">window.close();window.opener.location.reload(false);</script>')
            else:
                errors = form._errors.setdefault("no_field", form.error_class())
                errors.append("validation Error")
                return render_to_response('vasubank/login.html', {'form': form},
                                          context_instance=RequestContext(request))
        else:
            return render_to_response('vasubank/login.html', {'form': form}, context_instance=RequestContext(request))
    else:
        '''user is not submitting the form, show the login form'''
        form = LoginForm()
        context = {'form': form}
        return render_to_response('vasubank/login.html', context, context_instance=RequestContext(request))


def LogoutRequest(request):
    if request.user.is_authenticated():
        logout(request)
        return HttpResponseRedirect('/')


def TransactionDetails(request):
    if request.user.is_authenticated():
        a=request.POST.get('uid')
        b=request.POST.get('fees')
        c=request.POST.get('acct_num')
        temp=temporary(uuid=a,accnt_num=b,fees=c,user=request.user)
        temp.save()
        context = {
            'uid': a,
            'fees': b,
            'acct_num': c,
        }
        return render_to_response('vasubank/details.html',context,context_instance=RequestContext(request))
    else:
        return render('vasubank/invalid_trans.html')

def Payment(request):
    if request.user.is_authenticated():
        login_user=garbage.objects.filter(user=request.user)
        temp_obj=temporary.objects.filter(user=request.user)
        bank_acc=temp_obj.account.account_no
        cust_acc=login_user.account.account_no
        amt=temp_obj.fees
        t_t='F'
        t_s=0
        trans_id=12354564#random
        cust = account.objects.get(account_no=cust_acc)
        if cust is not None:
            if cust.cust_id.balance>amt:
                t_s=1
                bank=account.objects.get(account_no=bank_acc)
                if bank is not None:
                    bank.balance=bank.balance+amt
                    cust.balance=cust.balance-amt
                    trans=transaction(date=timezone.now(),account_from=cust,
                                   account_to=bank,
                                   transaction_type=t_t,
                                   transaction_status=t_s,
                                   transaction_id=trans_id)
                    trans.save()
                    cust.save()
                    bank.save()
                    t_s=2
                    transu=transaction.objects.get(transaction_id=trans_id)
                    transu.transaction_status=t_s
                    transu.save()
                else:
                    t_s=3
            else:
                t_s=3
        else:
            t_s=3
        args = {'status':t_s}
        print args
        return render_to_response('vasubank/payment_status.html',args)
    else:
        return render('vasubank/invalid_trans.html')


#print str(request.POST.get('uid'))
