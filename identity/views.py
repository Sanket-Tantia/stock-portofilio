from django.shortcuts import render, redirect

from .forms import LoginForm
from django.forms.utils import ErrorList

from django.contrib.auth import authenticate, login

# redirect after form submit
from django.http import HttpResponseRedirect
from django.http import HttpResponse

from core.decorators import isauthenticated_user

# Create your views here.
@isauthenticated_user
def login_view(request):
    login_form = LoginForm(request.POST or None)
    context = {}

    if request.method == "POST":
        if login_form.is_valid():
            username = login_form.cleaned_data.get("username")
            password = login_form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                context['message'] = 'Invalid username or password'
        else:
            context['message'] = 'Error in validating. Try again'

    return render(request, "accounts/login.html", {"form": login_form, "context" : context})