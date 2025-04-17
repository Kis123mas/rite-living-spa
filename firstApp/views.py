from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import *
import calendar
import json
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import TruncMonth
from .models import *
from datetime import datetime, timedelta, date
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.contrib.auth import get_user_model



def LandingPageView(request):
    """ landing page """
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
            print("Form saved successfully!")  # Debugging message after successful save
        else:
            print("Form errors: ", form.errors)  # Debugging message to see any validation errors
    else:
        form = UniformForm()

    # Query all uniforms for the current month and year
    uniforms_for_month = Uniform.objects.filter(uniform_date__year=year, uniform_date__month=month)


    orders = Order.objects.select_related('client', 'product').order_by('-created_at')
    order_count = orders.count()

    context = {
        'orders': orders,
        'order_count': order_count,
        'status_choices': Order.STATUS_CHOICES,
        'calendar_weeks': days_of_week,
        'month_name': month_name,
        'year': year,
        'form': form,
        'uniforms_for_month': uniforms_for_month,
    }
    

    # Render the template with the generated data, form, and uniforms
    return render(request, 'auth/calender.html', context)



def RecordservicePageView(request):
    if request.method == 'POST':
        form = ServiceRenderedForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Service recorded successfully.")
            form = ServiceRenderedForm()
        else:
            print(form.errors)
    else:
        form = ServiceRenderedForm()

    services = ServiceRendered.objects.order_by('-created_at')

    orders = Order.objects.select_related('client', 'product').order_by('-created_at')
    order_count = orders.count()

    context = {
        'form': form,
        'services': services,
        'orders': orders,
        'order_count': order_count,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'auth/recordservice.html', context)


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

    context = {
        'user_profile': user_profile,
        'orders': orders,
        'order_count': order_count,
        'status_choices': Order.STATUS_CHOICES,


        'user' : user,
        'orders': orders,
        'user_order_count': user_order_count,
        'user_orders': user_orders,
        'user_order_count_show': user_order_count_show
    }
    
    return render(request, 'auth/profile.html', context)


def ProductPage(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('productspage')
    else:
        form = ProductForm()

    products = Product.objects.all().order_by('-created_at')  # fetch products for display

    orders = Order.objects.select_related('client', 'product').order_by('-created_at')
    order_count = orders.count()

    context = {
        'form': form,
        'products': products,
        'orders': orders,
        'order_count': order_count,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'auth/product.html',context)



def delete_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product.delete()
    return redirect('productspage')



def UpdateOrderStatus(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
    
    return redirect(request.META.get('HTTP_REFERER', 'orders_list'))


@login_required
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


def DeleteOrder(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        order.delete()
        messages.success(request, "Order deleted successfully.")
    return redirect('dashboardpage')


@login_required
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



def RecordexpensesPageView(request):
    """ Expense recording page """
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            form = ExpenseForm()  # Clear the form after saving
    else:
        form = ExpenseForm()

    # Get the month and year from the GET request, defaulting to current month and year
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))

    # Fetch the expenses filtered by month and year
    expenses = Expense.objects.filter(date__month=month, date__year=year)

    orders = Order.objects.select_related('client', 'product').order_by('-created_at')
    order_count = orders.count()

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
    }

    return render(request, 'auth/expenses.html', context)


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
    }

    return render(request, 'auth/calculate.html', context)


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



@login_required
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



def BookPageView(request):
    user = request.user
    if request.method == 'POST':
        form = SpaSessionBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            form = SpaSessionBookingForm()
            return redirect('booksessionpage')
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

    return redirect('booksessionpage')



@login_required(login_url='loginpage')
def DeleteBooking(request, booking_id):
    booking = get_object_or_404(SpaSessionBooking, id=booking_id)

    if request.method == "POST":

        booking.delete()
        messages.success(request, "Booking deleted successfully.")

    return redirect('booksessionpage')



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
            return redirect('userreviewpage')
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


def AboutPageView(request):
    """ about page """
    return render(request, 'firstApp/aboutpage.html')


def ServicePageView(request):
    """ service page """
    
    return render(request, 'firstApp/servicepage.html')


def ProductPageView(request):
    """ products page """
    return render(request, 'firstApp/productpage.html')


def ReviewPageView(request):
    """ review page """
    return render(request, 'firstApp/reviewpage.html')


def ContactPageView(request):
    """ contact page """
    return render(request, 'firstApp/contactpage.html')


def StaffPageView(request):
    """ staff page from admin view """
    staff_users = CustomUser.objects.filter(is_not_secretary=True)

    return render(request, 'auth/staffpage.html', {
        'staff_users': staff_users,
    })



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


def delete_user(request, user_id):
    """ Delete a user """
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id)
        user.delete()
    return redirect('userpage')


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


def NotfoundPageView(request, exception):
    """ not found page """
    return render(request, 'auth/notfound.html', status=404)