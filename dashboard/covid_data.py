import pandas as pd
import seaborn as sns 
import matplotlib
matplotlib.use('Agg') # Use 'Agg' backend for non-interactive plotting (essential for servers)
import matplotlib.pyplot as plt
import os
from bokeh.plotting import figure # Assuming these are used by other functions
from bokeh.embed import components # Assuming these are used by other functions
import folium # Assuming these are used by other functions
import requests # Assuming these are used by other functions
from datetime import datetime, timedelta # Ensure this is imported for date handling

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False # Prevents minus signs from being squares if font issue persists

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')
IMAGES_DIR = os.path.join(STATIC_DIR, 'images')

os.makedirs(IMAGES_DIR, exist_ok=True)


# Helper function to load and clean data - used by other plotting functions
def load_clean_data():
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'covid_data.csv')
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: CSV file not found at '{csv_path}' for load_clean_data.")
        csv_path_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'covid_data.csv')
        try:
            df = pd.read_csv(csv_path_root)
            print(f"Loaded CSV from project root: '{csv_path_root}'")
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found at '{csv_path}' or '{csv_path_root}'.")

    df['ObservationDate'] = pd.to_datetime(df['ObservationDate'])
    df = df.dropna()
    df = df[df['Confirmed'] > 0]
    return df

# --- Your other plotting functions (plot_cases_over_time, plot_top_deaths_by_country, etc.) ---
# ... (Keep them as they were in your covid_data.py file) ...
def plot_cases_over_time():
    df = load_clean_data()
    plt.figure(figsize=(10, 5))
    sns.set(style="darkgrid")
    sns.lineplot(data=df, x='ObservationDate', y='Confirmed', color='#e63946')
    plt.title("📈 Confirmed COVID-19 Cases Over Time", fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Confirmed Cases")
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, 'plot1_cases.png')) 
    plt.close()

def plot_top_deaths_by_country():
    df = load_clean_data()
    latest = df[df['ObservationDate'] == df['ObservationDate'].max()]
    top_countries = latest.groupby('Country/Region')['Deaths'].sum().nlargest(10).reset_index()

    plt.figure(figsize=(10,6))
    sns.barplot(data=top_countries, x='Deaths', y='Country/Region', hue='Country/Region', legend=False, palette='Reds_r') 
    plt.title("🔴 Top 10 Countries by COVID-19 Deaths")
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, 'plot2_deaths.png'))
    plt.close()


def plot_case_distribution():
    df = load_clean_data()
    latest = df[df['ObservationDate'] == df['ObservationDate'].max()]
    summary = latest[['Confirmed', 'Deaths', 'Recovered']].sum()
    
    plt.figure(figsize=(7,7))
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    plt.pie(summary, labels=summary.index, autopct='%1.1f%%', colors=colors, startangle=140)
    plt.title("📊 Case Distribution") 
    plt.savefig(os.path.join(IMAGES_DIR, 'plot3_pie.png'))
    plt.close()
    

def plot_area_confirmed_recovered():
    df = load_clean_data()
    daily = df.groupby('ObservationDate')[['Confirmed', 'Recovered']].sum().reset_index()
    
    plt.figure(figsize=(10,6))
    plt.stackplot(daily['ObservationDate'], daily['Confirmed'], daily['Recovered'],
                  labels=['Confirmed', 'Recovered'], colors=['#ffbe0b', '#06d6a0'])
    plt.legend(loc='upper left')
    plt.title("📉 Confirmed vs Recovered Over Time")
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, 'plot4_area.png'))
    plt.close()


def plot_bokeh_cases():
    df = load_clean_data()
    p = figure(title='🧭 Interactive Confirmed Cases',
               x_axis_label='Date', y_axis_label='Confirmed',
               x_axis_type='datetime', width=800, height=450, # Adjusted Bokeh plot size
               tools="pan,wheel_zoom,box_zoom,reset,save,hover") # Added common tools
    p.line(df['ObservationDate'], df['Confirmed'], line_width=2, color='#0077b6', legend_label='Confirmed')
    p.legend.location = "top_left"
    script, div = components(p)
    return script, div

def generate_folium_map():
    """
    Generates an interactive Folium map centered on Lahore,
    displaying example COVID-19 case data with CircleMarkers.
    The map is saved as 'folium_map.html' in the static directory.
    """
    # Ensure the static directory exists
    os.makedirs(STATIC_DIR, exist_ok=True)

    # Initialize the map centered on Lahore
    m = folium.Map(location=[31.5497, 74.3436], zoom_start=13, tiles='cartodbpositron')

    case_data = [
        {"location": "Johar Town", "lat": 31.4700, "lon": 74.2790, "cases": 150},
        {"location": "Model Town", "lat": 31.4890, "lon": 74.3255, "cases": 120},
        {"location": "Gulberg", "lat": 31.5243, "lon": 74.3515, "cases": 90},
        {"location": "Shadman", "lat": 31.5590, "lon": 74.3182, "cases": 70},
        {"location": "DHA Phase 5", "lat": 31.4567, "lon": 74.3921, "cases": 200},
        {"location": "Ferozepur Road", "lat": 31.4500, "lon": 74.3100, "cases": 180},
        {"location": "Raiwind Road", "lat": 31.3900, "lon": 74.2100, "cases": 100},
    ]

    for data in case_data:
        folium.CircleMarker(
            location=[data["lat"], data["lon"]],
            radius=min(data["cases"] / 20, 20),
            color='crimson',
            fill=True,
            fill_color='crimson',
            fill_opacity=0.6,
            tooltip=f"{data['location']}: {data['cases']} cases"
        ).add_to(m)
    output_path = os.path.join(STATIC_DIR, 'folium_map.html')
    m.save(output_path)


def generate_global_map():
    df = load_clean_data()

    coords_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'country_coordinates.csv')
    try:
        coords = pd.read_csv(coords_path)
    except FileNotFoundError:
        print(f"Error: country_coordinates.csv not found at '{coords_path}'.")
        coords_path_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'country_coordinates.csv')
        try:
            coords = pd.read_csv(coords_path_root)
            print(f"Loaded country_coordinates.csv from project root: '{coords_path_root}'")
        except FileNotFoundError:
            print("Error: country_coordinates.csv not found in expected locations. Skipping global map.")
            return

    latest = df[df['ObservationDate'] == df['ObservationDate'].max()]
    latest_grouped = latest.groupby('Country/Region')[['Confirmed']].sum().reset_index()

    merged = pd.merge(latest_grouped, coords, on='Country/Region', how='inner')

    top10 = merged.sort_values(by='Confirmed', ascending=False).head(10)

    m = folium.Map(location=[20, 0], zoom_start=2, tiles='cartodbpositron')

    for _, row in top10.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=10,
            color='crimson',
            fill=True,
            fill_opacity=0.8,
            tooltip=f"{row['Country/Region']}: {int(row['Confirmed'])} cases"
        ).add_to(m)

    m.save(os.path.join(STATIC_DIR, 'folium_global.html')) 


def plot_scatter_confirmed_vs_deaths():
    df = load_clean_data()
    latest = df[df['ObservationDate'] == df['ObservationDate'].max()]
    
    plt.figure(figsize=(8,6))
    plt.scatter(latest['Confirmed'], latest['Deaths'], alpha=0.6, color='#ff006e')
    plt.title("🧪 Confirmed vs Deaths")
    plt.xlabel("Confirmed Cases")
    plt.ylabel("Deaths")
    plt.grid(True)
    plt.savefig(os.path.join(IMAGES_DIR, 'plot5_scatter.png'))
    plt.close()


def plot_correlation_heatmap():
    df = load_clean_data()
    corr = df[['Confirmed', 'Deaths', 'Recovered']].corr()
    
    plt.figure(figsize=(6,5))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title("📊 Correlation Matrix")
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, 'plot6_heatmap.png'))
    plt.close()


def plot_bokeh_daily_new_cases():
    df = load_clean_data()
    df_new_cases = df.groupby('ObservationDate')['Confirmed'].sum().diff().fillna(0).reset_index(name='NewCases')
    
    df_new_cases['NewCases'] = df_new_cases['NewCases'].apply(lambda x: max(0, x))

    p = figure(title='📆 Daily New Confirmed Cases',
               x_axis_type='datetime', width=800, height=450, 
               tools="pan,wheel_zoom,box_zoom,reset,save,hover")
    p.vbar(x=df_new_cases['ObservationDate'], top=df_new_cases['NewCases'], width=0.9, color='#ffb703')
    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "New Confirmed Cases"
    script, div = components(p)
    return script, div


def plot_pakistan_vs_world():
    df = load_clean_data()
    df['Country/Region'] = df['Country/Region'].str.strip()
    
    pakistan = df[df['Country/Region'] == 'Pakistan'].groupby('ObservationDate')['Confirmed'].sum().reset_index()
    # Corrected world aggregation
    world = df.groupby('ObservationDate')['Confirmed'].sum().reset_index() 

    plt.figure(figsize=(10,5))
    plt.plot(world['ObservationDate'], world['Confirmed'], label='🌍 Global', color='gray')
    plt.plot(pakistan['ObservationDate'], pakistan['Confirmed'], label='🇵🇰 Pakistan', color='green')
    plt.title("📊 Pakistan vs Global Confirmed Cases")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, 'plot7_pak_vs_world.png'))
    plt.close()


def save_summary_stats():
    df = load_clean_data()
    latest = df[df['ObservationDate'] == df['ObservationDate'].max()]
    summary = latest.groupby('Country/Region')[['Confirmed', 'Deaths', 'Recovered']].sum().sort_values(by='Confirmed', ascending=False).head(30)
    summary.to_html(os.path.join(STATIC_DIR, 'summary_table.html'), classes='table table-striped table-bordered')

def save_bokeh_components():
    script1, div1 = plot_bokeh_cases()
    script2, div2 = plot_bokeh_daily_new_cases()

    with open(os.path.join(STATIC_DIR, 'bokeh_script1.js'), 'w') as f:
        f.write(script1)
    with open(os.path.join(STATIC_DIR, 'bokeh_div1.html'), 'w') as f:
        f.write(div1)
    with open(os.path.join(STATIC_DIR, 'bokeh_script2.js'), 'w') as f:
        f.write(script2)
    with open(os.path.join(STATIC_DIR, 'bokeh_div2.html'), 'w') as f:
        f.write(div2)


# --- THIS IS THE MODIFIED plot_covid_data FUNCTION TO HANDLE ONE OR TWO COUNTRIES ---
def plot_covid_data(
    df: pd.DataFrame, # Now accepts the full DataFrame directly from views.py
    country_names: list[str], # Changed from country_name to country_names (a list)
    start_date_str: str,
    end_date_str: str,
    output_file_path: str, 
    y_column: str = 'Confirmed',
    plot_type: str = 'line' # Still assuming line plot for comparison
) -> bool: 
    """
    Generates a plot comparing one or two countries for a given metric and date range,
    and saves it to the specified file path.

    Args:
        df (pd.DataFrame): The full, loaded COVID-19 DataFrame.
        country_names (list[str]): A list containing one or two country/region names to plot.
                                   If empty, or no valid countries after filtering, returns False.
        start_date_str (str): The start date for the plot in 'YYYY-MM-DD' format.
        end_date_str (str): The end date for the plot in 'YYYY-MM-DD' format.
        output_file_path (str): The full file path where the generated plot image (PNG) will be saved.
        y_column (str, optional): The column to plot on the y-axis (e.g., 'Confirmed', 'Deaths', 'Recovered').
                                   Defaults to 'Confirmed'.
        plot_type (str, optional): The type of plot to draw ('line', 'bar'). Defaults to 'line'.
                                   Note: Bar plots are generally not ideal for time series comparison of multiple lines.

    Returns:
        bool: True if the plot was successfully generated and saved, False otherwise.
    """
    # Basic validation for country_names list
    if not country_names or len(country_names) == 0:
        print("Error (plot_covid_data): No countries provided for plotting.")
        return False
    
    # Ensure we only process up to two countries for this comparison plot
    if len(country_names) > 2:
        print("Warning (plot_covid_data): More than two countries provided. Plotting only the first two.")
        country_names = country_names[:2]

    # Convert input date strings to datetime objects
    try:
        start_date = pd.to_datetime(start_date_str)
        end_date = pd.to_datetime(end_date_str)
    except ValueError:
        print("Error (plot_covid_data): Invalid date format. Please use 'YYYY-MM-DD'.")
        return False

    # Ensure the y_column exists in the DataFrame passed to this function
    if y_column not in df.columns:
        print(f"Error (plot_covid_data): Column '{y_column}' not found in the provided DataFrame.")
        return False

    # Ensure the Y-column is numeric (perform once on the main DF if not already)
    df[y_column] = pd.to_numeric(df[y_column], errors='coerce')


    plt.figure(figsize=(12, 7)) # A good size for comparing two lines
    # Using 'Set2' palette which provides distinct and generally colorblind-friendly colors
    colors = sns.color_palette("Set2", len(country_names)) 

    actual_countries_plotted = [] # To track which countries actually had data and were plotted

    for i, country_name in enumerate(country_names):
        # Filter data for the current country and date range
        filtered_df_country = df[
            (df['Country/Region'].str.lower() == country_name.lower()) &
            (df['ObservationDate'] >= start_date) &
            (df['ObservationDate'] <= end_date)
        ].copy()
        
        # Drop rows where 'ObservationDate' or the 'y_column' became NaN after filtering/conversion
        filtered_df_country.dropna(subset=['ObservationDate', y_column], inplace=True)
        
        if filtered_df_country.empty:
            print(f"No valid data found for '{country_name}' in selected range for '{y_column}'. Skipping this country.")
            continue # Skip to the next country if no data for this country
        
        filtered_df_country.sort_values(by='ObservationDate', inplace=True) # Sort by date for plotting

        if plot_type == 'line':
            plt.plot(filtered_df_country['ObservationDate'], filtered_df_country[y_column],
                     label=country_name, # Use country name for legend
                     marker='o', markersize=4, linewidth=1.5, color=colors[i])
            actual_countries_plotted.append(country_name)
        elif plot_type == 'bar':
            # While the request mentioned 'bar', for comparison of two time series, 'line' is usually better.
            # If a bar chart is strictly needed for comparison, you'd likely want grouped bars per date,
            # which requires a different plotting approach (e.g., using sns.barplot or pandas plot).
            # For simplicity and clear comparison, we'll suggest line for multi-country.
            print(f"Warning: Bar plot type is not ideally suited for multi-country time series comparison. Plotting '{country_name}' as a line.")
            plt.plot(filtered_df_country['ObservationDate'], filtered_df_country[y_column],
                     label=f"{country_name} (Line)", marker='o', markersize=4, linewidth=1.5, color=colors[i])
            actual_countries_plotted.append(country_name)
        else:
            print(f"Error (plot_covid_data): Unsupported plot_type '{plot_type}'. Choose 'line' or 'bar'.")
            plt.close()
            return False

    if not actual_countries_plotted:
        print("Error (plot_covid_data): No data available for any of the selected countries with given filters to plot.")
        plt.close()
        return False

    # Dynamic title based on how many countries were actually plotted
    title_text = ""
    if len(actual_countries_plotted) == 1:
        title_text = f'{y_column} Cases in {actual_countries_plotted[0]}'
    elif len(actual_countries_plotted) == 2:
        title_text = f'{y_column} Cases: {actual_countries_plotted[0]} vs. {actual_countries_plotted[1]}'
    else: # Fallback, though ideally should not happen with current logic
        title_text = f'{y_column} Cases for selected countries'

    plt.title(f'{title_text} ({start_date_str} to {end_date_str})', fontsize=16)
    plt.xlabel('Observation Date', fontsize=12)
    plt.ylabel(f'Number of {y_column} Cases', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)
    plt.legend(loc='upper left', fontsize=10) # Show legend for multiple lines
    plt.tight_layout()

    # --- Save the plot to the specified file path ---
    try:
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        plt.savefig(output_file_path, format='png')
        return True
    except Exception as e:
        print(f"Error (plot_covid_data): Could not save plot to '{output_file_path}': {e}")
        raise # Re-raise the exception to be caught in views.py
    finally:
        plt.close()