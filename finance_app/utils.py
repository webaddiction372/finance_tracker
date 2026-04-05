from datetime import date
from calendar import monthrange
from django.db.models import Sum
from .models import Transaction, Budget

def month_bounds(target: date):
    first = target.replace(day=1)
    last = target.replace(day=monthrange(target.year, target.month)[1])
    return first, last

def spending_by_category(user, target: date):
    start, end = month_bounds(target)
    qs = (Transaction.objects
          .filter(user=user, date__range=(start, end), is_income=False)
          .values('category__name')
          .annotate(total=Sum('amount'))
          .order_by('-total'))
    return list(qs)

def income_total(user, target: date):
    start, end = month_bounds(target)
    return (Transaction.objects
            .filter(user=user, date__range=(start, end), is_income=True)
            .aggregate(total=Sum('amount'))['total'] or 0)

def expense_total(user, target: date):
    start, end = month_bounds(target)
    return (Transaction.objects
            .filter(user=user, date__range=(start, end), is_income=False)
            .aggregate(total=Sum('amount'))['total'] or 0)

def budget_usage(user, target: date):
    start, end = month_bounds(target)
    spent = (Transaction.objects
             .filter(user=user, date__range=(start, end), is_income=False)
             .values('category')
             .annotate(total=Sum('amount')))
    spent_map = {row['category']: row['total'] for row in spent}
    rows = []
    budgets = Budget.objects.filter(month=start).select_related('category')
    for b in budgets:
        total_spent = spent_map.get(b.category_id, 0) or 0
        pct = float(total_spent / b.amount * 100) if b.amount else 0.0
        rows.append({'category': b.category.name, 'budget': b.amount, 'spent': total_spent, 'percent': round(pct, 2)})
    return rows
