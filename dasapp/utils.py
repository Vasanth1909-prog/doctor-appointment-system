import random
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from twilio.rest import Client
import razorpay
from razorpay.errors import BadRequestError, ServerError

from .models import SMSLog, Payment, Appointment


class VideoSMSHelper:
    """Handles video link generation and SMS sending"""

    def __init__(self):
        self.twilio_client = None
        if getattr(settings, 'TWILIO_ACCOUNT_SID', None) and getattr(settings, 'TWILIO_AUTH_TOKEN', None):
            self.twilio_client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
        self.twilio_from = getattr(settings, 'TWILIO_PHONE_NUMBER', None)

    def generate_video_link(self, appointment):
        """Generate a unique video meeting link for an appointment"""
        meeting_id = f"apt{appointment.id}-{random.randint(1000, 9999)}"
        base_url = getattr(settings, 'VIDEO_CONFERENCE_URL', 'https://meet.jit.si/')
        video_link = f"{base_url}{meeting_id}"

        appointment.video_link = video_link
        appointment.meeting_id = meeting_id
        appointment.save(update_fields=['video_link', 'meeting_id'])

        return video_link, meeting_id

    def send_sms(self, phone_number, message, appointment=None, sms_type='appointment_booking'):
        """Send SMS via Twilio and log it"""
        status = 'pending'
        response_text = ''

        if self.twilio_client and self.twilio_from:
            try:
                message_obj = self.twilio_client.messages.create(
                    body=message,
                    from_=self.twilio_from,
                    to=phone_number
                )
                status = 'sent'
                response_text = f"Twilio SID: {message_obj.sid}"
            except Exception as e:
                status = 'failed'
                response_text = str(e)
        else:
            print(f"[SMS to {phone_number}]: {message}")
            status = 'sent'

        SMSLog.objects.create(
            appointment=appointment,
            phone_number=phone_number,
            message=message,
            sms_type=sms_type,
            status=status,
            response=response_text
        )
        return status == 'sent'

    def send_appointment_confirmation(self, appointment):
        """Send appointment confirmation SMS with video link if online"""
        patient_phone = appointment.mobilenumber
        patient_name = appointment.fullname
        apt_date = appointment.date_of_appointment
        apt_time = appointment.time_of_appointment

        message = f"Dear {patient_name}, your appointment #{appointment.appointmentnumber} is confirmed for {apt_date} at {apt_time}. "

        if getattr(appointment, 'video_link', None):
            message += f"Video consultation link: {appointment.video_link} Meeting ID: {appointment.meeting_id}. "

        message += "Thank you for choosing our service."

        return self.send_sms(patient_phone, message, appointment, 'appointment_booking')

    def send_payment_confirmation(self, appointment, transaction_id, amount):
        """Send payment confirmation SMS"""
        patient_phone = appointment.mobilenumber
        patient_name = appointment.fullname

        message = (
            f"Dear {patient_name}, payment of ₹{amount} for appointment "
            f"#{appointment.appointmentnumber} is successful. "
            f"Transaction ID: {transaction_id}. Thank you!"
        )

        return self.send_sms(patient_phone, message, appointment, 'payment_confirmation')

    def send_reminder(self, appointment):
        """Send reminder 24h before appointment"""
        patient_phone = appointment.mobilenumber
        patient_name = appointment.fullname
        apt_time = appointment.time_of_appointment

        doctor_name = "Doctor"
        try:
            if hasattr(appointment.doctor_id, 'admin'):
                doctor_name = appointment.doctor_id.admin.first_name
        except Exception:
            pass

        message = f"Reminder: Your appointment with Dr. {doctor_name} is tomorrow at {apt_time}. "
        if getattr(appointment, 'video_link', None):
            message += f"Video link: {appointment.video_link}"

        return self.send_sms(patient_phone, message, appointment, 'appointment_reminder')


class PaymentHelper:
    """Handles payment processing with Razorpay"""

    def __init__(self):
        self.razorpay_configured = False
        self.client = None

        key_id = getattr(settings, 'RAZORPAY_KEY_ID', '').strip()
        key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '').strip()

        placeholder_values = {
            '',
            'YOUR_ACTUAL_KEY_SECRET',
            'YOUR_REAL_RAZORPAY_KEY_SECRET',
            'YOUR_ACTUAL_KEY_ID',
            'YOUR_REAL_RAZORPAY_KEY_ID',
            'rzp_test_YOUR_ACTUAL_KEY_ID',
        }

        try:
            if (
                key_id
                and key_secret
                and key_id not in placeholder_values
                and key_secret not in placeholder_values
                and 'YOUR_' not in key_id
                and 'YOUR_' not in key_secret
            ):
                self.client = razorpay.Client(auth=(key_id, key_secret))
                self.razorpay_configured = True
            else:
                print("⚠️ Razorpay keys are missing or placeholder values. Using test mode.")
        except Exception as e:
            print(f"Razorpay initialization error: {e}")
            self.razorpay_configured = False

    def create_order(self, amount, currency='INR'):
        """Create a Razorpay order with error handling"""
        if not self.razorpay_configured:
            print("⚠️ Razorpay not configured. Using mock order for testing.")
            return {
                'id': f'mock_order_{random.randint(1000, 9999)}',
                'amount': int(float(amount) * 100),
                'currency': currency,
                'status': 'created',
                'mock': True
            }

        try:
            order_data = {
                'amount': int(float(amount) * 100),
                'currency': currency,
                'payment_capture': 1
            }
            order = self.client.order.create(data=order_data)
            return order

        except BadRequestError as e:
            print(f"Razorpay BadRequestError: {e}")
            if "Authentication failed" in str(e):
                raise Exception("Razorpay authentication failed. Please check your API keys.")
            raise Exception(f"Razorpay error: {e}")

        except ServerError as e:
            print(f"Razorpay ServerError: {e}")
            raise Exception("Razorpay server error. Please try again later.")

        except Exception as e:
            print(f"Razorpay unexpected error: {e}")
            raise Exception(f"Payment processing error: {e}")

    def verify_payment(self, order_id, payment_id, signature):
        """Verify payment signature"""
        if not self.razorpay_configured:
            print("⚠️ Razorpay not configured. Skipping payment verification.")
            return True

        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        try:
            self.client.utility.verify_payment_signature(params_dict)
            return True
        except Exception as e:
            print(f"Payment verification error: {e}")
            return False

    def process_payment(self, appointment, amount, payment_method, request):
        """Main method to process payment"""
        try:
            amount = float(amount)

            if payment_method == 'online':
                if not self.razorpay_configured:
                    messages.warning(
                        request,
                        "Razorpay is not configured yet, so test mode was used. Appointment created successfully."
                    )
                    appointment.payment_status = 'completed'
                    appointment.payment_method = 'online'
                    appointment.payment_amount = amount
                    appointment.transaction_id = f"TEST_{random.randint(10000, 99999)}"
                    appointment.payment_date = datetime.now()
                    appointment.save()

                    return {
                        'success': True,
                        'redirect': False,
                        'test_mode': True
                    }

                order = self.create_order(amount)
                request.session['razorpay_order_id'] = order['id']
                request.session['appointment_id'] = appointment.id

                appointment.payment_amount = amount
                appointment.save(update_fields=['payment_amount'])

                return {
                    'success': True,
                    'order': order,
                    'redirect': True
                }

            appointment.payment_status = 'pending'
            appointment.payment_method = 'offline'
            appointment.payment_amount = amount
            appointment.save()

            return {
                'success': True,
                'redirect': False
            }

        except Exception as e:
            print(f"Payment processing error: {e}")
            error_message = str(e)

            if "authentication failed" in error_message.lower():
                messages.error(request, "Payment system configuration error. Please try offline payment or contact support.")
            elif "Razorpay server error" in error_message:
                messages.error(request, "Payment gateway is temporarily unavailable. Please try again later.")
            else:
                messages.error(request, f"Payment processing failed: {error_message}")

            appointment.payment_status = 'failed'
            appointment.payment_method = payment_method
            appointment.payment_amount = amount if str(amount).strip() else 0
            appointment.save()

            return {
                'success': False,
                'redirect': False,
                'error': error_message
            }

    def complete_payment(self, appointment, payment_id, order_id, signature):
        """Complete payment after verification"""
        if not self.razorpay_configured:
            print("⚠️ Razorpay not configured. Skipping payment verification.")
            appointment.payment_status = 'completed'
            appointment.payment_date = datetime.now()
            appointment.transaction_id = payment_id or f"TEST_{random.randint(10000, 99999)}"
            appointment.save()

            Payment.objects.create(
                appointment=appointment,
                patient_name=appointment.fullname,
                patient_phone=appointment.mobilenumber,
                amount=appointment.payment_amount,
                payment_method='online',
                transaction_id=appointment.transaction_id,
                payment_status='completed',
                payment_date=datetime.now()
            )
            return True

        if self.verify_payment(order_id, payment_id, signature):
            appointment.payment_status = 'completed'
            appointment.payment_date = datetime.now()
            appointment.transaction_id = payment_id
            appointment.save()

            Payment.objects.create(
                appointment=appointment,
                patient_name=appointment.fullname,
                patient_phone=appointment.mobilenumber,
                amount=appointment.payment_amount,
                payment_method='online',
                transaction_id=payment_id,
                payment_status='completed',
                payment_date=datetime.now()
            )
            return True

        return False