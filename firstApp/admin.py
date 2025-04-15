from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)
    search_fields = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name','last_name')}),
        ('Company Position', {'fields': ('is_secretary','is_not_secretary', 'is_admin')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)



# Create a custom admin class to display UserProfile fields more conveniently in the admin panel
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address', 'birthday', 'bio', 'facebook', 'twitter', 'instagram', 'linkedin')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')  # Allows searching by user email or name
    list_filter = ('birthday', 'facebook', 'twitter', 'instagram', 'linkedin')  # Filter by social media links
    fieldsets = (
        (None, {
            'fields': ('user', 'profile_picture', 'phone_number', 'address', 'birthday', 'bio')
        }),
        ('Social Media Links', {
            'fields': ('facebook', 'twitter', 'instagram', 'linkedin')
        }),
    )

# Register the UserProfile model with the custom admin class
admin.site.register(UserProfile, UserProfileAdmin)



class ServiceRenderedAdmin(admin.ModelAdmin):
    list_display = ['staff_name', 'amount', 'service_type', 'service_rendered', 'service_date']
    search_fields = ['staff_name__username', 'service_type']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'staff_name':
            # Only show users where is_not_secretary=True
            kwargs['queryset'] = CustomUser.objects.filter(is_not_secretary=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(ServiceRendered, ServiceRenderedAdmin)


class UniformAdmin(admin.ModelAdmin):
    list_display = ('uniform_date', 'uniform_type', 'uniform_color', 'uniform_notes')
    list_filter = ('uniform_date', 'uniform_type', 'uniform_color')
    search_fields = ('uniform_type', 'uniform_color', 'uniform_notes')
    ordering = ('uniform_date',)

    # Correcting fieldsets to use a list for fields
    fieldsets = (
        (None, {
            'fields': ('uniform_date',)
        }),
        ('Uniform Details', {
            'fields': ('uniform_type', 'uniform_color', 'uniform_notes')
        }),
    )

admin.site.register(Uniform, UniformAdmin)



@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('amount', 'category', 'date', 'description', 'created_at', 'updated_at')
    list_filter = ('category', 'date')
    search_fields = ('description', 'category')
    date_hierarchy = 'date'



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'uploaded_file', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'product', 'uploaded_file', 'status', 'created_at')
    search_fields = ('client__first_name', 'client__last_name', 'product__name')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'sender', 'sent_at')
    list_filter = ('sent_at',)
    search_fields = ('content', 'sender__username', 'order__product_name')
    ordering = ('-sent_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    
    list_display = ('name', 'rating', 'created_at')
    search_fields = ('name', 'message')
    list_filter = ('rating', 'created_at')



@admin.register(SpaSessionBooking)
class SpaSessionBookingAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'session_type',
        'service_type',
        'preferred_date',
        'preferred_time',
        'status',
        'created_at',
    )
    list_filter = ('session_type', 'service_type', 'status', 'preferred_date', 'created_at')
    search_fields = ('user__username', 'user__email', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Session Details', {
            'fields': (
                'session_type',
                'service_type',
                'preferred_date',
                'preferred_time',
                'message'
            )
        }),
        ('Status & Metadata', {
            'fields': ('status', 'created_at')
        }),
    )