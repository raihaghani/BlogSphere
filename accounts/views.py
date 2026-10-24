from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import RegistrationForm

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Your account is ready. Sign in to join the conversation.')
        return redirect('login')
    return render(request, 'accounts/register.html', {'form': form})
