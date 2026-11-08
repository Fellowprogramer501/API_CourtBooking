# =====================================================================
# TAG LEGEND
#   [CHANGED]  line existed before, I changed it
#   [ADDED]    new line or block
#   [REMOVED]  something I took out (shown as a comment so you can see it)
# Anything without a tag is exactly as you wrote it.
# =====================================================================

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password   # [CHANGED] added make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from .models import user
from Court_booking.models import booking_order
from . import forms
import logging                                                          # [ADDED] to log real email errors
import secrets                                                          # [ADDED] safer random numbers for OTP
# [REMOVED] import random  -> replaced by secrets
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)                                    # [ADDED]

MAX_OTP_ATTEMPTS = 5                                                    # [ADDED] stops guessing the code

def user_logout(request):
    logout(request)
    return redirect('home')


def user_login(request):
    if request.method == 'POST':
        form = forms.loginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                x = user.objects.get(email=email)
                if check_password(password, x.password):
                    login(request, x)
                    messages.success(request, f"Welcome {x.username}")
                    return redirect('home')
                else:
                    messages.error(request, "Incorrect password.")
            except user.DoesNotExist:                                   
                messages.error(request, "User not found")  
    else:
        form = forms.loginForm()
    return render(request, 'login_pg.html', {'form': form})


@login_required
def user_page(request):
    current_user = request.user                                        
    bookings = booking_order.objects.filter(user=current_user)          
    return render(request, 'userpage.html', {'bookings': bookings, 'user': current_user}) 


def registration_page(request):
    if request.method == 'POST':
        form = forms.registerationform(request.POST)
        if form.is_valid():
            try:
                request.session['user_data'] = {
                    'username': form.cleaned_data['username'],
                    'first_name': form.cleaned_data['first_name'],
                    'last_name': form.cleaned_data['last_name'],
                    'email': form.cleaned_data['email'],
                    'num': str(form.cleaned_data['num']),               
                    'password': make_password(form.cleaned_data['password1']),  
                }
                email = form.cleaned_data['email']
                if otp_genrator(request, email):
                    return redirect('verify')
            except Exception as e:
                logger.exception("Registration failed")                 
                messages.error(request, f"Try again: {str(e)}")
        else:
            # x = ValueError()
            messages.error(request, "some of the data aint right")
    else:
        form = forms.registerationform()
    return render(request, 'registeration.html', {'form': form})


def otp_genrator(request, email):
    otp = str(secrets.randbelow(90000) + 10000)                         # [CHANGED] was random.randint(10000, 99999), same 5-digit range
    request.session['otp'] = otp                                        # [CHANGED] already a string
    request.session['otp_time'] = datetime.now().isoformat()
    request.session['otp_attempts'] = 0                                 # [ADDED] reset the wrong-guess counter
    try:
        send_mail(
            subject="Your OTP Code",
            message=f"Your OTP is {otp}. It expires in 2 minutes.",
            from_email=None,                                            # [CHANGED] uses DEFAULT_FROM_EMAIL from settings.py
            recipient_list=[email],
            fail_silently=False,                                        # [ADDED] makes errors raise instead of being hidden
        )
    except Exception as e:                                              # [CHANGED] was a bare "except:" that threw the error away
        logger.exception("OTP email failed")                            # [ADDED] full error in your terminal
        # [CHANGED] now shows the real reason; once it works, replace {e} with a generic message
        messages.error(request, f"Failed to send OTP to {email}: {e}")
        return False                                                    # [ADDED]
    messages.success(request, "OTP sent to your email.")
    return True                                                         # [ADDED]
    # [REMOVED] the "if result: ... else: ..." check, because send_mail raises on failure when fail_silently=False


def otp_verification(request):
    if request.method == "POST":
        user_otp = (request.POST.get("otp") or "").strip()              # [CHANGED] strips spaces, handles an empty value
        session_otp = request.session.get("otp")
        otp_time = request.session.get("otp_time")
        if not session_otp or not otp_time:
            messages.error(request, "No OTP was sent.")
            return redirect('register')

        if datetime.now() > datetime.fromisoformat(otp_time) + timedelta(minutes=2):
            messages.error(request, "OTP has expired.")
            request.session.pop('otp', None)
            request.session.pop('otp_time', None)
            return redirect('register')

        # [ADDED] too many wrong guesses -> the code is cancelled
        if request.session.get('otp_attempts', 0) >= MAX_OTP_ATTEMPTS:
            messages.error(request, "Too many wrong attempts. Please register again.")
            request.session.pop('otp', None)
            request.session.pop('otp_time', None)
            request.session.pop('otp_attempts', None)
            return redirect('register')

        if secrets.compare_digest(user_otp, session_otp):               # [CHANGED] was "user_otp == session_otp"
            user_data = request.session.get("user_data")
            if not user_data:
                messages.error(request, "Session expired.")
                return redirect('register')

            # [ADDED] stops a crash if the email or username was taken in the meantime
            if user.objects.filter(email=user_data['email']).exists() or \
               user.objects.filter(username=user_data['username']).exists():
                messages.error(request, "An account with this email or username already exists.")
                return redirect('register')

            x = user(
                username=user_data['username'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                num=user_data['num'],
                email=user_data['email'],
            )
            x.password = user_data['password']                          # [CHANGED] already hashed, was x.set_password(user_data['password'])
            x.save()
            # user_login
            request.session.flush()
            login(request, x)
            return redirect('home')                                     # [CHANGED] was redirect('login'), but you are already logged in
        else:
            request.session['otp_attempts'] = request.session.get('otp_attempts', 0) + 1  # [ADDED] count the wrong guess
            messages.error(request, "Invalid OTP.")
            return redirect('verify')
    return render(request, 'auth.html')