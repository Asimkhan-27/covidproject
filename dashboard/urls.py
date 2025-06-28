from django.urls import path
from . import views

app_name = 'dashboard' 

urlpatterns = [
    path('', views.home_view, name='home'), 
    
    path('charts/', views.dashboard_charts_view, name='dashboard_charts'),
    
    path('summary/', views.summary_view, name='summary'),
    
    path('about/', views.about_project_view, name='about_project'), 
    
    path('live/', views.live_chart_view, name='live_chart'),
 
    # Admin trigger URL
    path('generate-dashboard/', views.trigger_plot_generation_view, name='generate_dashboard'),
]