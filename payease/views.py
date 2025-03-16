from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import json
from django.template.loader import render_to_string
from django.db.models import Q
from datetime import timedelta
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from .models import Laborer, Payment, Transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone


@csrf_exempt
def register_laborer(request):
    
    if request.method == 'POST':
        try:
            
            data = json.loads(request.body)
            start_date = datetime.fromisoformat(data['start_date']) 
            if start_date.hour == 0 and start_date.minute == 0 and start_date.second == 0 and start_date.microsecond == 0:
                current_time = timezone.localtime(timezone.now())

                start_date = start_date.replace(hour=current_time.hour, minute=current_time.minute, 
                                     second=current_time.second, microsecond=current_time.microsecond)
    
            laborer = Laborer(
                name=data['name'],
                phone=data['phone'],
                role=data['role'],
                salary=float(data['salary']),
                rate = round(float(data['salary'])/30,2),
                rate_type=data['rate_type'],
                start_date=start_date 
            )
            laborer.save()
            
            payment = Payment(
                laborer=laborer,  
                start_date= start_date,
                end_date= start_date ,
                days_worked=0, 
                total_amount=0, 
                payment_status='pending' 
            )
            payment.save()
            return JsonResponse({"message": "Laborer Registered Successfully!"}, status=201)

        except json.JSONDecodeError:
            print("JSON Decode Error: Invalid JSON format")
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        except Exception as e:
            print("Error in register_laborer:", str(e))  # Log error
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, "Form.html")

    
def dashboard(request):
    
    query = request.GET.get('q', '').strip()
    sort_option = request.GET.get('sort', 'Newest')
    
    if query:
            laborers = Laborer.objects.filter(
            Q(name__icontains=query) | 
            Q(role__icontains=query) |
            Q(salary__icontains=query) |
            Q(phone__icontains=query) |
            Q(start_date__icontains=query) |
            Q(payment__payment_status__icontains=query) |
            Q(status__icontains=query)) 
            print(laborers)
        
    else:
         
     laborers = Laborer.objects.all()
     
    if sort_option == 'Newest':
        print('sort_option is newest')
        laborers = laborers.order_by('-start_date')
    elif sort_option == 'Oldest':
        print('sort_optino is oldest')
        laborers = laborers.order_by('start_date')
    elif sort_option == 'Highest_Salary':
        print('sort_optino is highest salary')
        laborers = laborers.order_by('-salary')
    elif sort_option == 'Lowest_Salary':
        print('sort_optino is lowest salary')
        laborers = laborers.order_by('salary')
    payments_to_update = []
    for laborer in laborers:
      
        payment = Payment.objects.filter(laborer = laborer).first()
        
        if laborer.status == "Active":
            print('the status is active')
            laborer.loan = round(Transaction.objects.filter(laborer = laborer, type_of_payment='Loan', status = 'Active').aggregate(total_loan=Sum('paid_amount'))['total_loan'] or 0, 2)
            if laborer.start_date.tzinfo is None:
                laborer_start_date = timezone.make_aware(laborer.start_date, timezone.get_current_timezone())
            else:
                laborer_start_date = laborer.start_date

            current_time = timezone.now()
            

            time_worked = current_time - laborer_start_date
            seconds_worked = time_worked.total_seconds()
            salary_per_second = laborer.rate / (24 * 60 * 60)
            
            if payment:

              payment.total_amount = round(round(seconds_worked * salary_per_second, 1) - laborer.loan - payment.paid_amount,1)
              payment.days_worked = round(seconds_worked / (24*60*60),1)
              payment.save()
              payments_to_update.append(payment)
              
        elif laborer.status == 'Re-enable':
            
            laborer.deducted_loan = float(laborer.deducted_loan) if laborer.deducted_loan else 0
            laborer.loan = round(Transaction.objects.filter(laborer = laborer, type_of_payment='Loan', status = 'Re-enable').aggregate(total_loan=Sum('paid_amount'))['total_loan'] or 0, 2)
            new_loan_to_deduct = laborer.loan - laborer.deducted_loan
            laborer_re_start_date = laborer.re_start_date + timedelta(hours=3)
            laborer.start_date = laborer_re_start_date
            laborer.save()
            print(f'Laborer re start date {laborer_re_start_date}')
            time_zone_updated = timezone.now() + timedelta(hours = 3)
            time_worked = time_zone_updated - laborer_re_start_date
            seconds_worked = time_worked.total_seconds()
            salary_per_second = laborer.rate / (24 * 60 * 60)
                    
            if payment:

              payment.total_amount = round(payment.after_paid_amount + round(seconds_worked * salary_per_second, 1) - laborer.loan, 1)
              payment.days_worked = round(seconds_worked / (24*60*60),1)
              print(f'laborer loan is {laborer.loan}')
              print('Payment after paid amount')
              print(payment.after_paid_amount)
              print('Laborer after loan amount')
              print(laborer.after_loan_amount)
              print('new_loan_to_deduct')
              print(new_loan_to_deduct)
              print('payment total amount')
              payment.save()
              payments_to_update.append(payment)
              
            
        else:
            if payment:
              print(laborer.status)
              print('the payment is not clicked enable or re-enable')
              laborer.loan = round(Transaction.objects.filter(laborer = laborer, type_of_payment='Loan', status = 'Re-enable').aggregate(total_loan=Sum('paid_amount'))['total_loan'] or 0, 2)
              payment.total_amount = payment.total_amount
              payment.save()
              payments_to_update.append(payment)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('laborer_table_rows.html', {'laborers': laborers, 'payments': payments_to_update})
        return JsonResponse({'html': html})

    return render(request, 'Payease.html', {'laborers': laborers,
                                            'payments': payments_to_update})
    

@csrf_exempt

def terminate_contract(request, laborer_id):
  
    laborer = get_object_or_404(Laborer, id=laborer_id)
    payment = get_object_or_404(Payment, laborer = laborer)

    if request.method == "POST":
      laborer.status = 'Terminated'
      laborer.save()
      payment.payment_status = 'paid'
      payment.save()

      print(laborer.status)
      return redirect('dashboard')
    
    
    return JsonResponse({"error": "Invalid request method"}, status=400)
  

@csrf_exempt

def amount_to_pay (request, laborer_id):
    
    laborer = get_object_or_404(Laborer, id = laborer_id)
    payment = get_object_or_404(Payment, laborer = laborer)
    if request.method == "POST":
        payment.paid_amount = abs(int(request.POST.get('amount_to_pay')))
        payment.after_paid_amount = round(float(payment.total_amount) - float(payment.paid_amount),2)
        payment.total_amount = round(payment.after_paid_amount,1)
        payment.save()
        transaction_history = Transaction (
            laborer = laborer,
            payment = payment,
            name = laborer.name,
            role = laborer.role,
            validity = 'Done',
            type_of_payment = 'Salary',
            start_date = laborer.re_start_date,
            paid_amount = payment.paid_amount,
        )
        transaction_history.save()
        return redirect('dashboard')
        
    return render(request, 'Payment-card.html', {'laborer': laborer, 'payment': payment})


def amount_to_loan(request, laborer_id):
    laborer = get_object_or_404(Laborer, id = laborer_id)
    payment = get_object_or_404(Payment, laborer = laborer)
    
    if request.method == "POST":
        new_loan =  float(request.POST.get('amount_to_loan'))
        laborer.after_loan_amount = round(float(payment.total_amount) - float(new_loan),2)
        payment.total_amount = round(laborer.after_loan_amount,1)
        
        laborer.save()
        payment.save()

        transaction_history = Transaction (
            laborer = laborer,
            payment = payment,
            name = laborer.name,
            role = laborer.role,
            validity = 'Done',
            type_of_payment = 'Loan',
            start_date = laborer.re_start_date,
            paid_amount = new_loan,
            status = laborer.status
        )
        transaction_history.save()
        laborer.deducted_loan = laborer.loan 
        laborer.save()
        return redirect('dashboard')
        
    return render(request, 'Loan-card.html', {'laborer': laborer, 'payment': payment})


    
def activate_contract(request, laborer_id):
  
    laborer = get_object_or_404(Laborer, id=laborer_id)
    payment = get_object_or_404(Payment, laborer = laborer)

    if request.method == "POST":
        
      re_enable_time_str = request.POST.get("re_enable_time")
      re_enable_time = timezone.datetime.fromisoformat(re_enable_time_str)
      re_enable_time = timezone.make_aware(re_enable_time)
      laborer.re_start_date = re_enable_time
      laborer.status = 'Re-enable'
      laborer.loan = 0
      print(laborer.status)
      payment.payment_status = 'pending'
      payment.total_amount = payment.total_amount
      laborer.status = 'Re-enable'
      laborer.save()  
      payment.save()
    

      print(laborer.status)
      return redirect('dashboard')
    
    
    return JsonResponse({"error": "Invalid request method"}, status=400)



def delete_laborer(request, laborer_id):
    
    laborer = get_object_or_404(Laborer, id = laborer_id)
    print(laborer)
    payment = get_object_or_404(Payment, laborer = laborer)

    laborer.delete()
    return redirect('dashboard')

@csrf_exempt

def transaction_history(request):
    transactions = Transaction.objects.filter()
    laborers_total_number = Laborer.objects.count()
    
    sort_option = request.GET.get('sort', 'Newest')
    
    if sort_option == 'Newest':
        print('sort_option is newest')
        transactions = transactions.order_by('-start_date')
    elif sort_option == 'Oldest':
        print('sort_optino is oldest')
        transactions = transactions.order_by('start_date')
    elif sort_option == 'Highest_Paid':
        print('sort_optino is highest paid')
        transactions = transactions.order_by('-paid_amount')
    elif sort_option == 'Lowest_Paid':
        print('sort_optino is lowest paid')
        transactions = transactions.order_by('paid_amount')
    elif sort_option == 'Payment_Type':
        print('sort_optino is payment type')
        transactions = transactions.order_by('type_of_payment')
    print(laborers_total_number)
    transaction_data = []
    context = []
    if Transaction.objects.count() > 0:
        total_paid = abs(round(Transaction.objects.filter(type_of_payment='Salary').aggregate(total_paid=Sum('paid_amount'))['total_paid'] or 0, 2))

        total_loan = round(Transaction.objects.filter(type_of_payment='Loan').aggregate(total_loan=Sum('paid_amount'))['total_loan'] or 0, 2)

        for transaction in transactions:
            
            transaction_data.append( {
                'name' : transaction.name,
                'role' : transaction.role,
                'validity': transaction.validity,
                'start_date': transaction.start_date,
                'paid_amount': transaction.paid_amount,
                'type_of_payment': transaction.type_of_payment,
            })
            
            context = {
                
            'total': laborers_total_number,
            'total_paid': total_paid,
            'total_loan': total_loan,
            }
            
    
    return render(request, 'Transaction.html', {
        'transaction_data': transaction_data,
        'context': context
    })
    