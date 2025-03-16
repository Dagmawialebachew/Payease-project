
from django.contrib import admin
from django.urls import path,include
from payease import views

urlpatterns = [
    path('register-laborer/', views.register_laborer, name='register_laborer'),
    path('terminate-contract/<str:laborer_id>/', views.terminate_contract, name='terminate_contract'),
    path('activate-contract/<str:laborer_id>/', views.activate_contract, name='activate_contract'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('amount-to-pay/<str:laborer_id>/', views.amount_to_pay, name='amount_to_pay'),
    path('transaction_history', views.transaction_history, name = 'transaction_history'),
    path('amount-to-loan/<str:laborer_id>/', views.amount_to_loan, name = 'amount_to_loan'),
    path('delete_laborer/<str:laborer_id>/', views.delete_laborer, name = 'delete_laborer')
    
]
