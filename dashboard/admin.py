from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.urls import reverse
from .models import ChartTrigger
from .views import generate_all_dashboard_static_content

class DashboardAdminPanel(admin.ModelAdmin):
    change_list_template = "admin/dashboard_admin_panel.html"  # custom template
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        generate_url = reverse('dashboard:generate_dashboard')
        extra_context['generate_url'] = generate_url
        return super().changelist_view(request, extra_context=extra_context)

# Register with any dummy model
from .models import DummyModel
admin.site.register(DummyModel, DashboardAdminPanel)


@admin.register(ChartTrigger)
class ChartTriggerAdmin(admin.ModelAdmin):
    change_list_template = "admin/generate_charts.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate/', self.admin_site.admin_view(self.generate_charts), name='generate-charts'),
        ]
        return custom_urls + urls

    def generate_charts(self, request):
        generate_all_dashboard_static_content()
        self.message_user(request, "✅ Charts generated successfully.")
        return HttpResponseRedirect("../")