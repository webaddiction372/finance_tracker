from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Transaction, Category, Budget


class CategorySelect(forms.Select):
    def __init__(self, *args, category_kind_map=None, **kwargs):
        self.category_kind_map = category_kind_map or {}
        super().__init__(*args, **kwargs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        raw_value = option.get("value")
        if raw_value in ("", None):
            option["attrs"]["data-kind"] = "all"
        else:
            option["attrs"]["data-kind"] = self.category_kind_map.get(str(raw_value), "expense")
        return option


class StyledFieldsMixin:
    field_classes = {
        forms.TextInput: 'input',
        forms.EmailInput: 'input',
        forms.PasswordInput: 'input',
        forms.NumberInput: 'input',
        forms.DateInput: 'input',
        forms.Select: 'select',
    }

    def apply_styling(self):
        for field_name, field in self.fields.items():
            widget = field.widget
            classes = widget.attrs.get('class', '')
            base_class = 'input'
            for widget_type, class_name in StyledFieldsMixin.field_classes.items():
                if isinstance(widget, widget_type):
                    base_class = class_name
                    break
            widget.attrs['class'] = f"{classes} {base_class}".strip()
            widget.attrs.setdefault('placeholder', field.label)


class RegisterForm(StyledFieldsMixin, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget = forms.TextInput()
        self.fields['last_name'].widget = forms.TextInput()
        self.fields['email'].widget = forms.EmailInput()
        self.fields['password1'].help_text = 'Use at least 8 characters and avoid common passwords.'
        self.fields['password2'].help_text = 'Enter the same password again to confirm.'
        self.apply_styling()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class StyledAuthenticationForm(StyledFieldsMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styling()


class StyledPasswordResetForm(StyledFieldsMixin, PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styling()


class StyledSetPasswordForm(StyledFieldsMixin, SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styling()

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'description', 'category', 'amount', 'is_income']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.TextInput(attrs={'placeholder': 'e.g., Groceries at FreshMart'}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.order_by('name')
        category_kind_map = {
            str(category.pk): 'expense' if category.is_expense else 'income'
            for category in categories
        }
        self.fields['category'].queryset = categories
        self.fields['category'].widget = CategorySelect(category_kind_map=category_kind_map)
        self.fields['category'].widget.choices = self.fields['category'].choices
        StyledFieldsMixin.apply_styling(self)

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        is_income = cleaned_data.get('is_income')

        if category:
            expects_expense = not bool(is_income)
            if category.is_expense != expects_expense:
                entry_type = 'income' if is_income else 'expense'
                self.add_error('category', f'Select a category that belongs to {entry_type}.')

        return cleaned_data

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'is_expense']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        StyledFieldsMixin.apply_styling(self)

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month']
        widgets = {'month': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_expense=True).order_by('name')
        StyledFieldsMixin.apply_styling(self)

    def clean_month(self):
        month = self.cleaned_data['month']
        return month.replace(day=1)
