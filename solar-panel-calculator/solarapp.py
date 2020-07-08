import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://codepen.io/chriddyp/pen/bWLwgP.css'])
server = app.server

solar_dict = np.load('solar_dict.npy',allow_pickle='TRUE').item()
solar_df = pd.read_csv('solar_df.csv', index_col='State')


app.layout = dbc.Container([
    dbc.Col(html.Div(), width=4),
    dbc.Col(html.Div(
        [
        dbc.Jumbotron(
            [
                html.H1('Solar Calculator'),
                html.Hr(),
                html.P("Calculate your cost to 'GO SOLAR'"
                ),
            ], 
            style={ 
            'background-image': ('linear-gradient(to bottom, rgba(0,0,0,0.6) 0%,rgba(0,0,0,0.6) 100%),' 
                                'url(https://solarworksca.com/wp-content/uploads/2018/01/banner-finance-incentives.jpg)'
            ),
            'background-attachment': 'fixed',
            'background-position': '50% -50%',
            'background-repeat': 'no-repeat',
            'background-size': 'contain',
            'text-align': 'center',
            'color':'white',}
        ),
        
        html.Label('Determine Solar Hours :',
            style={'font-weight':'bold'}
        ),

        dcc.Dropdown(
            id='state_dropdown',
            options=[{'label':k, 'value': k} for k in solar_dict.keys()],
            value='TX'
        ),
        html.Br(),

        dcc.Dropdown(
            id='city_dropdown'
        ),

        html.Br(),

        dcc.Dropdown(
            id='hour_dropdown',
            options=[
                {'label': 'Year Avg.', 'value': 'Year Avg.'},
                {'label': 'Summer Avg.', 'value': 'Summer Avg.'},
                {'label': 'Winter Avg.', 'value': 'Winter Avg.'}
            ],
            value='Year Avg.'
        ),
        html.Br(),
        html.Div(id='display_selected_values'),
        html.Hr(),
        
        html.Label('Electricity Cost ($/kWh) :',
            style={'font-weight':'bold'}
        ),

        dcc.Slider(
            id='kWh_cost_slider',
            min=0,
            max=0.250,
            step=0.001,
            value=0.149
        ),
        html.Div(id='slider_cost_container'),

        html.Hr(),

        html.Label('Average Electricity Usage (kWh/mo.) :',
            style={'font-weight':'bold'}
        ),

        dcc.Slider(
            id='kWh_usage_slider',
            min=0,
            max=3000,
            step=10,
            value=1000
        ),
        html.Div(id='slider_usage_container'),

        html.Hr(),

        html.Label('Home Energy Offset :',
            style={'font-weight':'bold'}
        ),

        dcc.Slider(
            id='energy_offset_slider',
            min=0,
            max=100,
            step=1,
            value=100
        ),
        html.Div(id='slider_offset_container'),

        html.Hr(),

        dcc.Checklist(
            id='fed_tax_credit',
            options=[
                {'label': '   Apply 26% Federal Tax Credit', 'value':'True'}
            ],
            style={'font-weight':'bold'},
            value=['True']
        ),

        html.Hr(),
        html.Label('Select Loan Period :',
            style={'font-weight':'bold'}
        ),

        dcc.Dropdown(
            id='loan_dropdown',
            options=[
                {'label': 'Cash', 'value': 'Cash'},
                {'label': '5 Year 1.99%', 'value': '5 Year 1.99%'},
                {'label': '10 Year 2.99%', 'value': '10 Year 2.99%'},
                {'label': '15 Year 3.99%', 'value': '15 Year 3.99%'},
                {'label': '20 Year 4.99%', 'value': '20 Year 4.99%'},
                {'label': '25 Year 5.49%', 'value': '25 Year 5.49%'},
            ],
            value='Cash'
            ),


        html.Hr(),
        html.Br(),
        dbc.Button('CALCULATE MY COST', id='calculate_cost_button', color='primary', block=True, size='lg'),
        html.Hr(),
        html.Br(),
        html.Div(id='container_cost_button', style={'text-align': 'center'}),
        html.Br(),
        html.Hr(),
        ]
    )),
    dbc.Col(html.Div(), width=4),
])



def solar_hours(selected_hours, selected_state, selected_city):
    return solar_df[(solar_df.index == selected_state) & (solar_df['City'] == selected_city)][selected_hours].item()

def utility_sum(cost, usage, offset, time=25, utility_savings=0):
    for i in range(time):
        utility_savings += cost*((1.02)**i)*(usage*12)*(offset/100)
    return int(utility_savings)


@app.callback(
    Output('city_dropdown', 'options'),
    [Input('state_dropdown', 'value')])
def set_city_options(selected_state):
    return[{'label': i, 'value': i} for i in solar_dict[selected_state]['City']]

@app.callback(
    Output('city_dropdown', 'value'),
    [Input('city_dropdown', 'options')])
def set_city_value(available_options):
    return available_options[0]['value']

@app.callback(
    Output('display_selected_values', 'children'),
    [Input('hour_dropdown', 'value'),
    Input('state_dropdown', 'value'),
    Input('city_dropdown', 'value'),
    ])
def set_display_children(selected_hours, selected_state, selected_city):
    return u'The {} solar hours for {},{} are {}'.format(
        selected_hours,
        selected_city,
        selected_state,
        str(solar_hours(selected_hours, selected_state, selected_city))
    )

@app.callback(
    Output('slider_cost_container', 'children'),
    [Input('kWh_cost_slider', 'value')])
def slider_cost_output(value):
    return '{} $/kWh'.format(value)

@app.callback(
    Output('slider_usage_container', 'children'),
    [Input('kWh_usage_slider', 'value')])
def slider_usage_output(value):
    return '{} kWh/month'.format(value)

@app.callback(
    Output('slider_offset_container', 'children'),
    [Input('energy_offset_slider', 'value')])
def slider_offset_output(value):
    return '{}% home usage offset by solar energy'.format(value)

@app.callback(
    Output('container_cost_button', 'children'),
    [Input('calculate_cost_button', 'n_clicks')],
    [State('hour_dropdown', 'value'),
    State('state_dropdown', 'value'),
    State('city_dropdown', 'value'),
    State('kWh_cost_slider', 'value'),
    State('kWh_usage_slider', 'value'),
    State('energy_offset_slider', 'value'),
    State('fed_tax_credit', 'value'),
    State('loan_dropdown', 'value')
    ])
def system_size_output(n_clicks, selected_hours, selected_state, selected_city, cost, usage, offset, credit, loan):
    
    if n_clicks:
        hours = solar_hours(selected_hours, selected_state, selected_city)
        kW = round((usage*(offset/100))/(hours*30), 2)
        num_panels = int(kW//0.34 + (kW%0.34>0))
        loan_period = 0 if loan=='Cash' else int(loan.split()[0])
        interest_rate = 0 if loan=='Cash' else float(loan.split()[2].replace('%',''))
        r = interest_rate/1200
        cost_low = int(kW*3700*.74) if credit else int(kW*3700)
        cost_high = int(kW*4600*.74) if credit else int(kW*4600)
        interest_low = 0 if loan=='Cash' else int(cost_low*(r*(1+r)**(loan_period*12))/((1+r)**(loan_period*12)-1)*(loan_period*12))-cost_low
        interest_high = 0 if loan=='Cash' else int(cost_high*(r*(1+r)**(loan_period*12))/((1+r)**(loan_period*12)-1)*(loan_period*12))-cost_high
        system_cost_low = cost_low + interest_low
        system_cost_high = cost_high + interest_high

        # Create dataframe to calculate average annual cash flow from solar produced electricity
        df = pd.DataFrame(columns=['year','panel_eff','kWh_daily_per_panel','kWh_price','cash_flow'])
        df['year']=range(26)
        df.set_index('year', inplace=True)
        df['panel_eff']=[0.0000,0.1900,0.1862,0.1850,0.1838,0.1826,0.1814,0.1802,0.1791,
                        0.1779,0.1767,0.1756,0.1744,0.1733,0.1722,0.1711,0.1700,0.1688,
                        0.1678,0.1667,0.1656,0.1645,0.1634,0.1624,0.1613,0.1603
                        ]
        df['kWh_daily_per_panel']=df['panel_eff']*hours*1.7922
        df['kWh_price']=cost*(1.02)**df.index
        df['cash_flow']=num_panels*365*df['kWh_daily_per_panel']*df['kWh_price']
        avg_annual_flow = round(df['cash_flow'][1:26].mean(), 2)
        payback_period_low = int(system_cost_low//avg_annual_flow) + (system_cost_low % avg_annual_flow > 0)
        payback_period_high = int(system_cost_high//avg_annual_flow) + (system_cost_high % avg_annual_flow > 0)
        
        table_header = [
            html.Thead(html.Th(['Your Results :'], colSpan='2',style={'text-align': 'center'}))
        ]

        row1 = html.Tr([html.Td('Estimated System Size :', style={'text-align': 'center'}), html.Td('{} kW'.format(kW))])
        row2 = html.Tr([html.Td('Number of Panels :', style={'text-align': 'center'}), html.Td(num_panels)])
        row3 = html.Tr([html.Td('Estimated Utility Savings* : ', style={'text-align': 'center'}), 
                html.Td('${}'.format(utility_sum(cost, usage, offset)))])
        row4 = html.Tr([html.Td('Estimated System Cost** : ', style={'text-align': 'center'}), 
                html.Td('${} - ${}'.format(system_cost_low, system_cost_high))])
        row5 = html.Tr([html.Td('Estimated Payback Period :', style={'text-align': 'center'}), 
                html.Td('{} - {} years'.format(payback_period_low, payback_period_high))])
        table_body = [html.Tbody([row1, row2, row3, row4, row5])]

        return (dbc.Table(table_header + table_body, bordered=True, striped=True, hover=True, dark=False),
        html.Label('*Over 25 year system warranty'),
        html.Br(),
        html.Label('**National Retailer, credit applied' if credit else '*National Retailer, no credit'))
        
    

if __name__ == '__main__':
    app.run_server(debug=True)