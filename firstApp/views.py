from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import *
import calendar
import json
from django.db.models.functions import TruncMonth
from .models import *
from datetime import datetime, timedelta, date
from django.db.models import Count, Sum
from django.http import JsonResponse



def LandingPageView(request):
    """ landing page """
    return render(request, 'firstApp/landingpage.html')



def RegisterPageView(request):
    """Register a new user using a custom form"""
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
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

    # Render the template with the generated data, form, and uniforms
    return render(request, 'auth/calender.html', {
        'calendar_weeks': days_of_week,
        'month_name': month_name,
        'year': year,
        'form': form,  # Pass the form to the template
        'uniforms_for_month': uniforms_for_month,  # Pass the list of uniforms
    })



def RecordservicePageView(request):
    if request.method == 'POST':
        form = ServiceRenderedForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Service recorded successfully.")
            form = ServiceRenderedForm()
        else:
            print(form.errors)  # DEBUG
    else:
        form = ServiceRenderedForm()

    services = ServiceRendered.objects.order_by('-created_at')
    return render(request, 'auth/recordservice.html', {'form': form, 'services': services})


def ProfilePageView(request):
    """ Profile page """
    
    # Ensure the user is logged in
    if not request.user.is_authenticated:
        return redirect('loginpage')  # Redirect to login page if not logged in
    
    # Get the logged-in user's profile (or 404 if not found)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    return render(request, 'auth/profile.html', {'user_profile': user_profile})


def ProductPage(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('productspage')
    else:
        form = ProductForm()

    products = Product.objects.all().order_by('-created_at')  # fetch products for display
    
    return render(request, 'auth/product.html', {
        'form': form,
        'products': products,
    })



def delete_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product.delete()
    return redirect('productspage')


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
        

    context = {
        'staff_jobs': staff_jobs,
        'payment_summary': payment_summary,
        'month': month,
        'year': year,
        'month_name': month_name,
        'all_jobs': all_jobs,
        'total_amount': total_amount,
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


    # Pass all the data to the template
    context = {
        'user': user,
        'profile': profile,
        'staff_labels': json.dumps(staff_labels),
        'staff_data': json.dumps(staff_data),
        'months': months,  # Pass the list of months
        'month': month,
        'year': year,
    }

    return render(request, 'auth/dashboard.html', context)


def StorePageView(request):
    """ store page """
    return render(request, 'auth/store.html')


def BookPageView(request):
    """ book page """
    return render(request, 'auth/booksession.html')


def UserReviewPageView(request):
    """ review page """
    return render(request, 'auth/review.html')


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



def NotfoundPageView(request, exception):
    """ not found page """
    return render(request, 'auth/notfound.html', status=404)