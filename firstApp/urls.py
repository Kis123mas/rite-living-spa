from django.urls import path
from .views import *


urlpatterns = [
    path('', LandingPageView, name='landingpage'),
    path('register', RegisterPageView, name='registerpage'),
    path('login', LoginPageView, name='loginpage'),
    path('logout', logoutView, name='logout'),
    path('dashboard', DashboardPageView, name='dashboardpage'),
    path('store', StorePageView, name='storepage'),
    path('book-session', BookPageView, name='booksessionpage'),
    path('user-review', UserReviewPageView, name='userreviewpage'),
    path('about', AboutPageView, name='aboutpage'),
    path('service', ServicePageView, name='servicepage'),
    path('products', ProductPageView, name='productpage'),
    path('review', ReviewPageView, name='reviewpage'),
    path('contact', ContactPageView, name='contactpage'),
    path('calender', CalenderPageView, name='calenderpage'),
    path('record-service', RecordservicePageView, name='recordservicepage'),
    path('record-expenses', RecordexpensesPageView, name='recordexpensespage'),
    path('calculate', CalculatePageView, name='calculate'),
    path('get-staff-jobs/<int:staff_id>/', get_staff_jobs, name='get_staff_jobs'),
    path('Profile', ProfilePageView, name='profilepage'),
    path('update-profile', UpdateProfileView, name='profileupdatepage'),
    path('product', ProductPage, name='productspage'),
    path('delete-product/<int:product_id>/', delete_product, name='delete_product'),
]