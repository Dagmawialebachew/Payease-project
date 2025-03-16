from django.contrib import admin
from .models import Laborer, Payment, Transaction

class LaborerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'role', 'rate', 'loan' ,'rate_type', 'start_date', 'status', 're_start_date', 'deducted_loan')
    
admin.site.register(Laborer, LaborerAdmin)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('laborer', 'start_date', 'end_date', 'days_worked', 'total_amount', 'payment_status', 'paid_amount', 'after_paid_amount')
    
admin.site.register(Payment, PaymentAdmin)

class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'validity', 'start_date', 'paid_amount', 'type_of_payment', 'status')
    
admin.site.register(Transaction, TransactionHistoryAdmin)

