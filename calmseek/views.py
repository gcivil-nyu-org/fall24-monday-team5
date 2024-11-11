from django.shortcuts import render, redirect


def error(request):
    return render(request, "error.html")

def redirect_to_dashboard(request):
    if request.user.is_authenticated:
        if request.user.role == "User":
            return redirect('accounts:client_dashboard')
        elif request.user.role == "Provider":
            return redirect('accounts:provider_dashboard')
        # You can add additional roles if needed or default to a specific dashboard
    return redirect('login')
