"""
Gialova Lagoon Hydrological & Salinity Scenario Analysis (2001-2050)
Author: [Avwerosuo Udjoh]
Description:
    Compares Stella Architect system dynamics simulation outputs between:
      1. Baseline Scenario (Xerolagados River Disconnected, post-1960 status quo)
      2. Restoration Scenario (22 km2 Xerolagados Sub-Catchment Reconnected)
    Validates model trajectories against October 2025 field survey measurements
    (Trial 4 multiparameter probe: mean salinity 40.08 PSU, range 31.36-59.39 PSU;
    main basin mean depth 0.49 m, range 0.23-1.02 m) and generates a 300 DPI
    
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def load_and_prepare(baseline_path: str, restoration_path: str, lagoon_area_m2: float = 2_255_000.0):
    """Load Stella CSV exports and compute mean water depth (m)."""
    df_base = pd.read_csv(baseline_path)
    df_rest = pd.read_csv(restoration_path)

    years = np.arange(2001, 2001 + len(df_base))
    df_base["Year"] = years
    df_rest["Year"] = years

    df_base["Depth_m"] = df_base["Lagoon Volume"] / lagoon_area_m2
    df_rest["Depth_m"] = df_rest["Lagoon Volume"] / lagoon_area_m2

    return df_base, df_rest, years


def print_summary_statistics(df_base: pd.DataFrame, df_rest: pd.DataFrame):
    """Print comparative metrics for Historical (2001-2020) vs Projected (2021-2050)."""
    for label, df in [("Baseline (Disconnected)", df_base), ("Restoration (Reconnected)", df_rest)]:
        hist = df[df["Year"] <= 2020]
        fut = df[df["Year"] >= 2021]
        print(f"=== {label} ===")
        print(f"  2001-2020 Mean Salinity : {hist['Salinity'].mean():.2f} PSU (Max: {hist['Salinity'].max():.2f} PSU)")
        print(f"  2021-2050 Mean Salinity : {fut['Salinity'].mean():.2f} PSU (Max: {fut['Salinity'].max():.2f} PSU)")
        print(f"  2025 Simulated Salinity : {df[df['Year'] == 2025]['Salinity'].values[0]:.2f} PSU")
        print(f"  2001-2020 Mean Depth    : {hist['Depth_m'].mean():.3f} m")
        print(f"  2021-2050 Mean Depth    : {fut['Depth_m'].mean():.3f} m")
        print(f"  2025 Simulated Depth    : {df[df['Year'] == 2025]['Depth_m'].values[0]:.3f} m\n")


def plot_scenario_comparison(df_base: pd.DataFrame, df_rest: pd.DataFrame, years: np.ndarray, output_png: str):
    """Generate a high-resolution (300 DPI) 4-panel scenario comparison chart."""
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    plt.rcParams["axes.edgecolor"] = "#CBD5E1"
    plt.rcParams["axes.linewidth"] = 0.8

    fig, axes = plt.subplots(2, 2, figsize=(15, 10.5), dpi=300)
    fig.patch.set_facecolor("white")

    c_base = "#D95F02"   # Burnt Orange (Disconnected Baseline)
    c_rest = "#1B9E77"   # Teal Green (Reconnected Restoration)
    c_field = "#7570B3"  # Purple (October 2025 Field Validation)

    # Panel A: Lagoon Salinity Trajectory & 2025 Field Validation
    ax = axes[0, 0]
    ax.plot(years, df_base["Salinity"], color=c_base, lw=2.2, label="Baseline (Disconnected River)")
    ax.plot(years, df_rest["Salinity"], color=c_rest, lw=2.2, label="Restoration (22 km² River Reconnected)")
    ax.axhline(38.0, color="#475569", ls="--", lw=1.1, label="Marine Seawater (38 PSU)")
    ax.axhline(55.0, color="#B91C1C", ls=":", lw=1.2, label="Severe Hypersaline Stress (>55 PSU)")
    ax.axvspan(2021, 2050, color="#F1F5F9", alpha=0.8, zorder=0)
    ax.errorbar(
        2025, 40.08, yerr=[[40.08 - 31.36], [59.39 - 40.08]],
        fmt="o", color=c_field, ecolor=c_field, elinewidth=2, capsize=5, markersize=7, zorder=5,
        label="Oct 2025 Field Survey (Mean: 40.1 PSU)"
    )
    ax.set_title("A. Lagoon Salinity Trajectory & 2025 Field Validation", fontsize=12, fontweight="bold", loc="left", pad=10)
    ax.set_ylabel("Salinity (PSU)", fontsize=10.5, fontweight="bold")
    ax.set_ylim(0, 85)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="upper left", fontsize=8.5, frameon=True, facecolor="white", framealpha=0.9)

    # Panel B: Mean Water Depth & Hydrological Stability
    ax = axes[0, 1]
    ax.plot(years, df_base["Depth_m"], color=c_base, lw=2.2, label="Baseline Depth (Disconnected)")
    ax.plot(years, df_rest["Depth_m"], color=c_rest, lw=2.2, label="Restoration Depth (Reconnected)")
    ax.axhline(0.77, color="#0284C7", ls="--", lw=1.1, label="Overflow Sill Threshold (0.77 m)")
    ax.axhline(0.60, color="#64748B", ls="--", lw=1.1, label="Equilibrium Sea Level (0.60 m)")
    ax.errorbar(
        2025, 0.49, yerr=[[0.49 - 0.23], [1.02 - 0.49]],
        fmt="s", color=c_field, ecolor=c_field, elinewidth=2, capsize=5, markersize=6.5, zorder=5,
        label="Oct 2025 Field Depth (Main Basin Mean: 0.49 m)"
    )
    ax.axvspan(2021, 2050, color="#F1F5F9", alpha=0.8, zorder=0)
    ax.set_title("B. Mean Water Depth & Hydrological Stability (2001–2050)", fontsize=12, fontweight="bold", loc="left", pad=10)
    ax.set_ylabel("Mean Water Depth (m)", fontsize=10.5, fontweight="bold")
    ax.set_ylim(0.15, 1.15)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="upper left", fontsize=8.5, frameon=True, facecolor="white", framealpha=0.9)

    # Panel C: Freshwater Supply vs. Turc PET Evaporative Loss
    ax = axes[1, 0]
    inflow_base = (df_base["Precipitation Direct"] + df_base["Ag Withdrawal"]) / 1e6
    inflow_rest = (df_rest["Xerolagados Catchment Runoff"] + df_rest["Precipitation Direct"] + (df_rest["Ag Withdrawal"] / 5.77)) / 1e6
    pet_m3 = df_base["Evaporative loss via Turc PET"] / 1e6
    ax.plot(years, inflow_rest, color=c_rest, lw=2.0, label="Total Freshwater Inflow (Restoration)")
    ax.plot(years, inflow_base, color=c_base, lw=2.0, label="Total Freshwater Inflow (Baseline)")
    ax.plot(years, pet_m3, color="#DC2626", lw=2.2, ls="-", label="Evaporative Loss via Turc PET")
    ax.axvspan(2021, 2050, color="#F1F5F9", alpha=0.8, zorder=0)
    ax.set_title("C. Climate Warming Effect: Freshwater Supply vs. Turc PET Loss", fontsize=12, fontweight="bold", loc="left", pad=10)
    ax.set_xlabel("Simulation Year", fontsize=10.5, fontweight="bold")
    ax.set_ylabel("Annual Water Flux (Million m³/yr)", fontsize=10.5, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="upper left", fontsize=8.5, frameon=True, facecolor="white", framealpha=0.9)

    # Panel D: Net Sea Exchange Dynamics
    ax = axes[1, 1]
    ax.bar(years - 0.2, df_base["Sea exchange"] / 1e6, width=0.4, color=c_base, alpha=0.85, label="Baseline Sea Exchange (+In / -Out)")
    ax.bar(years + 0.2, df_rest["Sea exchange"] / 1e6, width=0.4, color=c_rest, alpha=0.85, label="Restoration Sea Exchange (+In / -Out)")
    ax.axhline(0, color="#334155", lw=1.0)
    ax.axvspan(2021, 2050, color="#F1F5F9", alpha=0.8, zorder=0)
    ax.set_title("D. Net Sea Exchange (+Seawater Intrusion vs. -Freshwater Flushing)", fontsize=12, fontweight="bold", loc="left", pad=10)
    ax.set_xlabel("Simulation Year", fontsize=10.5, fontweight="bold")
    ax.set_ylabel("Net Sea Exchange (Million m³/yr)", fontsize=10.5, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="lower left", fontsize=8.5, frameon=True, facecolor="white", framealpha=0.9)

    fig.suptitle(
        "Gialova Lagoon Hydrological & Salinity Scenario Analysis (2001–2050)\n"
        "GIS-Informed System Dynamics Model Validated with October 2025 Field Measurements",
        fontsize=14.5, fontweight="bold", y=0.98
    )
    plt.tight_layout(rect=[0, 0.01, 1, 0.94])
    plt.savefig(output_png, dpi=300)
    print(f"Saved high-resolution figure to: {output_png}")


if __name__ == "__main__":
    df_baseline, df_restoration, sim_years = load_and_prepare(
        baseline_path="Baseline_Disconnected.csv",
        restoration_path="Restoration_Reconnected.csv"
    )
    print_summary_statistics(df_baseline, df_restoration)
    plot_scenario_comparison(
        df_baseline, df_restoration, sim_years,
        output_png="Gialova_Scenario_Analysis_2001_2050.png"
    )
