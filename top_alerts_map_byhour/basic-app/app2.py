import pandas as pd
import json
import altair as alt 
from shiny import App, render, ui, reactive
from shinywidgets import render_altair, output_widget



# Loading the essential data
top_alerts_map_byhour = pd.read_csv('/Users/zhengcui/Desktop/python 2/student30538/problem_sets/ps6/top_alerts_map_byhour/top_alerts_map_byhour.csv') 
top_alerts_map_byhour['type_subtype'] = top_alerts_map_byhour['updated_type'].str.capitalize() + ' - ' + top_alerts_map_byhour['updated_subtype'].str.replace('_', ' ').str.title()
type_subtype_choices = top_alerts_map_byhour['type_subtype'].drop_duplicates().sort_values().tolist()



file_path = "/Users/zhengcui/Desktop/python 2/student30538/problem_sets/ps6/Boundaries - Neighborhoods.geojson"
with open(file_path) as f:
    chicago_geojson = json.load(f)

geo_data = alt.Data(values=chicago_geojson["features"])



#prepare UI,server and diagram
app_ui = ui.page_fluid(
    ui.panel_title("Traffic Alert Dashboard"),
    ui.input_select("selected_type_subtype", "Select Type-Subtype", choices=type_subtype_choices, selected=type_subtype_choices[0]),
    ui.input_slider("selected_hour", "Select Hour", min=0, max=23, value=12, step=1),
    output_widget("traffic_map")
)

def server(input, output, session):
    @output
    @render_altair
    def traffic_map():
        
        selected_hour = f"{input.selected_hour():02}:00"  

        
        essential_data = top_alerts_map_byhour[
            (top_alerts_map_byhour['type_subtype'] == input.selected_type_subtype()) &
            (top_alerts_map_byhour['hour'] == selected_hour)
        ]
        if essential_data.empty:
            return alt.Chart().mark_text(text="No data available").properties(width=600, height=400)
        
        top10_data = essential_data.nlargest(10, 'count')

        
        return diagram(top10_data)

def diagram(data):
   
    unique_number = sorted(data['count'].unique())

    geo_map = alt.Chart(alt.Data(geo_data)).mark_geoshape(
        fill='lightgray', stroke='white'
    ).encode(
        tooltip='properties.pri_neigh:N'
    ).properties(
        width=600, height=400,
        title='Traffic Alerts Report-Chicago'
    ).project(type='mercator')

    scatter_plot = alt.Chart(data).mark_circle(
        stroke='black', strokeWidth=1,fill='red'
    ).encode(
        longitude='longitude:Q',
        latitude='latitude:Q',
        size=alt.Size('count:Q', title='Number of Alerts',
                      scale=alt.Scale(domain=[min(unique_number), max(unique_number)], range=[20, 500], clamp=True),
                      legend=alt.Legend(title="Number of Alerts", values=unique_number)), 
        tooltip=[alt.Tooltip('longitude', title='Longitude'),
                 alt.Tooltip('latitude', title='Latitude'),
                 alt.Tooltip('count', title='Number of Alerts', format=".0f")]
    ).properties(
        width=600, height=400
    )

    return geo_map + scatter_plot




app = App(app_ui, server)