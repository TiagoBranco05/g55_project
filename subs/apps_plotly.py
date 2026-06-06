
from flask import render_template, session
import os
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'G55.db')

BLUE     = '#1a3a5c'
ACCENT   = '#2e6da4'
ORANGE   = '#d4622a'
TEAL     = '#1a6e7a'
LAVENDER = '#5c4a8a'
DAYS     = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

PALETTE = [
    '#1a3a5c','#2e6da4','#4a9fd4','#7bbfe8',
    '#d4622a','#e8924a','#2a7a4b','#a0cfa8','#b0b0b0'
]

def apps_plotly():
    engine = create_engine('sqlite:///' + DB_PATH)

    df_red = pd.read_sql('SELECT * FROM Redemption', engine)
    df_pro = pd.read_sql('SELECT * FROM Promotion',  engine)
    df_air = pd.read_sql('SELECT * FROM Airline',    engine)
    df_ap  = pd.read_sql('SELECT * FROM AirlinePromotion', engine)
    df_rew = pd.read_sql('SELECT * FROM Reward',     engine)

    df_red['redemption_date'] = pd.to_datetime(df_red['redemption_date'])
    df_red['week']  = df_red['redemption_date'].dt.to_period('W').astype(str)
    df_red['dow']   = df_red['redemption_date'].dt.dayofweek
    df_red['weekno']= df_red['redemption_date'].dt.isocalendar().week.astype(int)

  

    merged = (df_red
              .merge(df_ap, on='promotion_id')
              .merge(df_air[['airline_id','name']], on='airline_id'))

    top_airlines = (merged.groupby('name')['miles_used']
                          .sum().sort_values(ascending=True).tail(10))
    a_min, a_max = top_airlines.min(), top_airlines.max()

    weekly = df_red.groupby('week').size().reset_index(name='count')

    miles_vals = df_red['miles_used'].values

    top_pass = (df_red.groupby('passenger_id')['miles_used']
                      .sum().sort_values(ascending=True).tail(10)
                      .reset_index())
    top_pass['passenger_id'] = top_pass['passenger_id'].astype(str)
    p_min = top_pass['miles_used'].min()
    p_max = top_pass['miles_used'].max()

    reward_miles = (df_red
                    .merge(df_pro[['promotion_id','reward_id']], on='promotion_id')
                    .merge(df_rew[['reward_id','name']], on='reward_id')
                    .groupby('name')['miles_used'].sum()
                    .sort_values(ascending=False))
    top8 = reward_miles.head(8)
    other = reward_miles.iloc[8:].sum()
    if other > 0:
        top8 = pd.concat([top8, pd.Series({'Other': other})])

    hm = (df_red.groupby(['weekno','dow']).size()
                .reset_index(name='count'))
    pivot = hm.pivot(index='dow', columns='weekno', values='count').fillna(0)



    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Top 10 Airlines by Miles Redeemed',
            'Weekly Redemption Volume',
            'Miles Used Distribution',
            'Top 10 Passengers by Total Miles',
            'Miles Redeemed by Reward Type',
            'Redemption Intensity: Day of Week × Calendar Week',
        ),
        specs=[
            [{'type': 'xy'},     {'type': 'xy'}],
            [{'type': 'xy'},     {'type': 'xy'}],
            [{'type': 'domain'}, {'type': 'heatmap'}],
        ],
        vertical_spacing=0.13,
        horizontal_spacing=0.12,
        column_widths=[0.5, 0.5],
        row_heights=[0.33, 0.33, 0.34],
    )

    


    fig.add_trace(go.Bar(
        x=top_airlines.values / 1_000_000,
        y=top_airlines.index,
        orientation='h',
        marker=dict(
            color=top_airlines.values,
            colorscale=[[0,'#9dc6e8'],[1,BLUE]],
            showscale=False,
        ),
        hovertemplate='<b>%{y}</b><br>%{x:.3f}M miles<extra></extra>',
        name='',
    ), row=1, col=1)
    fig.update_xaxes(
        range=[a_min/1e6*0.90, a_max/1e6*1.02],
        title_text='Total Miles (M)', row=1, col=1)
    fig.update_yaxes(tickfont=dict(size=9), row=1, col=1)

    


    fig.add_trace(go.Scatter(
        x=weekly['week'], y=weekly['count'],
        mode='lines+markers',
        line=dict(color=ORANGE, width=2),
        marker=dict(size=5, color=ORANGE),
        fill='tozeroy', fillcolor='rgba(212,98,42,0.12)',
        hovertemplate='Week: %{x}<br>Redemptions: %{y}<extra></extra>',
        name='',
    ), row=1, col=2)
    fig.update_xaxes(title_text='Week', tickangle=35,
                     tickfont=dict(size=8), row=1, col=2)
    fig.update_yaxes(title_text='Redemptions', row=1, col=2)

    


    fig.add_trace(go.Histogram(
        x=miles_vals, nbinsx=30,
        marker=dict(color=TEAL,
                    line=dict(color='white', width=0.4)),
        opacity=0.85,
        hovertemplate='Miles: %{x}<br>Count: %{y}<extra></extra>',
        name='',
    ), row=2, col=1)
    fig.update_xaxes(title_text='Miles Used', row=2, col=1)
    fig.update_yaxes(title_text='Count', row=2, col=1)

    


    fig.add_trace(go.Bar(
        x=top_pass['miles_used'] / 1000,
        y=top_pass['passenger_id'],
        orientation='h',
        marker=dict(
            color=top_pass['miles_used'].values,
            colorscale=[[0,'#c4a8e8'],[1,LAVENDER]],
            showscale=False,
        ),
        hovertemplate='Passenger %{y}<br>%{x:.1f}k miles<extra></extra>',
        name='',
    ), row=2, col=2)
    fig.update_xaxes(
        range=[p_min/1000*0.90, p_max/1000*1.02],
        title_text='Total Miles (k)', row=2, col=2)
    fig.update_yaxes(tickfont=dict(size=9), row=2, col=2)

    


    fig.add_trace(go.Pie(
        labels=top8.index,
        values=top8.values,
        hole=0.46,
        marker=dict(colors=PALETTE[:len(top8)],
                    line=dict(color='white', width=1.5)),
        textinfo='label+percent',
        textfont=dict(size=9),
        hovertemplate='<b>%{label}</b><br>%{value:,.0f} miles<br>%{percent}<extra></extra>',
        sort=False,
        name='',
    ), row=3, col=1)

    total_b = reward_miles.sum() / 1e9
    fig.add_annotation(
        text=f'{total_b:.2f}B<br>miles',
        x=0.195, y=0.105,
        xref='paper', yref='paper',
        showarrow=False,
        font=dict(size=11, color=BLUE),
        align='center',
    )

    


    fig.add_trace(go.Heatmap(
        z=pivot.values,
        x=[f'W{w}' for w in pivot.columns],
        y=[DAYS[i] for i in pivot.index],
        colorscale='Blues',
        showscale=True,
        colorbar=dict(
            title=dict(text='Redemptions', side='right'),
            thickness=12, len=0.30,
            y=0.09, yanchor='bottom',
        ),
        hovertemplate='Week: %{x}<br>Day: %{y}<br>Redemptions: %{z}<extra></extra>',
        name='',
    ), row=3, col=2)
    fig.update_xaxes(tickfont=dict(size=8), tickangle=35, row=3, col=2)
    fig.update_yaxes(autorange='reversed',
                     tickfont=dict(size=9), row=3, col=2)

    

    
    fig.update_layout(
        height=1200,
        title=dict(
            text='G55 Airline Loyalty — Interactive Dashboard',
            font=dict(size=15, color=BLUE),
            x=0.5, y=0.99,
        ),
        paper_bgcolor='#f8f8f8',
        plot_bgcolor='#ffffff',
        font=dict(family='Arial', size=11, color='#333'),
        showlegend=False,
        margin=dict(l=30, r=80, t=60, b=30),
    )

    fig.update_xaxes(showgrid=True, gridcolor='#e4e4e4', gridwidth=0.5,
                     zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='#e4e4e4', gridwidth=0.5,
                     zeroline=False)

    for ann in fig.layout.annotations:
        ann.font.size  = 12
        ann.font.color = BLUE

    plot_div = fig.to_html(
        full_html=False, div_id='my-plot',
        config={'displayModeBar': True, 'scrollZoom': False,
                'modeBarButtonsToRemove': ['lasso2d','select2d']},
    )

    return render_template('plotly.html',
                           plot_div=plot_div,
                           ulogin=session.get('user'))
