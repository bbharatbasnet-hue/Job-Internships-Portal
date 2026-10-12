from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from accounts import views as account_views
from config.sitemaps import JobSitemap, CompanySitemap


# ============================================================
# SITEMAP CONFIGURATION
# ============================================================

sitemaps = {
    "jobs": JobSitemap,
    "companies": CompanySitemap,
}


# ============================================================
# URL PATTERNS
# ============================================================

urlpatterns = [

    # --------------------------------------------------------
    # ADMIN PANEL
    # --------------------------------------------------------

    path(
        "admin/",
        admin.site.urls,
    ),

    # --------------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------------

    path(
        "accounts/",
        include("django.contrib.auth.urls"),
    ),

    path(
        "accounts/",
        include("accounts.urls"),
    ),

    # --------------------------------------------------------
    # JOBS
    # --------------------------------------------------------

    path(
        "",
        include("jobs.urls"),
    ),

    # --------------------------------------------------------
    # COMPANIES
    # --------------------------------------------------------

    path(
        "companies/",
        account_views.company_list,
        name="company_list",
    ),

    path(
        "companies/<int:pk>/",
        account_views.company_detail,
        name="company_detail",
    ),

    # --------------------------------------------------------
    # APPLICATIONS
    # --------------------------------------------------------

    path(
        "applications/",
        include("applications.urls"),
    ),

    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    path(
        "dashboard/",
        include("dashboard.urls"),
    ),

    # --------------------------------------------------------
    # NOTIFICATIONS
    # --------------------------------------------------------

    path(
        "notifications/",
        include("notifications.urls"),
    ),

    # --------------------------------------------------------
    # API
    # --------------------------------------------------------

    path(
        "api/",
        include("config.api_urls"),
    ),

    # --------------------------------------------------------
    # PASSWORD RESET
    # --------------------------------------------------------

    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html"
        ),
        name="password_reset",
    ),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

    # --------------------------------------------------------
    # SITEMAP
    # --------------------------------------------------------

    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django_sitemap",
    ),

    # --------------------------------------------------------
    # ROBOTS.TXT
    # --------------------------------------------------------

    path(
        "robots.txt",
        lambda request: __import__(
            "django.http",
            fromlist=["HttpResponse"]
        ).HttpResponse(
            "User-agent: *\n"
            "Allow: /\n"
            "Sitemap: /sitemap.xml\n",
            content_type="text/plain",
        ),
        name="robots_txt",
    ),
]


# ============================================================
# DEVELOPMENT MEDIA FILES
# ============================================================

# Serve uploaded media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )