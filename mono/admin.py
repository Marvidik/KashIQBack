from django.contrib import admin
from .models import Account, Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('txn_id', 'account', 'amount', 'type', 'date', 'currency')
    list_filter = ('type', 'currency', 'account')
    search_fields = ('txn_id', 'narration', 'account__user__username')
    ordering = ('-date',)
    actions = ['delete_selected']  # Optional: default Django bulk delete


# ✅ Custom action to delete all transactions for selected accounts
@admin.action(description="🗑 Delete all transactions for selected accounts")
def delete_transactions_for_accounts(modeladmin, request, queryset):
    account_ids = queryset.values_list('id', flat=True)
    deleted_count, _ = Transaction.objects.filter(account_id__in=account_ids).delete()
    modeladmin.message_user(request, f"Successfully deleted {deleted_count} transactions.")


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'acct_name', 'bank', 'acct_number', 'type', 'balance', 'linked_on')
    search_fields = ('user__username', 'acct_name', 'bank', 'acct_number')
    list_filter = ('bank', 'type')
    actions = [delete_transactions_for_accounts]
