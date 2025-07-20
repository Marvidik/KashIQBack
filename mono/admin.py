# admin.py
from django.contrib import admin
from .models import Account, Transaction

class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    fields = ('txn_id', 'amount', 'type', 'date')
    readonly_fields = ('txn_id', 'amount', 'type', 'date')
    can_delete = False
    show_change_link = True

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    inlines = [TransactionInline]
    list_display = ('user','bank')  # customize based on your Account model
