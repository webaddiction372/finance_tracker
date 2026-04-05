from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.contrib.admin import display

from .admin_site import finance_admin_site
from .models import Budget, Category, Transaction


@admin.register(Category, site=finance_admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category_kind", "transaction_count", "budget_count")
    search_fields = ("name",)
    ordering = ("name",)

    @display(description="Type")
    def category_kind(self, obj):
        return "Expense" if obj.is_expense else "Income"

    @display(description="Transactions")
    def transaction_count(self, obj):
        return obj.transactions.count()

    @display(description="Budgets")
    def budget_count(self, obj):
        return obj.budgets.count()


@admin.register(Budget, site=finance_admin_site)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("category", "month", "amount")
    list_filter = ("month", "category")
    search_fields = ("category__name",)
    date_hierarchy = "month"
    list_select_related = ("category",)
    ordering = ("-month", "category__name")


@admin.register(Transaction, site=finance_admin_site)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "description", "user", "category", "entry_type", "amount_display")
    list_filter = ("is_income", "category", "date", "user")
    search_fields = ("description", "category__name", "user__username", "user__email")
    list_select_related = ("user", "category")
    date_hierarchy = "date"
    ordering = ("-date", "-id")
    readonly_fields = ("signed_amount_preview",)
    fieldsets = (
        ("Transaction Details", {"fields": ("user", "date", "description", "category")}),
        ("Financial Data", {"fields": ("amount", "is_income", "signed_amount_preview")}),
    )

    @display(description="Type")
    def entry_type(self, obj):
        return "Income" if obj.is_income else "Expense"

    @display(description="Signed Amount")
    def amount_display(self, obj):
        sign = "+" if obj.is_income else "-"
        return f"{sign}{obj.amount}"

    @display(description="Signed Preview")
    def signed_amount_preview(self, obj):
        if not obj.pk:
            return "The signed amount will appear after the transaction is saved."
        sign = "+" if obj.is_income else "-"
        return f"{sign}{obj.amount}"


finance_admin_site.register(User, UserAdmin)
finance_admin_site.register(Group, GroupAdmin)
