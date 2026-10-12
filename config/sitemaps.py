from django.contrib.sitemaps import Sitemap

from accounts.models import Company
from jobs.models import Job


# ============================================================
# JOB SITEMAP
# ============================================================

class JobSitemap(Sitemap):
    # How often the sitemap content is expected to change
    changefreq = "daily"

    # Priority of job URLs in the sitemap
    priority = 0.9

    def items(self):
        # Return only active jobs
        return Job.objects.filter(is_active=True)


# ============================================================
# COMPANY SITEMAP
# ============================================================

class CompanySitemap(Sitemap):
    # How often company information is expected to change
    changefreq = "weekly"

    # Priority of company URLs in the sitemap
    priority = 0.7

    def items(self):
        # Return only companies whose employer account is active
        return Company.objects.filter(employer__is_active=True)