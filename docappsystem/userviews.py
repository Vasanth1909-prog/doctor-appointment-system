import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail

from dasapp.models import DoctorReg, Appointment, Page
from dasapp.utils import VideoSMSHelper, PaymentHelper


# ================= PROFESSIONAL EMAIL =================
def send_appointment_email(appointment):
    try:
        subject = "Appointment Confirmation"

        # Doctor Name
        if appointment.doctor_id and appointment.doctor_id.admin:
           doctor_name = f"{appointment.doctor_id.admin.first_name} {appointment.doctor_id.admin.last_name}"
        else:
            doctor_name = "Doctor"

        # Payment
        payment_amount = appointment.payment_amount if appointment.payment_amount else "N/A"
        transaction_id = appointment.transaction_id if appointment.transaction_id else "N/A"

        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color:#f6f6f6; padding:20px;">
            <div style="max-width:600px; margin:auto; background:#ffffff; padding:25px; border:1px solid #ddd;">
                
                <h2>Appointment Confirmation</h2>

                <p>Dear {appointment.fullname},</p>

                <p>Your appointment has been successfully scheduled. The details are provided below:</p>

                <h4>Appointment Details</h4>
                <table style="width:100%;">
                    <tr><td><strong>Doctor</strong></td><td>{doctor_name}</td></tr>
                    <tr><td><strong>Appointment Number</strong></td><td>{appointment.appointmentnumber}</td></tr>
                    <tr><td><strong>Date</strong></td><td>{appointment.date_of_appointment}</td></tr>
                    <tr><td><strong>Time</strong></td><td>{appointment.time_of_appointment}</td></tr>
                </table>

                <br>

                <h4>Consultation Details</h4>
                <p>
                    Meeting Link:<br>
                    <a href="{appointment.video_link}">{appointment.video_link}</a><br><br>
                    Meeting ID: {appointment.meeting_id}
                </p>

                <h4>Payment Details</h4>
                <table style="width:100%;">
                    <tr><td><strong>Amount</strong></td><td>{payment_amount}</td></tr>
                    <tr><td><strong>Method</strong></td><td>{appointment.payment_method}</td></tr>
                    <tr><td><strong>Status</strong></td><td>{appointment.payment_status}</td></tr>
                    <tr><td><strong>Transaction ID</strong></td><td>{transaction_id}</td></tr>
                </table>

                <br>

                <p>Please ensure that you join the consultation on time and have a stable internet connection.</p>

                <br>

                <p>Thank you for choosing our services.</p>

                <p>
                Regards,<br>
                <strong>HospitalCare Team</strong>
                </p>

            </div>
        </body>
        </html>
        """

        plain_message = f"""
Appointment Confirmation

Doctor: {doctor_name}
Date: {appointment.date_of_appointment}
Time: {appointment.time_of_appointment}

Join: {appointment.video_link}
"""

        send_mail(
            subject,
            plain_message,
            settings.EMAIL_HOST_USER,
            [appointment.email],
            html_message=html_message,
            fail_silently=True
        )

        print("Professional email sent")

    except Exception as e:
        print("Email error:", e)


# ================= HOME =================
def userbase(request):
    return render(request, 'userbase.html')


def Index(request):
    return render(request, 'index.html', {
        'doctorview': DoctorReg.objects.all(),
        'page': Page.objects.all()
    })


# ================= BOOK APPOINTMENT =================
def create_appointment(request):
    doctorview = DoctorReg.objects.all()
    page = Page.objects.all()

    if request.method == "POST":
        try:
            appointmentnumber = random.randint(100000000, 999999999)
            doctor = DoctorReg.objects.get(id=request.POST.get('doctor_id'))

            appointment = Appointment.objects.create(
                appointmentnumber=appointmentnumber,
                fullname=request.POST.get('fullname'),
                email=request.POST.get('email'),
                mobilenumber=request.POST.get('mobilenumber'),
                date_of_appointment=request.POST.get('date_of_appointment'),
                time_of_appointment=request.POST.get('time_of_appointment'),
                doctor_id=doctor,
                additional_msg=request.POST.get('additional_msg', ''),
                status='0',
                payment_method=request.POST.get('payment_method'),
                payment_status='pending',
            )

            consultation_type = request.POST.get('consultation_type')
            payment_method = request.POST.get('payment_method')

            # Save payment amount
            appointment.payment_amount = doctor.consultation_fee
            appointment.save()

            # ===== VIDEO LINK =====
            if consultation_type == 'online':
                VideoSMSHelper().generate_video_link(appointment)

            # ===== ONLINE PAYMENT =====
            if payment_method == 'online':
                result = PaymentHelper().process_payment(
                    appointment,
                    doctor.consultation_fee,
                    payment_method,
                    request
                )

                if result.get('success'):

                    if result.get('test_mode'):
                        return redirect('dummy_payment_page', appointment_id=appointment.id)

                    if 'order' not in result:
                        return redirect('appointment_success', appointment_id=appointment.id)

                    request.session['pending_appointment_id'] = appointment.id

                    return render(request, 'user/razorpay_checkout.html', {
                        'order': result['order'],
                        'appointment': appointment,
                        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                        'callback_url': request.build_absolute_uri('/payment-callback/')
                    })

                return redirect('appointment_success', appointment_id=appointment.id)

            # ===== OFFLINE =====
            VideoSMSHelper().send_appointment_confirmation(appointment)

            # Send Email
            send_appointment_email(appointment)

            messages.success(request, "Appointment booked successfully!")
            return redirect('appointment_success', appointment_id=appointment.id)

        except Exception as e:
            print("ERROR:", e)
            messages.error(request, "Something went wrong")

    return render(request, 'appointment.html', {'doctorview': doctorview, 'page': page})


# ================= PAYMENT CALLBACK =================
def payment_callback(request):
    if request.method == "POST":
        try:
            appointment = get_object_or_404(
                Appointment,
                id=request.session.get('pending_appointment_id')
            )

            if PaymentHelper().complete_payment(
                appointment,
                request.POST.get('razorpay_payment_id'),
                request.POST.get('razorpay_order_id'),
                request.POST.get('razorpay_signature')
            ):
                VideoSMSHelper().send_appointment_confirmation(appointment)

                # Send email after payment success
                send_appointment_email(appointment)

                del request.session['pending_appointment_id']

                return redirect('appointment_success', appointment_id=appointment.id)

        except Exception as e:
            print("Payment error:", e)

    return redirect('userappointment')


# ================= SUCCESS =================
def appointment_success(request, appointment_id):
    return render(request, 'user/appointment_success.html', {
        'appointment': get_object_or_404(Appointment, id=appointment_id),
        'page': Page.objects.all()
    })


# ================= SEARCH =================
def User_Search_Appointments(request):
    page = Page.objects.all()
    query = request.GET.get('query')

    if query:
        patient = Appointment.objects.filter(fullname__icontains=query) | \
                  Appointment.objects.filter(appointmentnumber__icontains=query)

        return render(request, 'search-appointment.html', {
            'patient': patient,
            'query': query,
            'page': page
        })

    return render(request, 'search-appointment.html', {'page': page})


# ================= DETAILS =================
def View_Appointment_Details(request, id):
    return render(request, 'user_appointment-details.html', {
        'patientdetails': Appointment.objects.filter(id=id),
        'page': Page.objects.all()
    })


# ================= DUMMY PAYMENT =================
def dummy_payment_page(request, appointment_id):
    return render(request, 'dummy_payment.html', {
        'appointment': get_object_or_404(Appointment, id=appointment_id),
        'page': Page.objects.all()
    })


def dummy_payment_process(request, appointment_id, status):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if status == 'success':
        appointment.payment_status = 'completed'
        appointment.transaction_id = f"DUMMY_{random.randint(10000,99999)}"
        appointment.save()

        VideoSMSHelper().send_appointment_confirmation(appointment)
        send_appointment_email(appointment)

    else:
        appointment.payment_status = 'failed'
        appointment.save()

    return redirect('appointment_success', appointment_id=appointment.id)