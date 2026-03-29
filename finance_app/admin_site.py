from datetime import date

from django.contrib.admin import AdminSite
from django.db.models import Sum

from .models import Budget, Category, Transaction


class FinanceAdminSite(AdminSite):
    site_header = "Finance Tracker Admin"
    site_title = "Finance Tracker Admin"
    index_title = "Operations Dashboard"
    site_url = "/"
    index_template = "admin/index.html"
    app_index_template = "admin/app_index.html"

    def each_context(self, request):
        context = super().each_context(request)
        today = date.today()
        month_start = today.replace(day=1)

        income_total = (
            Transaction.objects.filter(is_income=True, date__gte=month_start, date__lte=today)
            .aggregate(total=Sum("amount"))
            .get("total")
            or 0
        )
        expense_total = (
            Transaction.objects.filter(is_income=False, date__gte=month_start, date__lte=today)
            .aggregate(total=Sum("amount"))
            .get("total")
            or 0
        )
        recent_transactions = Transaction.objects.select_related("category")[:6]
        active_budgets = Budget.objects.filter(month=month_start).select_related("category")

        context.update(
            {
                "dashboard_stats": [
                    {"label": "Categories", "value": Category.objects.count(), "note": "Configured transaction groups"},
                    {"label": "Budgets", "value": Budget.objects.count(), "note": "Budget plans across months"},
                    {"label": "Transactions", "value": Transaction.objects.count(), "note": "Ledger entries recorded"},
                    {"label": "Net This Month", "value": income_total - expense_total, "note": "Income minus expenses"},
                ],
                "dashboard_month": month_start,
                "dashboard_income": income_total,
                "dashboard_expense": expense_total,
                "dashboard_recent_transactions": recent_transactions,
                "dashboard_active_budgets": active_budgets[:6],
            }
        )
        return context


finance_admin_site = FinanceAdminSite(name="finance_admin")
