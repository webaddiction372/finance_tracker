from datetime import date
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth.views import LoginView
from .models import Transaction, Category
from .forms import BudgetForm, CategoryForm, RegisterForm, StyledAuthenticationForm, TransactionForm
from .utils import spending_by_category, income_total, expense_total, budget_usage

class UserLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    authentication_form = StyledAuthenticationForm


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('finance_app:transaction_list')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('finance_app:transaction_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Your account has been created successfully.')
        return response


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    paginate_by = 20
    template_name = 'finance_app/transaction_list.html'

    def get_queryset(self):
        qs = super().get_queryset().select_related('category')
        q = self.request.GET.get('q')
        cat = self.request.GET.get('category')
        date_from = self.request.GET.get('from')
        date_to = self.request.GET.get('to')
        ttype = self.request.GET.get('type')  # income/expense/all

        if q:
            qs = qs.filter(Q(description__icontains=q))
        if cat:
            qs = qs.filter(category_id=cat)
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        if ttype == 'income':
            qs = qs.filter(is_income=True)
        elif ttype == 'expense':
            qs = qs.filter(is_income=False)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        ctx['query'] = self.request.GET
        return ctx

class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'finance_app/transaction_form.html'
    success_url = reverse_lazy('finance_app:transaction_list')

class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'finance_app/transaction_form.html'
    success_url = reverse_lazy('finance_app:transaction_list')

class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = 'finance_app/transaction_confirm_delete.html'
    success_url = reverse_lazy('finance_app:transaction_list')

class ReportView(LoginRequiredMixin, TemplateView):
    template_name = 'finance_app/report.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = date.today()
        year = self._safe_int(self.request.GET.get('year'), today.year)
        month = self._safe_int(self.request.GET.get('month'), today.month)
        month = month if 1 <= month <= 12 else today.month
        year = year if 2000 <= year <= 2100 else today.year
        target = date(year, month, 1)
        inc = income_total(target)
        exp = expense_total(target)
        ctx.update({
            'target': target,
            'spending_by_category': spending_by_category(target),
            'income_total': inc,
            'expense_total': exp,
            'net_total': (inc or 0) - (exp or 0),
            'budget_usage': budget_usage(target),
        })
        return ctx

    @staticmethod
    def _safe_int(raw_value, default):
        try:
            return int(raw_value)
        except (TypeError, ValueError):
            return default

def category_create(request):
    if not request.user.is_authenticated:
        return redirect('finance_app:login')
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('finance_app:transaction_list')
    else:
        form = CategoryForm()
    return render(request, 'finance_app/transaction_form.html', {'form': form, 'title': 'New Category'})

def budget_create(request):
    if not request.user.is_authenticated:
        return redirect('finance_app:login')
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('finance_app:report')
    else:
        form = BudgetForm()
    return render(request, 'finance_app/transaction_form.html', {'form': form, 'title': 'New Budget'})
