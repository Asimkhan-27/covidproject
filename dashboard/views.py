from django.shortcuts import render, redirect
from django.contrib import messages
from . import covid_data # Import your covid_data.py module
import os
import pandas as pd
# No longer need base64, io, matplotlib.pyplot directly here for plotting
# import base64
# import io
# import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import uuid # Needed to generate unique filenames for saved plots
from django.conf import settings # Needed to access STATIC_URL and BASE_DIR

def generate_all_dashboard_static_content():
    """
    Calls all functions in covid_data.py that generate plots, maps, tables, and Bokeh visualizations,
    saving them to the static directory.
    """
    print("Starting generation of my static COVID-19 dashboard content...")
    try:
        # Ensure the general IMAGES_DIR from covid_data.py is created if not exists
        # This will be handled by the STATIC_DIR logic in covid_data.py,
        # but calling os.makedirs explicitly here ensures it for all general plots.
        # This assumes IMAGES_DIR in covid_data.py is relative to STATIC_DIR which is set correctly.
        
        # A more robust approach for production would involve STATIC_ROOT,
        # but for development and basic setup, creating dirs within your app's static
        # or a project-level static directory that STATICFILES_DIRS points to is fine.
        
        # Ensure the base static directory for this app exists (if it's app-specific)
        app_static_dir_for_general_plots = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        os.makedirs(os.path.join(app_static_dir_for_general_plots, 'images'), exist_ok=True)


        covid_data.plot_cases_over_time()
        covid_data.plot_top_deaths_by_country()
        covid_data.plot_case_distribution()
        covid_data.plot_area_confirmed_recovered()
        covid_data.plot_scatter_confirmed_vs_deaths()
        covid_data.plot_correlation_heatmap()
        covid_data.plot_pakistan_vs_world()
        
        covid_data.generate_folium_map()
        covid_data.generate_global_map()
        covid_data.save_summary_stats()

        covid_data.save_bokeh_components()

        print("All static content (including Bokeh) generated successfully.")
        return True
    except Exception as e:
        print(f"Error generating static content: {e}")
        messages.error(None, f'Error generating static content: {e}')  # 'None' used when request isn't available
        return False

def trigger_plot_generation_view(request):
    """
    A view that triggers the generation of all static plots and maps.
    Accessible via a specific URL, typically for admin use.
    """
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            success = generate_all_dashboard_static_content()
            if success:
                messages.success(request, 'COVID-19 dashboard plots and maps successfully updated!')
            else:
                messages.error(request, 'Failed to update COVID-19 dashboard plots. Check server logs for details.')
        return redirect('admin:index')
    else:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('admin:login')


# 1. View for the Home/Welcome Page
def home_view(request):
    context = {
        'page_title': 'Welcome to the COVID-19 Data Dashboard',
        'intro_heading': 'Unveiling Global Health Insights',
        'intro_text': 'This interactive dashboard is your gateway to understanding the intricate patterns and impacts of the COVID-19 pandemic worldwide. Built with robust data analysis and cutting-edge visualization tools, it offers a dynamic perspective on confirmed cases, mortality rates, and recovery trends. Explore granular data, compare country-specific trajectories, and gain a deeper appreciation for the global health landscape. My mission is to empower informed understanding through accessible and visually compelling data.',
        'call_to_action_link': 'dashboard:dashboard_charts', 
        'call_to_action_text': 'Explore Interactive Charts',
        'image_url': 'images/virus_data_network.jpg' 
    }
    return render(request, 'home.html', context) 

# 2. View for the Dashboard Charts Page
def dashboard_charts_view(request):
    
    base_static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')

    try:
        with open(os.path.join(base_static_path, 'bokeh_script1.js'), 'r') as f:
            bokeh_script1 = f.read()
        with open(os.path.join(base_static_path, 'bokeh_div1.html'), 'r') as f:
            bokeh_div1 = f.read()
        with open(os.path.join(base_static_path, 'bokeh_script2.js'), 'r') as f:
            bokeh_script2 = f.read()
        with open(os.path.join(base_static_path, 'bokeh_div2.html'), 'r') as f:
            bokeh_div2 = f.read()
    except FileNotFoundError:
        bokeh_script1 = bokeh_div1 = bokeh_script2 = bokeh_div2 = ''
        print("Warning: Bokeh static files not found. Make sure to run the generation function.")

    context = {
        'plot1_cases': 'images/plot1_cases.png',
        'plot2_deaths': 'images/plot2_deaths.png',
        'plot3_pie': 'images/plot3_pie.png',
        'plot4_area': 'images/plot4_area.png',
        'plot5_scatter': 'images/plot5_scatter.png',
        'plot6_heatmap': 'images/plot6_heatmap.png',
        'plot7_pak_vs_world': 'images/plot7_pak_vs_world.png',

        'bokeh_script1': bokeh_script1,
        'bokeh_div1': bokeh_div1,
        'bokeh_script2': bokeh_script2,
        'bokeh_div2': bokeh_div2,
    }

    return render(request, 'dashboard_charts.html', context)


# 3. View for the Summary Statistics Page
def summary_view(request):
    context = {
        'page_title': 'Global COVID-19 Summary Statistics',
        'intro_heading': 'Comprehensive Overview',
        'intro_text': 'This page provides tabulated overviews of key COVID-19 metrics, allowing for quick comparisons and detailed review of cumulative statistics across nations.',
    }
    return render(request, 'summary.html', context) 

# 4. View for the About Project Page
def about_project_view(request):

    context = {
        'page_title': 'About This COVID-19 Dashboard Project',
        'intro_heading': 'My Mission & Methodology',
        'intro_text': 'This COVID-19 Data Dashboard was developed as a comprehensive tool to visualize and analyze the global impact of the pandemic. My mission is to transform complex datasets into accessible and actionable insights, empowering researchers, policymakers, and the public to better understand the crisis.',
        'purpose_text': 'The primary purpose of this project is to provide a clear, interactive platform for tracking COVID-19 data. I aim to highlight trends, geographical distribution, and the severity of the pandemic through various statistical and geospatial visualizations. By synthesizing data from reliable sources, I strive to offer an objective perspective on the unfolding health crisis.',
        'data_source_heading': 'Data Sources & Reliability',
        'data_sources_list': [
            'World Health Organization (WHO) Public Datasets',
            'Johns Hopkins University CSSE COVID-19 Data',
            'Official government public health records (aggregated and anonymized)',
            'Updated periodically to ensure the latest available information is reflected.'
        ],
        'technologies_heading': 'Technologies Powering This Dashboard',
        'technologies_list': [
            'Django (Python Web Framework): For robust backend development and dynamic content serving.',
            'Pandas (Data Manipulation & Analysis): For efficient data loading, cleaning, and transformation.',
            'Matplotlib & Seaborn (Static Plotting): For creating high-quality statistical graphs.',
            'Bokeh (Interactive Plotting): For dynamic, zoomable, and hover-enabled visualizations.',
            'Folium (Geospatial Data Visualization): For interactive mapping of global COVID-19 data.',
            'HTML5, CSS3, JavaScript: For a responsive and engaging frontend user experience.',
            'Custom CSS with Variables & Grid/Flexbox: Ensuring modern aesthetics and maintainability.',
        ]
    }
    return render(request, 'about_project.html', context)


CSV_FILE_PATH = os.path.join(settings.BASE_DIR, 'dashboard' ,'covid_data.csv') 

def live_chart_view(request):
    
    # --- 1. Define Default Values ---
    default_country1 = 'US' # Mandatory default for Country 1
    default_country2 = ''   # Optional default for Country 2 (empty string means no selection)
    default_y_column = 'Confirmed'
    # Set default dates to a range that is likely to exist in historical COVID-19 data
    end_date_default = datetime(2021, 12, 31) # Example: End of 2021
    start_date_default = datetime(2020, 1, 22) # Example: Early in the pandemic

    # --- 2. Retrieve Parameters from GET Request or Use Defaults ---
    country1 = request.GET.get('country1', default_country1)
    country2 = request.GET.get('country2', default_country2) 
    y_column = request.GET.get('y_column', default_y_column)
    start_date_str = request.GET.get('start_date', start_date_default.strftime('%Y-%m-%d'))
    end_date_str = request.GET.get('end_date', end_date_default.strftime('%Y-%m-%d'))

    plot_url = None
    error_message = None
    all_countries_from_csv = [] # This will hold all unique country names for the dropdowns

    try:
        # --- Load and Preprocess Data for All Operations ---
        main_df = pd.read_csv(CSV_FILE_PATH)
        main_df['ObservationDate'] = pd.to_datetime(main_df['ObservationDate'], errors='coerce')
        main_df.dropna(subset=['ObservationDate'], inplace=True) 

        # Get all unique countries for the dropdowns
        all_countries_from_csv = sorted(main_df['Country/Region'].dropna().unique().tolist())
        
        if not all_countries_from_csv:
            error_message = "No country data found in the CSV. Please check the 'Country/Region' column and data integrity."
            raise ValueError(error_message) 

        # --- Prepare list of countries to plot based on user selection ---
        countries_to_plot = []
        if country1:
            countries_to_plot.append(country1)
        # Add country2 only if it's selected and it's not the same as country1
        if country2 and country2 != country1: 
            countries_to_plot.append(country2)
        
        if not countries_to_plot:
            error_message = "Please select at least one country to plot."
            raise ValueError(error_message)

        # Validate that selected countries actually exist in our master list
        final_countries_to_plot = [c for c in countries_to_plot if c in all_countries_from_csv]
        
        if not final_countries_to_plot:
            error_message = "None of the selected countries were found in the dataset for the given criteria. Please check your selections."
            raise ValueError(error_message)
        
        # --- Define where the plot image will be saved and its public URL ---
        filename_parts = [c.replace(' ', '_').replace('/', '_') for c in final_countries_to_plot]
        if not filename_parts:
            filename_suffix = "no_countries_selected"
        elif len(filename_parts) == 1:
            filename_suffix = filename_parts[0]
        else: # Two countries selected
            filename_suffix = f"{filename_parts[0]}_vs_{filename_parts[1]}"

        # Add a short UUID hex string to the filename to ensure uniqueness for caching
        plot_filename = f"live_covid_plot_{filename_suffix}_{y_column}_{start_date_str}_{end_date_str}_{uuid.uuid4().hex[:8]}.png" 
        
        app_static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        plot_storage_full_path = os.path.join(app_static_dir, 'images', 'plots')
        
        os.makedirs(plot_storage_full_path, exist_ok=True) 
        full_output_file_path = os.path.join(plot_storage_full_path, plot_filename)
        
        # --- Call plot_covid_data to generate and save the plot ---
        plot_success = covid_data.plot_covid_data(
            df=main_df, # Pass the full DataFrame
            country_names=final_countries_to_plot, # Pass the (validated) list of countries to plot
            start_date_str=start_date_str,
            end_date_str=end_date_str,
            y_column=y_column,
            output_file_path=full_output_file_path
        )

        if plot_success:
            # Construct the URL that the browser will use to access the image.
            relative_url_path_from_static_root = os.path.join('images', 'plots', plot_filename)
            plot_url = os.path.join(settings.STATIC_URL, relative_url_path_from_static_root).replace(os.sep, '/')
        else:
            # This error message is set if plot_covid_data returns False
            # (e.g., if no data found for selected countries/dates within the plotting function)
            error_message = "No data found for the selected countries and date range to generate the chart. Please try different selections or check if the selected countries have data in this period."

    except FileNotFoundError as fnfe:
        error_message = f"Data file not found: '{CSV_FILE_PATH}'. Please ensure the CSV file exists at this location."
    except pd.errors.EmptyDataError:
        error_message = f"The CSV file '{CSV_FILE_PATH}' is empty or corrupted. Please check its content."
    except ValueError as ve: 
        error_message = str(ve)
    except Exception as e:
        error_message = "An unexpected error occurred while processing your request. Please try again or contact support."
        #traceback.print_exc() # Print full traceback for debugging

    context = {
        'all_countries': all_countries_from_csv, # All countries for both dropdowns
        'country1': country1, # Selected country 1 (for pre-selection)
        'country2': country2, # Selected country 2 (for pre-selection)
        'y_column': y_column,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'plot_url': plot_url,
        'error': error_message, # Pass the friendly error message
    }

    return render(request, 'templates/live_chart.html', context)
