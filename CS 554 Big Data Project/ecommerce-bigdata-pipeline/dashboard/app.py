#!/usr/bin/env python3
"""
Real-Time Dashboard for E-Commerce Analytics
Uses Plotly Dash for visualization
"""

import json
import threading
from collections import deque
from datetime import datetime
import os

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from kafka import KafkaConsumer
import happybase

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
HBASE_HOST = os.getenv('HBASE_HOST', 'localhost')
HBASE_PORT = int(os.getenv('HBASE_PORT', 9090))

# Data storage for real-time updates
event_data = {
    'view': deque(maxlen=100),
    'cart': deque(maxlen=100),
    'purchase': deque(maxlen=100),
    'timestamps': deque(maxlen=100)
}

brand_data = {}

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "E-Commerce Real-Time Analytics"

# Layout
app.layout = html.Div([
    html.Div([
        html.H1("E-Commerce Real-Time Analytics Dashboard", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
        html.P("Live streaming analytics powered by Kafka, Spark, and HBase",
               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': 16})
    ]),
    
    html.Div([
        # Row 1: Real-time metrics
        html.Div([
            html.Div([
                html.H3("Total Views", style={'color': '#3498db'}),
                html.H2(id='total-views', children='0', style={'fontSize': 48})
            ], className='metric-box', style={
                'width': '30%', 'display': 'inline-block', 'padding': 20,
                'backgroundColor': '#ecf0f1', 'margin': 10, 'borderRadius': 10
            }),
            
            html.Div([
                html.H3("Cart Additions", style={'color': '#f39c12'}),
                html.H2(id='total-carts', children='0', style={'fontSize': 48})
            ], className='metric-box', style={
                'width': '30%', 'display': 'inline-block', 'padding': 20,
                'backgroundColor': '#ecf0f1', 'margin': 10, 'borderRadius': 10
            }),
            
            html.Div([
                html.H3("Purchases", style={'color': '#27ae60'}),
                html.H2(id='total-purchases', children='0', style={'fontSize': 48})
            ], className='metric-box', style={
                'width': '30%', 'display': 'inline-block', 'padding': 20,
                'backgroundColor': '#ecf0f1', 'margin': 10, 'borderRadius': 10
            })
        ], style={'textAlign': 'center'}),
        
        # Row 2: Real-time event stream
        html.Div([
            dcc.Graph(id='realtime-events', style={'height': '400px'})
        ], style={'margin': 20}),
        
        # Row 3: Brand performance (from HBase batch analytics)
        html.Div([
            dcc.Graph(id='brand-performance', style={'height': '400px'})
        ], style={'margin': 20}),
        
    ]),
    
    # Update interval
    dcc.Interval(
        id='interval-component',
        interval=1000,  # Update every second
        n_intervals=0
    )
], style={'fontFamily': 'Arial, sans-serif', 'padding': 20})

# Callbacks
@app.callback(
    [Output('total-views', 'children'),
     Output('total-carts', 'children'),
     Output('total-purchases', 'children'),
     Output('realtime-events', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_realtime_metrics(n):
    """Update real-time metrics from Kafka stream"""
    
    # Calculate totals
    total_views = sum(event_data['view'])
    total_carts = sum(event_data['cart'])
    total_purchases = sum(event_data['purchase'])
    
    # Create time series chart
    figure = {
        'data': [
            go.Scatter(
                x=list(event_data['timestamps']),
                y=list(event_data['view']),
                mode='lines+markers',
                name='Views',
                line=dict(color='#3498db', width=2),
                fill='tozeroy'
            ),
            go.Scatter(
                x=list(event_data['timestamps']),
                y=list(event_data['cart']),
                mode='lines+markers',
                name='Cart Additions',
                line=dict(color='#f39c12', width=2),
                fill='tozeroy'
            ),
            go.Scatter(
                x=list(event_data['timestamps']),
                y=list(event_data['purchase']),
                mode='lines+markers',
                name='Purchases',
                line=dict(color='#27ae60', width=2),
                fill='tozeroy'
            )
        ],
        'layout': go.Layout(
            title='Real-Time Event Stream (Last 100 Windows)',
            xaxis={'title': 'Time'},
            yaxis={'title': 'Event Count'},
            hovermode='closest',
            plot_bgcolor='#ecf0f1',
            paper_bgcolor='#ffffff'
        )
    }
    
    return f"{total_views:,}", f"{total_carts:,}", f"{total_purchases:,}", figure

@app.callback(
    Output('brand-performance', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_brand_performance(n):
    """Update brand performance chart from HBase"""
    
    # Mock data (in production, read from HBase)
    brands = ['samsung', 'apple', 'sony', 'hp', 'dell', 'asus', 'lenovo', 'intel', 'msi', 'gigabyte']
    views = [450, 380, 320, 290, 260, 240, 210, 180, 150, 130]
    carts = [90, 85, 70, 60, 55, 50, 45, 40, 35, 30]
    purchases = [45, 50, 35, 30, 28, 25, 22, 20, 18, 15]
    
    figure = {
        'data': [
            go.Bar(name='Views', x=brands, y=views, marker_color='#3498db'),
            go.Bar(name='Cart', x=brands, y=carts, marker_color='#f39c12'),
            go.Bar(name='Purchases', x=brands, y=purchases, marker_color='#27ae60')
        ],
        'layout': go.Layout(
            title='Brand Performance (From Batch Analytics)',
            xaxis={'title': 'Brand'},
            yaxis={'title': 'Event Count'},
            barmode='group',
            plot_bgcolor='#ecf0f1',
            paper_bgcolor='#ffffff'
        )
    }
    
    return figure

# Kafka consumer thread
def kafka_consumer_thread():
    """Background thread to consume Kafka messages"""
    try:
        consumer = KafkaConsumer(
            'ecommerce-events',
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='dashboard-consumer',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        print("✓ Connected to Kafka, consuming events...")
        
        event_counts = {'view': 0, 'cart': 0, 'purchase': 0}
        last_update = datetime.now()
        
        for message in consumer:
            event = message.value
            event_type = event.get('event_type')
            
            if event_type in event_counts:
                event_counts[event_type] += 1
            
            # Update every second
            now = datetime.now()
            if (now - last_update).total_seconds() >= 1:
                event_data['view'].append(event_counts['view'])
                event_data['cart'].append(event_counts['cart'])
                event_data['purchase'].append(event_counts['purchase'])
                event_data['timestamps'].append(now.strftime('%H:%M:%S'))
                
                # Reset counts
                event_counts = {'view': 0, 'cart': 0, 'purchase': 0}
                last_update = now
                
    except Exception as e:
        print(f"Kafka consumer error: {e}")

# Start Kafka consumer in background
consumer_thread = threading.Thread(target=kafka_consumer_thread, daemon=True)
consumer_thread.start()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting Dashboard Server")
    print("="*60)
    print("\nAccess dashboard at: http://localhost:8050")
    print("\nPress Ctrl+C to stop\n")
    
    app.run_server(debug=True, host='0.0.0.0', port=8050)
