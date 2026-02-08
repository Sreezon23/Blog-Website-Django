from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from blog_app import views as blog_app_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog_app.urls')),
    
    # ==================== AUTHENTICATION ====================
    path('accounts/login/', auth_views.LoginView.as_view(template_name='blog_app/auth/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('accounts/register/', blog_app_views.register, name='register'),
    
    # ==================== PASSWORD RESET ====================
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='blog_app/auth/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='blog_app/auth/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='blog_app/auth/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='blog_app/auth/password_reset_complete.html'), name='password_reset_complete'),
]

# ==================== STATIC & MEDIA FILES ====================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
