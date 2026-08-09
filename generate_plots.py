import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def setup_time_axis(ax):
    """Applies consistent, readable time formatting to the x-axis for 24-hour periods."""
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

def plot_xray_flux(df, title, ylabel):
    """Helper function to plot GOES X-ray flux data."""
    if df.empty:
        print(f"Warning: No data for {title}")
        return None

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df['time_tag'], df['flux'], label=df['energy'].iloc[0], color='red')
    ax.set_yscale('log')

    setup_time_axis(ax)
    fig.autofmt_xdate()

    # Fix y-axis limits to [1e-8, 1e-3]
    ax.set_ylim(1e-8, 1e-3)

    ax.set_title(title)
    ax.set_xlabel('Time (UTC)')
    ax.set_ylabel(ylabel)
    ax.legend(loc='upper right')
    ax.grid(True, which="major", linestyle="-", alpha=0.6)
    ax.grid(True, which="minor", linestyle="--", alpha=0.3)
    plt.tight_layout()
    
    return fig

def plot_particle_flux(df, title, ylabel, legend_prefix):
    """Helper function to plot GOES integral proton or electron flux data."""
    if df.empty:
        print(f"Warning: No data for {title}")
        return None

    fig, ax = plt.subplots(figsize=(12, 6))
    
    unique_bands = df['energy'].unique()
    for band in unique_bands:
        df_band = df[df['energy'] == band]
        ax.plot(df_band['time_tag'], df_band['flux'], label=f'{legend_prefix} {band}')
        
    ax.set_yscale('log')
    setup_time_axis(ax)
    fig.autofmt_xdate()
    
    ax.set_title(title)
    ax.set_xlabel('Time (UTC)')
    ax.set_ylabel(ylabel)
    ax.legend(loc='upper right')
    ax.grid(True, which="major", linestyle="-", alpha=0.6)
    ax.grid(True, which="minor", linestyle="--", alpha=0.3)
    plt.tight_layout()
    
    return fig

def fetch_noaa_data(url, session):
    """Fetches JSON data from NOAA safely."""
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return pd.DataFrame()

def generate_and_save_noaa_plots():
    print("Fetching data from NOAA...")
    
    urls = {
        'xray': "https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json",
        'proton': "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json",
        'electron': "https://services.swpc.noaa.gov/json/goes/primary/integral-electrons-1-day.json"
    }

    # Using a session keeps the connection open, making multiple requests faster
    with requests.Session() as session:
        df_xray = fetch_noaa_data(urls['xray'], session)
        df_proton = fetch_noaa_data(urls['proton'], session)
        df_electron = fetch_noaa_data(urls['electron'], session)

    plot_dir = 'NOAA_Plots'
    os.makedirs(plot_dir, exist_ok=True)

    # --- X-ray Flux Plot ---
    if not df_xray.empty:
        df_xray['time_tag'] = pd.to_datetime(df_xray['time_tag'])
        df_long = df_xray[df_xray['energy'] == '0.1-0.8nm']
        fig_xray = plot_xray_flux(df_long, 'GOES Primary X-ray Flux (Past 24 Hours)', 'GOES X 1-min X-ray [W/m$^2$]')
        
        if fig_xray:
            path = os.path.join(plot_dir, 'goes_xray_flux.jpg')
            fig_xray.savefig(path, bbox_inches='tight')
            print(f"Saved GOES X-ray Flux plot to {path}")
            plt.close(fig_xray)

    # --- Proton Flux Plot ---
    if not df_proton.empty:
        df_proton['time_tag'] = pd.to_datetime(df_proton['time_tag'])
        fig_proton = plot_particle_flux(df_proton, 'GOES Primary Integral Proton Flux (Past 24 Hours)', 'Flux (particles/cm$^2$sr)', 'Protons')
        
        if fig_proton:
            path = os.path.join(plot_dir, 'goes_proton_flux.jpg')
            fig_proton.savefig(path, bbox_inches='tight')
            print(f"Saved GOES Integral Proton Flux plot to {path}")
            plt.close(fig_proton)

    # --- Electron Flux Plot ---
    if not df_electron.empty:
        df_electron['time_tag'] = pd.to_datetime(df_electron['time_tag'])
        fig_electron = plot_particle_flux(df_electron, 'GOES Primary Integral Electron Flux (Past 24 Hours)', 'Flux (electrons/cm$^2$sr)', 'Electrons')
        
        if fig_electron:
            path = os.path.join(plot_dir, 'goes_electron_flux.jpg')
            fig_electron.savefig(path, bbox_inches='tight')
            print(f"Saved GOES Integral Electron Flux plot to {path}")
            plt.close(fig_electron)

if __name__ == "__main__":
    generate_and_save_noaa_plots()
