from django.shortcuts import redirect, render
from django.shortcuts import HttpResponse

def isauthenticated_user(actual_func):
    def inner_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        #     if request.user.groups.exists():
        #         if request.user.groups.all()[0].name == 'admin':
        #             return redirect('dashboard')
        #         elif request.user.groups.all()[0].name == 'stockist':
        #             return redirect('userinfo')
        #         else:
        #             return redirect('gameconsole')
        # else:
        return actual_func(request, *args, **kwargs)
    return inner_func


def authorized_user(allowed_roles=[]):
    def decorator(actual_func):
        def inner_func(request, *args, **kwargs):
            if request.user.is_authenticated:
                group = None
                if request.user.groups.exists():
                    group = request.user.groups.all()[0].name

                if group in allowed_roles:
                    return actual_func(request, *args, **kwargs)
                else:
                    return render(request, 'accounts/login.html')
            return render(request, 'accounts/login.html')
        return inner_func
    return decorator
