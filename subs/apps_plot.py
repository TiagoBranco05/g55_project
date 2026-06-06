
from flask import render_template, session
import os, io, base64
import pandas as pd
from sqlalchemy import create_engine
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'G55.db')


C_BLUE    = '#1a3a5c'
C_ACCENT  = '#2e6da4'
C_ORANGE  = '#d4622a'
C_GREEN   = '#2a7a4b'
C_BG      = '#f8f8f8'
C_GRID    = '#e4e4e4'

plt.rcParams.update({
    'font.family':       'DejaVu Sans',
    'font.size':         10,
    'axes.titlesize':    11,
    'axes.titleweight':  'bold',
    'axes.titlecolor':   C_BLUE,
    'axes.labelcolor':   '#444',
    'axes.labelsize':    9,
    'axes.spines.top':   False,
    'axes.spines.right': False,
    'axes.edgecolor':    '#cccccc',
    'axes.facecolor':    '#ffffff',
    'figure.facecolor':  C_BG,
    'xtick.color':       '#555',
    'ytick.color':       '#555',
    'xtick.labelsize':   8,
    'ytick.labelsize':   8,
    'grid.color':        C_GRID,
    'grid.linewidth':    0.6,
})

def apps_plot():
    engine = create_engine('sqlite:///' + DB_PATH)

    df_red = pd.read_sql('SELECT * FROM Redemption', engine)
    df_pro = pd.read_sql('SELECT * FROM Promotion',  engine)
    df_air = pd.read_sql('SELECT * FROM Airline',    engine)
    df_ap  = pd.read_sql('SELECT * FROM AirlinePromotion', engine)

    df_red['redemption_date'] = pd.to_datetime(df_red['redemption_date'])
    df_red['week'] = df_red['redemption_date'].dt.to_period('W').astype(str)

    
    merged = (df_red
              .merge(df_ap, on='promotion_id')
              .merge(df_air[['airline_id','name']], on='airline_id'))
    top_airlines = (merged.groupby('name')['miles_used']
                          .sum()
                          .sort_values(ascending=True)
                          .tail(10))
    a_min = top_airlines.min()
    a_max = top_airlines.max()

    
    weekly = df_red.groupby('week').size().reset_index(name='count')

    
    miles_vals = df_red['miles_used'].values

    
    top_pass = (df_red.groupby('passenger_id')['miles_used']
                      .sum()
                      .sort_values(ascending=True)
                      .tail(10)
                      .reset_index())
    top_pass['passenger_id'] = top_pass['passenger_id'].astype(str)
    p_min = top_pass['miles_used'].min()

    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('G55 Airline Loyalty — Data Analysis',
                 fontsize=14, fontweight='bold', color=C_BLUE, y=0.98)
    plt.subplots_adjust(hspace=0.40, wspace=0.32,
                        left=0.05, right=0.97, top=0.93, bottom=0.08)

    
    ax = axes[0, 0]
    vals_m = top_airlines.values / 1_000_000
    
    norm   = (top_airlines.values - a_min) / (a_max - a_min)
    colors = plt.cm.Blues(0.35 + norm * 0.55)
    bars   = ax.barh(top_airlines.index, vals_m, color=colors, height=0.65)
    ax.set_xlim(a_min / 1_000_000 * 0.90, a_max / 1_000_000 * 1.03)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.2fM'))
    ax.set_title('Top 10 Airlines by Miles Redeemed')
    ax.set_xlabel('Total Miles (M)')
    ax.tick_params(axis='y', labelsize=8)
    ax.grid(axis='x', linestyle='--')
    
    for bar, v in zip(bars, vals_m):
        ax.text(bar.get_width() + (a_max/1e6 - a_min/1e6)*0.005,
                bar.get_y() + bar.get_height()/2,
                f'{v:.2f}M', va='center', fontsize=7, color='#333')

    
    ax = axes[0, 1]
    xs = range(len(weekly))
    ax.fill_between(xs, weekly['count'], alpha=0.15, color=C_ORANGE)
    ax.plot(xs, weekly['count'], color=C_ORANGE, linewidth=2, marker='o',
            markersize=5, markerfacecolor='white', markeredgecolor=C_ORANGE, markeredgewidth=1.5)
    ax.set_xticks(xs)
    ax.set_xticklabels(weekly['week'], rotation=40, ha='right', fontsize=7)
    ax.set_title('Weekly Redemption Volume')
    ax.set_xlabel('Week')
    ax.set_ylabel('Redemptions')
    ax.grid(axis='y', linestyle='--')
    
    peak_i = weekly['count'].idxmax()
    ax.annotate(f"Peak: {weekly['count'][peak_i]}",
                xy=(peak_i, weekly['count'][peak_i]),
                xytext=(peak_i - 0.5, weekly['count'][peak_i] + 3),
                fontsize=7.5, color=C_ORANGE,
                arrowprops=dict(arrowstyle='->', color=C_ORANGE, lw=1))

    
    ax = axes[1, 0]
    n, bins, patches = ax.hist(miles_vals, bins=30, color=C_ACCENT,
                               edgecolor='white', linewidth=0.5, alpha=0.85)
    
    bin_centres = 0.5*(bins[:-1]+bins[1:])
    norm2 = (bin_centres - bin_centres.min()) / (bin_centres.max() - bin_centres.min())
    cm    = plt.cm.Blues
    for patch, nc in zip(patches, norm2):
        patch.set_facecolor(cm(0.35 + nc * 0.55))
    
    mean_val = miles_vals.mean()
    ax.axvline(mean_val, color=C_ORANGE, linestyle='--', linewidth=1.2)
    ax.text(mean_val + 200, ax.get_ylim()[1]*0.92, f'Mean: {mean_val:.0f}',
            color=C_ORANGE, fontsize=8)
    ax.set_title('Miles Used Distribution')
    ax.set_xlabel('Miles Used')
    ax.set_ylabel('Count')
    ax.grid(axis='y', linestyle='--')

    
    ax = axes[1, 1]
    norm3  = (top_pass['miles_used'] - p_min) / (top_pass['miles_used'].max() - p_min)
    colors3 = plt.cm.Purples(0.35 + norm3 * 0.55)
    bars4  = ax.barh(top_pass['passenger_id'],
                     top_pass['miles_used'] / 1000,
                     color=colors3, height=0.65)
    ax.set_xlim(p_min / 1000 * 0.90, top_pass['miles_used'].max() / 1000 * 1.04)
    ax.set_title('Top 10 Passengers by Total Miles')
    ax.set_xlabel('Total Miles (k)')
    ax.set_ylabel('Passenger ID')
    ax.grid(axis='x', linestyle='--')
    for bar, v in zip(bars4, top_pass['miles_used']/1000):
        ax.text(bar.get_width() + (top_pass['miles_used'].max()/1000 - p_min/1000)*0.005,
                bar.get_y() + bar.get_height()/2,
                f'{v:.1f}k', va='center', fontsize=7, color='#333')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=130)
    plt.close(fig)
    buf.seek(0)
    image = base64.b64encode(buf.getvalue()).decode('utf-8')

    return render_template('plot.html', image=image, ulogin=session.get('user'))
