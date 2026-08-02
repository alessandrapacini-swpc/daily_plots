import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

def plot_xray_flux(df, title, ylabel, fig_name):
    """Helper function to plot GOES X-ray flux data."""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df['time_tag'], df['flux'], label=df['energy'].iloc[0], color='red')
    ax.set_yscale('log')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate()
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
    fig, ax = plt.subplots(figsize=(12, 6))
    unique_bands = df['energy'].unique()
    for band in unique_bands:
        df_band = df[df['energy'] == band]
        ax.plot(df_band['time_tag'], df_band['flux'], label=f'{legend_prefix} {band}')
    ax.set_yscale('log')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate()
    ax.set_title(title)
    ax.set_xlabel('Time (UTC)')
    ax.set_ylabel(ylabel)
    ax.legend(loc='upper right')
    ax.grid(True, which="major", linestyle="-", alpha=0.6)
    ax.grid(True, which="minor", linestyle="--", alpha=0.3)
    plt.tight_layout()
    return fig

def generate_and_save_noaa_plots():
    print("Fetching data from NOAA...")
    url1 = "https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json"
    url2 = "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json"
    url3 = "https://services.swpc.noaa.gov/json/goes/primary/integral-electrons-1-day.json"

    response1 = requests.get(url1)
    data1 = response1.json()

    response2 = requests.get(url2)
    data2 = response2.json()

    response3 = requests.get(url3)
    data3 = response3.json()

    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)
    df3 = pd.DataFrame(data3)

    df1['time_tag'] = pd.to_datetime(df1['time_tag'])
    df2['time_tag'] = pd.to_datetime(df2['time_tag'])
    df3['time_tag'] = pd.to_datetime(df3['time_tag'])

    # --- X-ray Flux Plot ---
    df_long = df1[df1['energy'] == '0.1-0.8nm']
    fig_xray = plot_xray_flux(df_long, 'GOES Primary X-ray Flux (Past 24 Hours)', 'Flux ($W/m^2$)', 'goes_xray_flux')

    # --- Proton Flux Plot ---
    fig_proton = plot_particle_flux(df2, 'GOES Primary Integral Proton Flux (Past 24 Hours)', 'Flux (particles/cm$^2$sr)', 'Protons')

    # --- Electron Flux Plot ---
    fig_electron = plot_particle_flux(df3, 'GOES Primary Integral Electron Flux (Past 24 Hours)', 'Flux (electrons/cm$^2$sr)', 'Electrons')

    # --- Save Plots locally in the GitHub workspace ---
    plot_dir = 'NOAA_Plots'
    os.makedirs(plot_dir, exist_ok=True)

    fig_xray.savefig(os.path.join(plot_dir, 'goes_xray_flux.jpg'), bbox_inches='tight')
    print(f"Saved GOES X-ray Flux plot to {os.path.join(plot_dir, 'goes_xray_flux.jpg')}")

    fig_proton.savefig(os.path.join(plot_dir, 'goes_proton_flux.jpg'), bbox_inches='tight')
    print(f"Saved GOES Integral Proton Flux plot to {os.path.join(plot_dir, 'goes_proton_flux.jpg')}")

    fig_electron.savefig(os.path.join(plot_dir, 'goes_electron_flux.jpg'), bbox_inches='tight')
    print(f"Saved GOES Integral Electron Flux plot to {os.path.join(plot_dir, 'goes_electron_flux.jpg')}")

    # Close plots to free up memory
    plt.close(fig_xray)
    plt.close(fig_proton)
    plt.close(fig_electron)

if __name__ == "__main__":
    generate_and_save_noaa_plots()
