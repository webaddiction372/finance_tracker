from datetime import date
from django.core.management.base import BaseCommand
from django.db.models import Sum
from finance_app.models import Budget, Transaction


class Command(BaseCommand):
    help = 'Checks budget usage for the current month and prints warnings for overspending.'

    def handle(self, *args, **options):
        today = date.today()
        start = today.replace(day=1)

        budgets = Budget.objects.filter(month=start).select_related('category')
        if not budgets.exists():
            self.stdout.write(self.style.WARNING('No budgets defined for this month.'))
            return

        spent = (Transaction.objects
                 .filter(is_income=False, date__gte=start, date__lte=today)
                 .values('category')
                 .annotate(total=Sum('amount')))
        spent_map = {row['category']: row['total'] for row in spent}

        for b in budgets:
            used = spent_map.get(b.category_id, 0) or 0
            if used >= b.amount:
                self.stdout.write(self.style.ERROR(f"OVER BUDGET: {b.category.name} used {used} / {b.amount}"))
            else:
                pct = float(used / b.amount * 100) if b.amount else 0.0
                self.stdout.write(self.style.SUCCESS(f"{b.category.name}: {used} / {b.amount} ({pct:.1f}%)"))
