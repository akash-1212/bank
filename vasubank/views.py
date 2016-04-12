import hashlib
import random
from decimal import Decimal

from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from vasubank.models import transaction, temporary, account_user_map, temp_user_map, account_inst_map


class LoginForm(forms.Form):
    username = forms.CharField(label=(u'username'))
    password = forms.CharField(label=(u'password'), widget=forms.PasswordInput(render_value=False))


def randomword():
    choose = "qwertyuiopasdfghjklzxcvbnm1234567890AQWSEDRFTGYHUJIKOLPZXCVBNM"
    return ''.join(random.choice(choose) for i in range(25))


# @csrf_exempt
def LoginRequest(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/vasubank/history')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/vasubank/history')
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


def print_history(request):
    if request.user.is_authenticated():
        print("in post")
        login_user = account_user_map.objects.filter(user=request.user)[0]
        cust_acc = login_user.account_no
        trans = transaction.objects.filter(
            Q(account_from=cust_acc) | Q(account_to=cust_acc.account_no))  # can be taken from session
        # print trans
        # for t in trans:
        print("in get")
        args = {'trans': trans}
        print(args)
        return render_to_response('vasubank/print_history.html', args)
    else:
        HttpResponseRedirect('insti/login/')



@csrf_exempt
def TransactionInitialise(request):
    # if request.user.is_authenticated():
    id = request.POST.get('uid')
    fee = request.POST.get('fees')
    college_id = request.POST.get('college_id')
    hush = request.POST.get('hash')
    m = hashlib.sha512()
    m.update(str(id).encode('utf-8'))
    m.update(str(fee).encode('utf-8'))
    m.update(str(college_id).encode('utf-8'))
    # print(hush + str(type(hush))+'         '+ m.hexdigest() + str(type(m.hexdigest())))
    print(str(hush))
    print(m.hexdigest())
    if str(hush) == str(m.hexdigest()):
        print(college_id)
        acct = account_inst_map.objects.filter(institute_id=college_id)[0].account_no
        # acct = account.objects.get(pk=acc_no)
        # user=uuid.uuid()
        print(id)
        temp = temporary(uuid=id, account_no=acct, fees=fee)
        # temp=temporary(uuid=a,accnt_num=b,fees=c,user=user)
        temp.save()
        context = {
            'id': id,
            'form': LoginForm()
        }
        return render_to_response('vasubank/payment_login.html', context, context_instance=RequestContext(request))

    context = {
        'message': 'DATA has been Tempered.',
    }
    return render_to_response('vasubank/invalid_trans.html', context, context_instance=RequestContext(request))


def TransactionDetails(request):
    # if request.user.is_authenticated():
    username = request.POST.get('username')
    password = request.POST.get('password')
    id = request.POST.get('id')
    # user=uuid.uuid()
    form = LoginForm(request.POST)
    print(str(form))
    print(username + password)
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        temp_obj = temporary.objects.filter(uuid=id)[0]
        print(str(user.username))
        act_obj = account_user_map.objects.filter(user=user)[0].account_no.cust_id.cust_name
        context = {
            'from_name': act_obj,
            'to_name': temp_obj.account_no.cust_id.cust_name,
            'fees': temp_obj.fees,
        }
        temp_user_obj = temp_user_map(user=user, temp=temp_obj).save()
        return render_to_response('vasubank/details.html', context, context_instance=RequestContext(request))
    else:
        errors = form._errors.setdefault("no_field", form.error_class())
        errors.append("validation Error")
        context = {
            'id': id,
            'form': form
        }
        return render_to_response('vasubank/payment_login.html', context, context_instance=RequestContext(request))



        # else:
        #     return render_to_response('vasubank/invalid_trans.html')


def CancelPayment(request):
    if request.user.is_authenticated():
        temp_user_map_obj = temp_user_map.objects.filter(user=request.user)[0]
        temp_obj = temp_user_map_obj.temp
        temp_user_map_obj.delete()
        # temp_obj.delete()
        args = {'status': '3', 'uid': temp_obj.uuid}
        print(args)
        return render_to_response('vasubank/payment_status.html', args)


def Payment(request):
    if request.user.is_authenticated():
        login_user = account_user_map.objects.filter(user=request.user)[0]
        temp_user_map_obj = temp_user_map.objects.filter(user=request.user)[0]
        temp_obj = temp_user_map_obj.temp
        temp_user_map_obj.delete()
        bank_acc = temp_obj.account_no
        cust_acc = login_user.account_no
        amt=Decimal(temp_obj.fees)
        t_t='F'
        t_s=0
        trans_id = 'TXN' + randomword()  # random
        # cust = account.objects.get(account_no=cust_acc)
        if cust_acc is not None:
            if cust_acc.balance>amt:
                t_s=1
                # bank=account.objects.get(account_no=bank_acc)
                if bank_acc is not None:
                    bank_acc.balance=bank_acc.balance+amt
                    cust_acc.balance=cust_acc.balance-amt
                    trans=transaction(date=timezone.now(),account_from=cust_acc,
                                   account_to=bank_acc.account_no,
                                   transaction_type=t_t,
                                   transaction_status=t_s,
                                   transaction_id=trans_id)
                    trans.save()
                    cust_acc.save()
                    bank_acc.save()
                    t_s=2
                    print(str(t_s))
                    trans.transaction_status=t_s
                    trans.save()
                else:
                    t_s=3
            else:

                t_s=3
        else:
            t_s=3
        args = {'status':t_s,'uid':temp_obj.uuid,'t_id':trans_id}
        print(args)
        return render_to_response('vasubank/payment_status.html',args)
    else:
        return render_to_response('vasubank/invalid_trans.html')


#print str(request.POST.get('uid'))
