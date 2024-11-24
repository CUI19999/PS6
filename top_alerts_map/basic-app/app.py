
from shiny import App, render, ui, reactive
from shinywidgets import render_altair, output_widget
import pandas as pd
import json
import altair as alt 


#load the essential data
top_10_alert_df = pd.read_csv('/Users/zhengcui/Desktop/python 2/student30538/problem_sets/ps6/top_alerts_map/top_alerts_map.csv')

file_path = "/Users/zhengcui/Desktop/python 2/student30538/problem_sets/ps6/Boundaries - Neighborhoods.geojson"
with open(file_path) as f:
    chicago_geojson = json.load(f)

geo_data = alt.Data(values=chicago_geojson["features"])



top_10_alert_df['type_subtype'] = top_10_alert_df['updated_type'].str.capitalize() + ' - ' + \
                                  top_10_alert_df['updated_subtype'].str.replace('_', ' ').str.title()


options = top_10_alert_df['type_subtype'].drop_duplicates().tolist()


#prepare UI,server and diagram
app_ui = ui.page_fluid(
    ui.panel_title("Traffic Alert Dashboard"),
    ui.input_select("selected_option", "Select options", choices=options, selected=options[0]),
    output_widget("traffic_plot")
)


def server(input, output, session):
    @output
    @render_altair
    def traffic_plot():
        selected_option = input.selected_option()
        filtered_data = top_10_alert_df[top_10_alert_df['type_subtype'] == selected_option]

        
        top_10_data = filtered_data.nlargest(10, 'count')

 
        
        
        geo_map = alt.Chart(alt.Data(geo_data)).mark_geoshape(
            fill='lightgray', stroke='white'
        ).encode(
            tooltip='properties.pri_neigh:N'
        ).properties(
            width=600, height=400,
            title='Traffic Alerts Report-Chicago'
        ).project(type='mercator')
        
        
        scatter_plot = alt.Chart(top_10_data).mark_circle(
            fill=None, stroke='red', strokeWidth=2
        ).encode(
            longitude='longitude:Q',
            latitude='latitude:Q',
            size=alt.Size('count:Q', title='Number of Alerts',
                          scale=alt.Scale(domain=[top_10_data['count'].min(), top_10_data['count'].max()]),
                          legend=alt.Legend(title="Traffic Alerts")
            ),
            color=alt.value('red'),
            tooltip=['longitude', 'latitude', 'count']
        ).properties(
            width=600, height=400
        )
        
        
        return geo_map + scatter_plot


app = App(app_ui, server)