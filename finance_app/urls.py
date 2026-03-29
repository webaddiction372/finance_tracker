from django.contrib.auth import views as auth_views
from django.urls import path
from django.urls import reverse_lazy
from . import views
from .forms import StyledPasswordResetForm, StyledSetPasswordForm

app_name = 'finance_app'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path(
        'forgot-password/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
            success_url=reverse_lazy('finance_app:password_reset_done'),
            form_class=StyledPasswordResetForm,
        ),
        name='password_reset',
    ),
    path(
        'forgot-password/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url=reverse_lazy('finance_app:password_reset_complete'),
            form_class=StyledSetPasswordForm,
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
        name='password_reset_complete',
    ),
    path('', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/new/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('transactions/<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='transaction_update'),
    path('transactions/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),
    path('report/', views.ReportView.as_view(), name='report'),
    path('categories/new/', views.category_create, name='category_create'),
    path('budgets/new/', views.budget_create, name='budget_create'),
]
