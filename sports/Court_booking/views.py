from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from .serializers import booking_serializer
from rest_framework.decorators import api_view
from users.models import user
from .models import Court, Branch, booking_order,court_pictures,booking_recipt
from .forms import BookingForm, court_selection
from django.contrib import messages
from datetime import datetime, timezone
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail

@api_view(['get'])
def serialised_court(request):
    courts = Court.objects.all()
    serialised = booking_serializer(courts, many=True)
    return Response(serialised.data)

@login_required
def form_booking(request):
    Courts = Branch.objects.all()
    crts = Court.objects.all()
    
    if request.method == "POST":
            form = BookingForm(request.POST)
            if form.is_valid():
                booking = form.save(commit=False)
                booking.user = request.user
                login(request, request.user)
                courts = Court.objects.all()
                for court in courts:
                    if court.sport.pk == booking.sport.pk and court.branch.pk == booking.branch.pk:
                        if court.available_courts > 0 :
                            booking.court = court
                            request.session['Booking_details'] = {
                                'user_pk':booking.user.pk,
                                'court_pk':booking.court.pk,
                                'Date': str(booking.Date),
                                'time': str(booking.time),
                                'duration':str(booking.duration),
                                'branch_pk':booking.branch.pk,
                                'sport_pk':booking.sport.pk,
                            }
                            return redirect('courts')
                        else:
                            messages.error(request, f"The courts for selected sport are already booked")
                    else:
                        messages.error(request, f"The selected {booking.sport} is not available  at {booking.branch}")
            else:
                messages.error(request, "There was an error in your booking form. Please check the details.")
    else:
        form = BookingForm()
    return render(request, 'booking.html',{'form':form, 'branchs':Courts, 'courts':crts})


def selection(request):
    court_data = request.session.get("Booking_details")
    date = court_data['Date']
    Date = datetime.strptime(date,"%Y-%m-%d").date()
    time = court_data['time']
    Time = datetime.strptime(time,"%H:%M:%S").time()
    Duration = court_data['duration']
    duration = datetime.strptime(Duration,"%H:%M:%S") - datetime.strptime("00:00:00", "%H:%M:%S")
    court_id = Court.objects.get(pk=court_data['court_pk'])
    branch = court_id.branch
    sport = court_id.sport
    if court_data:
        court = booking_order(
            user= request.user,
            court= court_id,
            Date=Date,
            time=Time,
            duration=duration,
            branch= branch,
            sport= sport
        )

        Branch = Court.objects.all()
        court_courts = range(1,( court.court.available_courts +1))
        court_pic = court_pictures.objects.all()
        if request.user == court.user:
            if request.method == "POST":
                form = court_selection(request.POST)
                if form.is_valid():
                    y = form.save(commit=False)
                    if int(y.court_no) <= int(court.court.available_courts):
                        start_dt = datetime.combine(court.Date, court.time)
                        end_dt = start_dt + court.duration
                        
                        court.start = start_dt
                        court.end= end_dt
                        
                        court.court_no = y.court_no
                        overlapping = booking_order.objects.filter(
                            start__lt = court.end,
                            end__gt = court.start,
                            court_no = court.court_no,
                            court = court.court
                        )
                        if overlapping.exists():
                            messages.error(request, f"Chose another field or timings, the timing{court.start} is already reserved at court no {court.court_no}" )
                            return redirect('booking')
                        else:
                            court.save()
                            o = request.user
                            crt = court.Code
                            request.session.flush()
                            login(request, o)         
                            user = request.user
                            email_sending(request,crt)
                            messages.success(request, "Booking confirmed! Details sent to your email.")
                            return redirect('userpage')
                    else:
                        messages.error(request,f"the selected court aint available")
                else:
                    messages.error(request,f"No courts available")
            else:
                form = court_selection()
        else:
            messages.error(request,f"{request.user} is not permitted to do this")
            return redirect('userpage')
    else:
        messages.error(request,f"the session has expired")
        return redirect('booking')
    return render(request, 'extended.html',{'form':form, 'available_sport':Branch,'booking_court':court ,'courts':court_courts,'pictures': court_pic})

def email_sending(request, court):
    print("function start 1")
    user = request.user
    booking = booking_order.objects.get(Code=court)
    print("data filtered 2")
    subject = f"Booking Connfirmation- {booking.court.sport} at {booking.branch.Location}"
    context = {
        'user':user,
        'booking':booking
    }
    print("basic things rendered")
    html_content = render_to_string("booking_confirmation.html", context)
    text_content = render_to_string("booking_confirmation.txt", context)
    print("4")
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,  
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    print("5")
    email.attach_alternative(html_content, "text/html")
    email.send()
    print("email sent", user.email, booking.user.email)
# Create your views here.