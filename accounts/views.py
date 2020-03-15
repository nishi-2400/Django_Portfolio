from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView,
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)

from .forms import (
    LoginForm, MyPasswordChangeForm, MyPasswordResetForm, MySetPasswordForm
)
from django.views import generic
 
class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'

class Login(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

class Logout(LogoutView):
    form_class = LoginForm
    initial = {'key': 'value'}
    template_name = 'accounts/logout.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        messages.success(request, 'ログアウトしました。')
        params = {
            'form': form,
        }
        return render(request, self.template_name, params)

class PasswordChange(PasswordChangeView):
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('accounts:password_change_done')
    template_name = 'accounts/password_change.html'

class PasswordChangeDone(PasswordChangeDoneView):
    template_name = 'accounts/password_change_done.html'

class PasswordReset(PasswordResetView):
    subject_template_name = 'mail/password_reset_subject.txt'
    email_template_name = 'mail/password_reset_message.txt'
    template_name = 'accounts/password_reset_form.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('accounts:password_reset_done')

class PasswordResetDone(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class PasswordResetConfirm(PasswordResetConfirmView):
    form_class = MySetPasswordForm
    success_url = reverse_lazy('accounts:password_reset_complete')
    template_name = 'accounts/password_reset_confirm.html'

class PasswordResetComplete(PasswordResetCompleteView):
    """新パスワード設定しましたページ"""
    template_name = 'accounts/password_reset_complete.html'