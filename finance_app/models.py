from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_expense = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Budget(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField(help_text='Use first day of month (e.g., 2025-09-01)')

    class Meta:
        unique_together = ('category', 'month')
        ordering = ['-month', 'category__name']

    def __str__(self):
        return f"{self.category.name} - {self.month:%b %Y}: {self.amount}"

class Transaction(models.Model):
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text='Expenses are positive; refunds as negative.')
    is_income = models.BooleanField(default=False, help_text='Tick for income; untick for expense.')

    class Meta:
        ordering = ['-date', '-id']

    def signed_amount(self):
        return self.amount if self.is_income else -self.amount

    def __str__(self):
        return f"{self.date} {self.description} ({'Income' if self.is_income else 'Expense'}) {self.amount}"
