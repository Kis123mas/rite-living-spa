from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import *
import calendar
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import json
from reportlab.lib import colors
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import TruncMonth
from .models import *
from datetime import datetime, timedelta, date
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .decorators import *



def LandingPageView(request):
    """ landing page """
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect(request.META.get('HTTP_REFERER', 'landingpage'))  # if no referer, fallback to home

    return render(request, 'firstApp/landingpage.html')



def RegisterPageView(request):
    """Register a new user using a custom form"""

    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Set backend explicitly before logging in
            user.backend = 'django.contrib.auth.backends.ModelBackend'

            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('loginpage')
    else:
        form = CustomUserRegistrationForm()

    return render(request, 'auth/register.html', {'form': form})


def LoginPageView(request):
    """ Login page view """
    if request.method == 'POST':
        email = request.POST.get('email')  # Get the email from the form
        password = request.POST.get('password')  # Get the password from the form

        # Debugging: Print email and password for debugging purposes
        print(f"Attempting to log in with email: {email}")

        # Attempt to authenticate the user using email and password
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # If user is authenticated, log them in
            print(f"Login successful for email: {email}")
            login(request, user)
            return redirect('dashboardpage')  # Redirect to the home page or wherever you'd like
        else:
            # If authentication fails, show an error message
            print(f"Authentication failed for email: {email}")
            messages.error(request, "Invalid email or password.")

    return render(request, 'auth/login.html')



def logoutView(request):
    """Logout the user and redirect to the landing page"""
    logout(request)
    return redirect('landingpage')

@login_required(login_url='loginpage')
def CalenderPageView(request):
    """ Calendar page view that renders a calendar with dates and a uniform form """
    
    # Get current date for dynamic month/year display
    today = datetime.today()
    month = today.month
    year = today.year
    
    # Generate calendar for the month
    cal = calendar.Calendar(firstweekday=6)  # Starts on Sunday
    month_days = cal.monthdayscalendar(year, month)
    
    # Build list of days with uniforms
    days_of_week = []
    for week in month_days:
        week_days = []
        for day in week:
            if day != 0:  # If day is not 0, it is a valid day of the month
                # Check if there is a uniform posted for this day
                uniform = Uniform.objects.filter(uniform_date__year=year, uniform_date__month=month, uniform_date__day=day).first()
                
                if uniform:
                    week_days.append({
                        'day': day,
                        'is_current_month': True,
                        'uniform': uniform,
                    })
                else:
                    week_days.append({
                        'day': day,
                        'is_current_month': True,
                        'uniform': None,
                    })
            else:
                week_days.append({
                    'day': '',
                    'is_current_month': False,
                    'uniform': None,
                })
        days_of_week.append(week_days)
    
    # Pass month name and year dynamically
    month_name = calendar.month_name[month]
    
    # Handle the uniform form submission (for posting new uniforms)
    if request.method == 'POST':
        # Debugging: Log the incoming POST data to verify the request
        print(request.POST)
        
        # Check if it's an update or a new post
        uniform_id = request.POST.get('id')
        
        if uniform_id:
            # If uniform_id is present, it's an update
            uniform = get_object_or_404(Uniform, id=uniform_id)
            form = UniformForm(request.POST, instance=uniform)  # Bind the form to the existing uniform instance
        else:
            # Otherwise, it's a new uniform post
            form = UniformForm(request.POST)

        if form.is_valid():
            form.save()  # Save the uniform data (either new or updated) to the database
            messages.success(request, "Uniform Saved successfully.")
        else:
            print("Form errors: ", form.errors)  # Debugging message to see any validation errors
    else:
        form = UniformForm()

    # Query all uniforms for the current month and year
    uniforms_for_month = Uniform.objects.filter(uniform_date__year=year, uniform_date__month=month)


    orders = Order.objects.select_related('client', 'product').order_by('-created_at')
    order_count = orders.count()


    # Booking form logic...
    total_bookings = SpaSessionBooking.objects.count()
    all_bookings = SpaSessionBooking.objects.all()

    context = {
        'orders': orders,
        'order_count': order_count,
        'status_choices': Order.STATUS_CHOICES,
        'calendar_weeks': days_of_week,
        'month_name': month_name,
        'year': year,
        'form': form,
        'uniforms_for_month': uniforms_for_month,
        'total_bookings': total_bookings,
        'all_bookings': all_bookings,
    }
    

    # Render the template with the generated data, form, and uniforms
    return render(request, 'auth/calender.html', context)


@login_required(login_url='loginpage')
@admin_and_secretary_required
def RecordservicePageView(request):
    if request.method == 'POST':
        form = ServiceRenderedForm(request.POST)
        if form.is_valid():
            form.save()
            form = ServiceRenderedForm()
            messages.success(request, "Service recorded successfully.")
            
        else:
            print(form.errors)
    else:
        form = ServiceRenderedForm()

    services = ServiceRendered.objects.order_by('-created_at')

    orders = Order.objects.select_related('client', 'product').order_by('-created_at')
    order_count = orders.count()

    # Booking form logic...
    total_bookings = SpaSessionBooking.objects.count()
    all_bookings = SpaSessionBooking.objects.all()

    context = {
        'form': form,
        'services': services,
        'orders': orders,
        'order_count': order_count,
        'status_choices': Order.STATUS_CHOICES,
        'total_bookings': total_bookings,
        'all_bookings': all_bookings,
    }
    return render(request, 'auth/recordservice.html', context)


@login_required(login_url='loginpage')
def ProfilePageView(request):
    """ Profile page """

    user = request.user
    
    # Ensure the user is logged in
    if not request.user.is_authenticated:
        return redirect('loginpage')  # Redirect to login page if not logged in
    
    # Get the logged-in user's profile (or 404 if not found)
    user_profile = get_object_or_404(UserProfile, user=request.user)

    orders = Order.objects.select_related('client', 'product').order_by('-created_at')
    order_count = orders.count()


    orders = Order.objects.select_related('client', 'product').order_by('-created_at')
    order_count = orders.count()
    user_order_count = orders.filter(client=user).count()

    user_orders = Order.objects.filter(client=user).select_related('product').prefetch_related('messages').order_by('-created_at')
    user_order_count_show = user_orders.count()

    # Booking form logic...
    total_bookings = SpaSessionBooking.objects.count()
    all_bookings = SpaSessionBooking.objects.all()

    context = {
        'user_profile': user_profile,
        'orders': orders,
        'order_count': order_count,
        'status_choices': Order.STATUS_CHOICES,
        'total_bookings': total_bookings,
        'all_bookings': all_bookings,
        'user' : user,
        'orders': orders,
        'user_order_count': user_order_count,
        'user_orders': user_orders,
        'user_order_count_show': user_order_count_show
    }
    
    return render(request, 'auth/profile.html', context)


@login_required(login_url='loginpage')
def ProductPage(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form = ProductForm()
            messages.success(request, "Product Added Successfully.")
    else:
        form = ProductForm()

    products = Product.objects.all().order_by('-created_at')  # fetch products for display

    orders = Order.objects.select_related('client', 'product').order_by('-created_at')
    order_count = orders.count()

    # Booking form logic...
    total_bookings = SpaSessionBooking.objects.count()
    all_bookings = SpaSessionBooking.objects.all()

    context = {
        'form': form,
        'products': products,
        'orders': orders,
        'order_count': order_count,
        'status_choices': Order.STATUS_CHOICES,
        'total_bookings': total_bookings,
        'all_bookings': all_bookings,
    }
    
    return render(request, 'auth/product.html',context)


@login_required(login_url='loginpage')
@admin_and_secretary_required
def delete_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product.delete()
    return redirect('productspage')


@login_required(login_url='loginpage')
@admin_and_secretary_required
def UpdateOrderStatus(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
    
    return redirect(request.META.get('HTTP_REFERER', 'orders_list'))


@login_required(login_url='loginpage')
@admin_and_secretary_required
def send_order_message(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        content = request.POST.get("content")

        order = get_object_or_404(Order, id=order_id)
        Message.objects.create(
            order=order,
            sender=request.user,
            content=content
        )
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='loginpage')
@admin_and_secretary_required
def DeleteOrder(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        order.delete()
        messages.success(request, "Order deleted successfully.")
    return redirect('dashboardpage')


@login_required(login_url='loginpage')
def UpdateProfileView(request):
    if request.method == 'POST':
        profile = request.user.profile

        phone = request.POST.get('phone_number')
        address = request.POST.get('address')
        birthday = request.POST.get('birthday')
        bio = request.POST.get('bio')
        facebook = request.POST.get('facebook')
        twitter = request.POST.get('twitter')
        instagram = request.POST.get('instagram')
        linkedin = request.POST.get('linkedin')

        if phone:
            profile.phone_number = phone
        if address:
            profile.address = address
        if birthday:
            profile.birthday = birthday
        if bio:
            profile.bio = bio
        if facebook:
            profile.facebook = facebook
        if twitter:
            profile.twitter = twitter
        if instagram:
            profile.instagram = instagram
        if linkedin:
            profile.linkedin = linkedin

        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()
        return redirect('profilepage') 


@login_required(login_url='loginpage')
@admin_and_secretary_required
def RecordexpensesPageView(request):
    """ Expense recording page """
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            form = ExpenseForm()
            messages.success(request, "Expense recorded successfully.")
    else:
        form = ExpenseForm()

    # Get the month and year from the GET request, defaulting to current month and year
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))

    # Fetch the expenses filtered by month and year
    expenses = Expense.objects.filter(date__month=month, date__year=year)

    orders = Order.objects.select_related('client', 'product').order_by('-created_at')
    order_count = orders.count()

    # Booking form logic...
    total_bookings = SpaSessionBooking.objects.count()
    all_bookings = SpaSessionBooking.objects.all()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check if it's an AJAX request
        # Return JSON data for AJAX request
        expenses_data = [
            {
                'amount': expense.amount,
                'description': expense.description,
                'category': expense.get_category_display(),
                'date': expense.date.strftime('%Y-%m-%d %H:%M')
            }
            for expense in expenses
        ]
        return JsonResponse({'expenses': expenses_data})

    # Pass data to the template for normal page load
    context = {
        'form': form,
        'expenses': expenses,
        'months': [
            "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"
        ],
        'month': month,
        'year': year,
        'orders': orders,
        'order_count': order_count,
        'status_choices': Order.STATUS_CHOICES,
        'total_bookings': total_bookings,
        'all_bookings': all_bookings,
    }

    return render(request, 'auth/expenses.html', context)


@login_required(login_url='loginpage')
@admin_and_secretary_required
def CalculatePageView(request):
    # Get month/year from GET params or use current month/year as default
    month = int(request.GET.get('month', date.today().month))
    year = int(request.GET.get('year', date.today().year))
    month_name = calendar.month_name[month]

    # Filter services by selected month and year, and ensure staff is not secretary
    services = ServiceRendered.objects.filter(
        service_date__month=month,
        service_date__year=year,
        staff_name__is_not_secretary=True  # Ensure the staff is not a secretary
    )

    # Group by staff and count jobs
    staff_jobs = (
        services.values('staff_name__id', 'staff_name__first_name', 'staff_name__last_name')
        .annotate(jobs_done=Count('id'))
        .order_by('staff_name__first_name')
    )

    # Calculate totals by payment method
    payment_totals = (
        services.values('mode_of_payment')
        .annotate(total=Sum('amount'))
    )

    # Create a payment summary dict
    payment_summary = {'cash': 0, 'pos': 0, 'transfer': 0}
    for entry in payment_totals:
        payment_summary[entry['mode_of_payment']] = entry['total'] or 0


    # Get all jobs for the month/year
    all_jobs = services.select_related('staff_name').order_by('-service_date')

    # Total amount
    total_amount = services.aggregate(total=Sum('amount'))['total'] or 0


    orders = Order.objects.select_related('client', 'product').order_by('-created_at')
    order_count = orders.count()


    # Booking form logic...
    total_bookings = SpaSessionBooking.objects.count()
    all_bookings = SpaSessionBooking.objects.all()

    context = {
        'staff_jobs': staff_jobs,
        'payment_summary': payment_summary,
        'month': month,
        'year': year,
        'month_name': month_name,
        'all_jobs': all_jobs,
        'total_amount': total_amount,
        'orders': orders,
        'order_count': order_count,
        'status_choices': Order.STATUS_CHOICES,
        'total_bookings': total_bookings,
        'all_bookings': all_bookings,
    }

    return render(request, 'auth/calculate.html', context)


@login_required(login_url='loginpage')
@admin_and_secretary_required
def get_staff_jobs(request, staff_id):
    month = int(request.GET.get('month', date.today().month))
    year = int(request.GET.get('year', date.today().year))

    jobs = ServiceRendered.objects.filter(
        staff_name__id=staff_id,
        service_date__month=month,
        service_date__year=year
    ).values(
        'service_rendered',
        'service_type',
        'amount',
        'mode_of_payment',
        'service_date',
        'customer_name',
        'description',
        'payment_status'
    )

    total_amount = jobs.aggregate(total=Sum('amount'))['total'] or 0

    return JsonResponse({
        'jobs': list(jobs),
        'total_amount': float(total_amount)
    })



@login_required(login_url='loginpage')
def DashboardPageView(request):
    user = request.user
    profile = getattr(user, 'profile', None)

    User = get_user_model()

    # Get the current month and year (or use query parameters to select a different month/year)
    month = int(request.GET.get('month', date.today().month))
    year = int(request.GET.get('year', date.today().year))

    # List of months
    months = [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ]

    # Service statistics by staff (number of services rendered for the specific month)
    services = ServiceRendered.objects.filter(
        service_date__month=month,
        service_date__year=year
    ).values('staff_name__first_name').annotate(total=Count('id'))

    staff_labels = [s['staff_name__first_name'] for s in services]
    staff_data = [s['total'] for s in services]


    orders = Order.objects.select_related('client', 'product').order_by('-created_at')
    order_count = orders.count()
    user_order_count = orders.filter(client=user).count()

    user_orders = Order.objects.filter(client=user).select_related('product').prefetch_related('messages').order_by('-created_at')
    user_order_count_show = user_orders.count()


    # Booking form logic...
    total_bookings = SpaSessionBooking.objects.count()
    all_bookings = SpaSessionBooking.objects.all()


    # super admin
    total_users = User.objects.count()
    total_services = ServiceRendered.objects.count()
    total_income = ServiceRendered.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    recent_services = ServiceRendered.objects.select_related('staff_name').order_by('-service_date')[:5]
    recent_reviews = Review.objects.order_by('-created_at')[:5]
    recent_orders = Order.objects.select_related('client', 'product').order_by('-created_at')[:5]
    pending_bookings = SpaSessionBooking.objects.filter(status='pending').order_by('-created_at')[:5]



    # Pass all the data to the template
    context = {
        'user': user,
        'profile': profile,
        'staff_labels': json.dumps(staff_labels),
        'staff_data': json.dumps(staff_data),
        'months': months,  # Pass the list of months
        'month': month,
        'year': year,
        'orders': orders,
        'user_orders': user_orders,
        'user_order_count_show': user_order_count_show,
        'order_count': order_count,
        'user_order_count': user_order_count,
        'status_choices': Order.STATUS_CHOICES,

        'total_bookings': total_bookings,
        'all_bookings': all_bookings,

        # super admin
        'total_users': total_users,
        'total_services': total_services,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'recent_services': recent_services,
        'recent_reviews': recent_reviews,
        'recent_orders': recent_orders,
        'pending_bookings': pending_bookings,
    }

    return render(request, 'auth/dashboard.html', context)


@login_required(login_url='loginpage')
def StorePageView(request):
    user = request.user

    products_list = Product.objects.all().order_by('-created_at')
    paginator = Paginator(products_list, 6)  # 6 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    orders = Order.objects.select_related('client', 'product').order_by('-created_at')
    order_count = orders.count()
    user_order_count = orders.filter(client=user).count()

    user_orders = Order.objects.filter(client=user).select_related('product').prefetch_related('messages').order_by('-created_at')
    user_order_count_show = user_orders.count()

    context = {
        'products': products,
        'orders': orders,
        'order_count': order_count,
        'user_order_count': user_order_count,
        'user_orders': user_orders,
        'user_order_count_show': user_order_count_show
    }

    return render(request, 'auth/store.html', context)



@login_required(login_url='loginpage')
def PlaceOrderView(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        uploaded_file = request.FILES.get('uploaded_file')

        product = Product.objects.get(id=product_id)
        Order.objects.create(
            client=request.user,
            product=product,
            uploaded_file=uploaded_file
        )
        return redirect('dashboardpage')  # or wherever you'd like

    return redirect('dashboardpage')


@login_required(login_url='loginpage')
def BookPageView(request):
    user = request.user
    if request.method == 'POST':
        form = SpaSessionBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            form = SpaSessionBookingForm()
            messages.success(request, "Your session has been successfully booked!")
    else:
        form = SpaSessionBookingForm()

    user_bookings = SpaSessionBooking.objects.filter(user=request.user).order_by('-created_at')

    orders = Order.objects.select_related('client', 'product').order_by('-created_at')
    order_count = orders.count()
    user_order_count = orders.filter(client=user).count()

    user_orders = Order.objects.filter(client=user).select_related('product').prefetch_related('messages').order_by('-created_at')
    user_order_count_show = user_orders.count()

    context = {
        'user' : user,
        'orders': orders,
        'form': form,
        'bookings': user_bookings,
        'order_count': order_count,
        'user_order_count': user_order_count,
        'user_orders': user_orders,
        'user_order_count_show': user_order_count_show
    }
    return render(request, 'auth/booksession.html', context)



@login_required(login_url='loginpage')
@admin_and_secretary_required
def UpdateBookingStatus(request, booking_id):
    booking = get_object_or_404(SpaSessionBooking, id=booking_id)

    if request.method == "POST":

        new_status = request.POST.get("status")
        if new_status:
            booking.status = new_status
            booking.save()
            messages.success(request, "Booking status updated successfully.")
        else:
            messages.error(request, "Please select a valid status.")

    return redirect('dashboardpage')



@login_required(login_url='loginpage')
@admin_and_secretary_required
def DeleteBooking(request, booking_id):
    booking = get_object_or_404(SpaSessionBooking, id=booking_id)

    if request.method == "POST":

        booking.delete()
        messages.success(request, "Booking deleted successfully.")

    return redirect('booksessionpage')



@login_required(login_url='loginpage')
def UserReviewPageView(request):
    """ review page """
    user = request.user
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            if request.user.is_authenticated:
                review.user = request.user
            review.save()
            form = ReviewForm()
            messages.success(request, "Thanks For the Review!")
        else:
            print(form.errors)  # DEBUG: Show form validation errors
    else:
        form = ReviewForm()

    orders = Order.objects.select_related('client', 'product').order_by('-created_at')
    order_count = orders.count()
    user_order_count = orders.filter(client=user).count()

    user_orders = Order.objects.filter(client=user).select_related('product').prefetch_related('messages').order_by('-created_at')
    user_order_count_show = user_orders.count()

    context = {
        'user' : user,
        'orders': orders,
        'form': form,
        'order_count': order_count,
        'user_order_count': user_order_count,
        'user_orders': user_orders,
        'user_order_count_show': user_order_count_show
    }

    return render(request, 'auth/review.html', context)


@login_required(login_url='loginpage')
@admin_required
def StaffPageView(request):
    """ staff page from admin view """
    staff_users = CustomUser.objects.filter(is_not_secretary=True)

    return render(request, 'auth/staffpage.html', {
        'staff_users': staff_users,
    })


@login_required(login_url='loginpage')
@admin_required
def UsersPageView(request):
    """ User page from admin view, with search functionality """
    query = request.GET.get('q', '')  # Get the search query
    users = CustomUser.objects.exclude(is_admin=True)

    if query:
        users = users.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(email__icontains=query)
        )

    return render(request, 'auth/users.html', {
        'users': users,
        'query': query,  # Pass the query back to the template to keep the search box filled
    })


@login_required(login_url='loginpage')
@admin_required
def EditUserView(request, user_id):
    """ Handle editing user information """
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.is_secretary = request.POST.get('is_secretary') == 'true'
        user.is_not_secretary = request.POST.get('is_not_secretary') == 'true'
        user.is_admin = request.POST.get('is_admin') == 'true'
        user.is_staff = request.POST.get('is_staff') == 'true'
        user.is_active = request.POST.get('is_active') == 'true'

        user.save()
        return redirect('userpage')

    return redirect('userpage')


@login_required(login_url='loginpage')
@admin_required
def delete_user(request, user_id):
    """ Delete a user """
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id)
        user.delete()
    return redirect('userpage')


@login_required(login_url='loginpage')
@admin_and_secretary_required
def profit_summary(request):
    # Get month and year from GET params, default to current month/year
    month = request.GET.get('month')
    year = request.GET.get('year')

    today = timezone.now()
    selected_month = int(month) if month else today.month
    selected_year = int(year) if year else today.year

    # Income
    services = ServiceRendered.objects.filter(
        service_date__month=selected_month,
        service_date__year=selected_year,
        payment_status='confirmed'
    )
    total_income = services.aggregate(total=Sum('amount'))['total'] or 0

    # Expenses
    expenses = Expense.objects.filter(
        date__month=selected_month,
        date__year=selected_year
    )
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0

    # Profit
    profit = total_income - total_expenses

    # Month list for dropdown
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]

    orders = Order.objects.select_related('client', 'product').order_by('-created_at')
    order_count = orders.count()


    # Booking form logic...
    total_bookings = SpaSessionBooking.objects.count()
    all_bookings = SpaSessionBooking.objects.all()

    context = {
        'services': services,
        'expenses': expenses,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'profit': profit,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'months': months,
        'orders': orders,
        'order_count': order_count,
        'total_bookings': total_bookings,
        'all_bookings': all_bookings,
    }
    return render(request, 'auth/summary.html', context)


@login_required(login_url='loginpage')
@not_secretary_required
def JobsPage(request):
    """ Staff job page with month/year filtering """

    user = request.user
    month = request.GET.get('month')
    year = request.GET.get('year')

    services = ServiceRendered.objects.filter(staff_name=user)

    total_amount = services.aggregate(Sum('amount'))['amount__sum'] or 0

    if month and year:
        services = services.filter(
            service_date__month=int(month),
            service_date__year=int(year)
        )

    # For the filter dropdowns
    current_year = datetime.now().year
    years = range(current_year - 5, current_year + 1)
    months = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    context = {
        'services': services,
        'months': months,
        'years': years,
        'selected_month': month,
        'selected_year': year,
        'total_amount': total_amount,
    }

    return render(request, 'auth/jobs.html', context)


@login_required(login_url='loginpage')
@admin_and_secretary_required
def download_report(request):
    month = request.GET.get('month')
    year = request.GET.get('year')

    if not month or not year:
        return redirect('profit_summary')

    month = int(month)
    year = int(year)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    left_margin = 50
    right_margin = width - 50
    top_margin = height - 50
    bottom_margin = 50

    y = top_margin

    def new_page():
        nonlocal y
        p.showPage()
        y = top_margin

    def draw_table_header(x_list, header_texts, y_position):
        p.setFont("Helvetica-Bold", 12)
        for i, text in enumerate(header_texts):
            p.drawString(x_list[i] + 2, y_position, text)

        # Draw header line under titles
        p.line(x_list[0], y_position - 2, x_list[-1] + 100, y_position - 2)

    # Draw Title
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, y, f"Monthly Report - {calendar.month_name[month]} {year}")
    y -= 50

    ## ------------------- Staff Services Section -------------------
    p.setFont("Helvetica-Bold", 16)
    p.drawString(left_margin, y, "Staff Services")
    y -= 30

    staff_members = CustomUser.objects.filter(is_not_secretary=True)
    total_income = 0

    # Table Column Positions
    x_list = [left_margin, left_margin + 150, left_margin + 350]

    # Draw the table header
    draw_table_header(x_list, ["Staff Name", "Service Rendered", "Amount (₦)"], y)
    y -= 25

    for staff in staff_members:
        services = ServiceRendered.objects.filter(
            staff_name=staff,
            service_date__month=month,
            service_date__year=year,
            payment_status='confirmed'
        )

        if services.exists():
            staff_full_name = f"{staff.first_name} {staff.last_name}"

            staff_total = 0

            for service in services:
                if y < bottom_margin + 50:
                    new_page()
                    p.setFont("Helvetica-Bold", 16)
                    p.drawString(left_margin, y, "Staff Services (contd)")
                    y -= 30
                    draw_table_header(x_list, ["Staff Name", "Service Rendered", "Amount (₦)"], y)
                    y -= 25

                p.setFont("Helvetica", 11)
                p.drawString(x_list[0] + 2, y, staff_full_name)
                p.drawString(x_list[1] + 2, y, service.service_rendered or "N/A")
                p.drawString(x_list[2] + 2, y, f"{service.amount:,.2f}")
                y -= 18

                staff_total += service.amount

            # Staff Subtotal row
            p.setFont("Helvetica-Bold", 11)
            p.drawString(x_list[1] + 2, y, f"Subtotal for {staff_full_name}")
            p.drawString(x_list[2] + 2, y, f"{staff_total:,.2f}")
            y -= 25

            total_income += staff_total

    # Total Income
    p.setStrokeColor(colors.black)
    p.line(left_margin, y, right_margin, y)
    y -= 20
    p.setFont("Helvetica-Bold", 14)
    p.drawString(left_margin, y, f"Total Income: ₦{total_income:,.2f}")
    y -= 40

    ## ------------------- Expenses Section -------------------
    if y < bottom_margin + 100:
        new_page()

    p.setFont("Helvetica-Bold", 16)
    p.drawString(left_margin, y, "Expenses")
    y -= 30

    # Table Column Positions for Expenses
    x_expense_list = [left_margin, left_margin + 250, left_margin + 400]

    draw_table_header(x_expense_list, ["Category", "Description", "Amount (₦)"], y)
    y -= 25

    expenses = Expense.objects.filter(date__month=month, date__year=year)
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0

    if expenses.exists():
        for expense in expenses:
            if y < bottom_margin + 50:
                new_page()
                p.setFont("Helvetica-Bold", 16)
                p.drawString(left_margin, y, "Expenses (contd)")
                y -= 30
                draw_table_header(x_expense_list, ["Category", "Description", "Amount (₦)"], y)
                y -= 25

            p.setFont("Helvetica", 11)
            p.drawString(x_expense_list[0] + 2, y, expense.category.capitalize())
            p.drawString(x_expense_list[1] + 2, y, (expense.description[:30] + '...') if len(expense.description) > 30 else expense.description)
            p.drawString(x_expense_list[2] + 2, y, f"{expense.amount:,.2f}")
            y -= 18
    else:
        p.setFont("Helvetica", 12)
        p.drawString(left_margin + 10, y, "No expenses recorded.")
        y -= 20

    # Total Expenses
    p.setStrokeColor(colors.black)
    p.line(left_margin, y, right_margin, y)
    y -= 20
    p.setFont("Helvetica-Bold", 14)
    p.drawString(left_margin, y, f"Total Expenses: ₦{total_expenses:,.2f}")
    y -= 40

    ## ------------------- Net Profit Section -------------------
    if y < bottom_margin + 100:
        new_page()

    final_profit = total_income - total_expenses

    p.setFont("Helvetica-Bold", 18)
    p.drawString(left_margin, y, "Net Profit Summary")
    y -= 25
    p.setStrokeColor(colors.grey)
    p.line(left_margin, y, right_margin, y)
    y -= 30

    p.setFont("Helvetica-Bold", 16)
    if final_profit >= 0:
        p.setFillColor(colors.green)
    else:
        p.setFillColor(colors.red)
    p.drawString(left_margin, y, f"Net Profit: ₦{final_profit:,.2f}")
    p.setFillColor(colors.black)

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"Monthly_Report_{calendar.month_name[month]}_{year}.pdf")



def AboutPageView(request):
    """ about page """
    return render(request, 'firstApp/aboutpage.html')


def ServicePageView(request):
    """ service page """
    
    return render(request, 'firstApp/servicepage.html')


def ReviewPageView(request):
    """ review page """
    reviews = Review.objects.all().order_by('-created_at')
    stars = range(1, 6)  # range from 1 to 5
    return render(request, 'firstApp/reviewpage.html', {'reviews': reviews, 'stars': stars})

def ContactPageView(request):
    """ contact page """
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contactpage')  # Or wherever you want to redirect
    else:
        form = ContactMessageForm()

    return render(request, 'firstApp/contactpage.html', {'form': form})


def custom_404_view(request, exception=None):
    return render(request, 'firstApp/404.html')