import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from dash import no_update
import datetime as dt

# Create app

app = dash.Dash(__name__)

app.config.suppress_callback_exceptions = True

df = pd.read_csv('automobile_sales.csv')

df['Month'] = pd.to_datetime(df['Date']).dt.month_name() #used for the names of the months
df['Year'] = pd.to_datetime(df['Date']).dt.year

app.layout = html.Div(children=[
    html.H1('Automobile Sales Statistics', 
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 26}),
    html.Div([
        dcc.Dropdown(id='dropdown-statistics', options=[
            {"label":"Yearly Statistics", "value":"Yearly Statistics"},
            {"label":"Recession Period Statistics", "value":"Recession Period Statistics"},
                        ], placeholder="Yearly Statistics",
                        style={'textAlign': 'center', 'padding': 3,'font-size': 20}),
        dcc.Dropdown(id='select-year', 
                     options=[{'label': i, 'value': i} for i in [i for i in range(1980, 2024, 1)]],
                     placeholder="Select-year",
                     style={'textAlign': 'center', 'padding': 3,'font-size': 20})
        ]),
    html.Div([
        html.Div(id='output-container', className='chart-grid', style={'display': 'flex', "flex-direction": "column"}),
    ])
        #outer division ends
    ])
#layout ends
#Place to add @app.callback Decorator
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value'))

def update_input_container(selected_statistics):
    if selected_statistics =='Yearly Statistics': 
        return False
    else: 
        return True
    
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'), Input(component_id='select-year', component_property='value')])


def update_output_container(selected_statistics, input_year, data: pd.DataFrame = df):
    if selected_statistics == 'Recession Period Statistics':
        # Filter the data for recession periods
        recession_data = data[data['Recession'] == 1]
        #Plot 1 Automobile sales fluctuate over Recession Period (year wise) using line chart
		 # grouping data for plotting
        yearly_rec=recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
		# Plotting the line graph
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec, 
                x='Year',
                y='Automobile_Sales',
                title="Sales by Year in Recession"))

        #Plot 2 Calculate the average number of vehicles sold by vehicle type and represent as a Bar chart
        # use groupby to create relevant data for plotting. 
        #Hint:Use Vehicle_Type and Automobile_Sales columns
        average_sales = recession_data.groupby('Vehicle_Type', as_index=False)['Automobile_Sales'].mean()                 
        R_chart2  = dcc.Graph(
            figure=px.bar(average_sales,
            x='Vehicle_Type',
            y='Automobile_Sales',
            title="Average Sales by Vehicle Type in Recession"))

        # Plot 3 : Pie chart for total expenditure share by vehicle type during recessions
        # grouping data for plotting
        # Hint:Use Vehicle_Type and Advertising_Expenditure columns
        exp_rec= recession_data.groupby('Vehicle_Type', as_index=False)['Advertising_Expenditure'].sum()
        R_chart3 = dcc.Graph(
                figure=px.pie(exp_rec,
                values='Advertising_Expenditure',
                names='Vehicle_Type',
                title="Total Advertising Expenditure by Vehicle Type in Recession"
            )
        )
        # Plot 4 Develop a Bar chart for the effect of unemployment rate on vehicle type and sales
        #grouping data for plotting
	    # Hint:Use unemployment_rate,Vehicle_Type and Automobile_Sales columns
        unemp_data= recession_data.groupby(['Vehicle_Type', 'unemployment_rate'])['Automobile_Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(figure=px.bar(unemp_data,
        x='unemployment_rate',
        y='Automobile_Sales',
		color='Vehicle_Type',
        labels={'unemployment_rate': 'Unemployment Rate', 'Automobile_Sales': 'Average Automobile Sales'},
        title='Effect of Unemployment Rate on Vehicle Type and Sales'))


        return [
            html.Div(className='chart-item', children=[html.Div(children=R_chart1),html.Div(children=R_chart2)],style={'display': 'flex'}),
            html.Div(className='chart-item', children=[html.Div(children=R_chart3),html.Div(children=R_chart4)],style={'display': 'flex'})
            ]
 
    # Yearly Statistic Report Plots 
     # Check for Yearly Statistics.
    elif (input_year and selected_statistics=='Yearly Statistics') :
        yearly_data = data[data['Year'] == input_year]
                              

        # Plot 1 :Yearly Automobile sales using line chart for the whole period.
        # grouping data for plotting.
		# Hint:Use the columns Year and Automobile_Sales.
        yas= data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(figure=px.line(
            yas,
            x='Year',
            y='Automobile_Sales',
            title='Average Sales by Year'))
            
        # Plot 2 :Total Monthly Automobile sales using line chart.

        # grouping data for plotting.
		# Hint:Use the columns Month and Automobile_Sales.
        mas=data.groupby('Month')['Automobile_Sales'].mean().reset_index()
        Y_chart2 = dcc.Graph(figure=px.line(
            mas,
            x='Month',
            y='Automobile_Sales',
            title='Total Monthly Automobile Sales'))


        # Plot bar chart for average number of vehicles sold during the given year
         # grouping data for plotting.
		 # Hint:Use the columns Year and Automobile_Sales
        avr_vdata=yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(figure=px.bar(
            avr_vdata,
            x='Vehicle_Type',
            y='Automobile_Sales',
            title='Average Vehicles Sold by Vehicle Type in the year {}'.format(input_year)))

        # Plot 4 Total Advertisement Expenditure for each vehicle using pie chart
        # grouping data for plotting.
		# Hint:Use the columns Vehicle_Type and Advertising_Expenditure
        exp_data=yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(
            figure=px.pie(exp_data, 
            values='Advertising_Expenditure',
            names='Vehicle_Type',
            title='Total Advertisment Expenditure for Each Vehicle'))
  
    return [
        html.Div(className='chart-item', children=[html.Div(children=Y_chart1),html.Div(children=Y_chart2)],style={'display':'flex'}),
        html.Div(className='chart-item', children=[html.Div(children=Y_chart3),html.Div(children=Y_chart4)],style={'display': 'flex'})
        ]


if __name__ == '__main__':
    app.run()