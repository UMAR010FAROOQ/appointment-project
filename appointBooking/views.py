# views.py
from django.shortcuts import render, get_object_or_404
from authentication.models import InstructorProfile
from instructors.models import AvailableTimeSlot
from appointBooking.models import Appointment
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.timezone import now
from datetime import timedelta
import hashlib
from django.contrib.auth.decorators import login_required
from social_django.models import UserSocialAuth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


# Configuration
JAZZCASH_MERCHANT_ID = "MC134763"
JAZZCASH_PASSWORD = "tt3x827u2u"
JAZZCASH_RETURN_URL = "http://127.0.0.1:8000/appointbooking/success/"
JAZZCASH_INTEGRITY_SALT = "810s8se82u"
JAZZCASH_POST_URL = "https://sandbox.jazzcash.com.pk/CustomerPortal/transactionmanagement/merchantform/"




def AppointBooking(request, pk):
    instructor = get_object_or_404(InstructorProfile, pk=pk)
    available_time_slots = AvailableTimeSlot.objects.filter(instructor=instructor, is_available=True).order_by('start_time')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        appointment_date = request.POST.get('appointment_date')
        if appointment_date:
            try:
                appointment_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format. Please select a valid date.", extra_tags='danger')
                return redirect(request.path_info)
        
        time_slot_id = request.POST.get('time_slot')
        
        # Check for missing date or time slot
        if not appointment_date or not time_slot_id:
            messages.error(request, "Select both date and time slot.", extra_tags='danger')
            return redirect(request.path_info)

        # Check if required fields are filled
        if not all([first_name, last_name, email, phone, address]):
            messages.error(request, "All fields are required.", extra_tags='danger')
            return redirect(request.path_info)

        # Fetch the selected time slot and validate
        try:
            time_slot = AvailableTimeSlot.objects.get(pk=time_slot_id)
        except AvailableTimeSlot.DoesNotExist:
            messages.error(request, "Selected time slot does not exist.", extra_tags='danger')
            return redirect(request.path_info)

        # Create and save the appointment
        appointment = Appointment.objects.create(
            instructor=instructor,
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            appointment_date=appointment_date,
            time_slot=time_slot,
            status='pending'
        )

        # Mark the selected time slot as unavailable
        time_slot.is_available = False
        time_slot.save()

        messages.success(request, "Booking Information saved successfully!", extra_tags='success')
        return redirect('appointBooking:appointment_checkout', appointment_id=appointment.id)

    return render(request, 'appointbooking/appointment.html', {
        'instructor': instructor,
        'available_time_slots': available_time_slots,
    })





def generate_jazzcash_hash(data):
    sorted_data = '&'.join(f'{k}={v}' for k, v in sorted(data.items()) if v)  # Exclude empty fields
    hash_string = JAZZCASH_INTEGRITY_SALT + '&' + sorted_data
    print(f"Hash String: {hash_string}")  # Debug print
    return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()


def AppointCheckout(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user, status='pending')
    
    
    instructor = appointment.instructor
    countdown_end_time = (now() + timedelta(minutes=10)).timestamp()  # Convert to timestamp for JS

    # Fetch the specific education record if it exists
    service_cost = instructor.educations.order_by('-end_date').first().service_cost if instructor.educations.exists() else 0

    # Generate JazzCash form data
    transaction_ref = f'TXN{datetime.now().strftime("%Y%m%d%H%M%S")}'
    data = {
        'pp_Version': '1.1',
        'pp_TxnType': '',
        'pp_Language': 'EN',
        'pp_MerchantID': JAZZCASH_MERCHANT_ID,
        'pp_SubMerchantID': '',
        'pp_Password': JAZZCASH_PASSWORD,
        "pp_BankID": "TBANK",
        'pp_ProductID': 'RETL',
        'pp_TxnRefNo': transaction_ref,
        'pp_Amount': f"{int(service_cost) * 100}",  
        'pp_TxnCurrency': 'PKR',
        'pp_TxnDateTime': datetime.now().strftime('%Y%m%d%H%M%S'),
        'pp_BillReference': f'APP{appointment_id}',
        'pp_Description': f'Appointment payment for {appointment.first_name} {appointment.last_name}',
        'pp_ReturnURL': JAZZCASH_RETURN_URL,
        'pp_SecureHash': '',
    }


    print(f"pp_Amount being passed: {data['pp_Amount']}")
    print(f"pp_MerchantID: {data['pp_MerchantID']}")
    print(f"pp_Password: {data['pp_Password']}")


    data['pp_SecureHash'] = generate_jazzcash_hash(data)
    data['pp_PostURL'] = JAZZCASH_POST_URL

    print(f"Generated Secure Hash: {data['pp_SecureHash']}")

    context = {
        'appointment': appointment,
        'instructor': instructor,
        'service_price': service_cost,
        'jazzcash_data': data,
        'countdown_end_time': countdown_end_time,
        'jazzcash_post_url': JAZZCASH_POST_URL 
        
    }
    return render(request, 'appointbooking/checkout.html', context)


@csrf_exempt
def AppointSuccess(request):
    # Retrieve the JazzCash response
    response_data = request.POST or request.GET
    print("JazzCash Response:", response_data)

    # Extract relevant fields from the JazzCash response
    pp_bill_reference = response_data.get('pp_BillReference')  # Should be in the format 'APP{appointment_id}'

    # Validate the Bill Reference
    if not pp_bill_reference or not pp_bill_reference.startswith('APP'):
        return JsonResponse({'error': 'Invalid or missing Bill Reference'}, status=400)
    
    # Extract the appointment ID from pp_BillReference
    appointment_id = pp_bill_reference[3:]  # Strip 'APP' to get the appointment ID

    # Fetch the appointment from the database
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return JsonResponse({'error': 'Appointment not found'}, status=404)

    # Change the status to 'confirmed' regardless of payment outcome
    appointment.status = 'confirmed'
    appointment.save()
    print(f"Appointment {appointment_id} status updated to 'confirmed'.")

    # Check payment response for display purposes
    pp_response_code = response_data.get('pp_ResponseCode')
    if pp_response_code == '000':  # Payment successful
        status_message = 'success'
    else:  # Payment failed
        status_message = 'failed'

    # Render the appropriate template
    return render(request, 'appointbooking/success.html', {'status': status_message})


def AppointCancelled(request):
    return render(request, 'appointbooking/cancelled.html')



@login_required
def add_to_google_calendar(request):
    # Retrieve the user's social auth entry
    try:
        social = request.user.social_auth.get(provider='google-oauth2')
    except UserSocialAuth.DoesNotExist:
        return render(request, 'appointbooking/success.html', {'status': 'failed', 'message': 'Google authentication required'})

    # Retrieve the access token and refresh token
    token = social.extra_data['access_token']
    credentials = Credentials(
        token=token,
        refresh_token=social.extra_data.get('refresh_token'),
        client_id=social.extra_data['client_id'],
        client_secret=social.extra_data['client_secret'],
        token_uri='https://oauth2.googleapis.com/token',
    )

    # Build the Google Calendar API service
    service = build('calendar', 'v3', credentials=credentials)

    # Define the event details (you might want to retrieve these details from your database)
    event = {
        'summary': f'Appointment with Dr. {request.user.first_name}',
        'location': 'Enter location here',
        'description': 'Appointment details here',
        'start': {
            'dateTime': '2024-12-01T10:00:00',  # Replace with actual start time
            'timeZone': 'Asia/Karachi',  # Adjust timezone if necessary
        },
        'end': {
            'dateTime': '2024-12-01T11:00:00',  # Replace with actual end time
            'timeZone': 'Asia/Karachi',
        },
    }

    try:
        # Insert the event into Google Calendar
        event = service.events().insert(calendarId='primary', body=event).execute()
        return render(request, 'appointbooking/success.html', {'status': 'success', 'message': 'Appointment added to Google Calendar'})
    except Exception as e:
        print("Error:", e)
        return render(request, 'appointbooking/success.html', {'status': 'failed', 'message': 'Failed to add appointment to Google Calendar'})


