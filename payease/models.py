from django.db import models
from datetime import datetime

class Laborer(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    rate = models.FloatField()
    salary = models.FloatField(default='0')
    loan = models.FloatField(default = '0')
    after_loan_amount = models.FloatField(default= '0')
    deducted_loan = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Already deducted loan

    RATE_CHOICES = [
        ("daily", "Daily"),
        ("hourly", "Hourly"),
        ("minute", "Minute"),
        ("second", "Second"),
    ]
    rate_type = models.CharField(max_length=10, choices=RATE_CHOICES, default="daily")
    start_date = models.DateTimeField()
    re_start_date = models.DateTimeField(default = datetime.now)
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Terminated", "Terminated"),
        ("Re-enable", "Re-enable"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Active")

    def __str__(self):
        return self.name


class Payment(models.Model):
    laborer = models.ForeignKey(Laborer, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    days_worked = models.FloatField()
    total_amount = models.FloatField()
    after_paid_amount = models.FloatField(default= '0')
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
    ]
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default="pending")
    paid_amount = models.FloatField(default='0')


    def __str__(self):
        return f"Payment for {self.laborer.name}"


class Transaction(models.Model):
    laborer = models.ForeignKey(Laborer, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    VALIDITY_CHOICES  = [
        ("Done", "Done"),
        ("Undone", "Undone")
    ]
    TYPE_OF_PAYMENT = [
        ('Loan', 'Loan'),
        ('Salary', 'Salary')
    ]
    validity = models.CharField(choices=VALIDITY_CHOICES, default= 'Done', max_length=10)
    role = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    paid_amount = models.FloatField()
    type_of_payment = models.CharField(max_length=10, choices = TYPE_OF_PAYMENT, default='Salary' )
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Terminated", "Terminated"),
        ("Re-enable", "Re-enable"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Active")



    