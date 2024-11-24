import pandas as pd
import json
import altair as alt 
from shiny import App, render, ui, reactive
from shinywidgets import render_altair, output_widget

# Loading the essential data
top_alerts_map_byhour_sliderrange = pd.read_csv('/Users/zhengcui/Desktop/python 2/student30538/problem_sets/ps6/top_alerts_map_byhour_sliderrange/top_alerts_map_byhour.csv')
top_alerts_map_byhour_sliderrange['type_subtype'] = top_alerts_map_byhour_sliderrange['updated_type'].str.capitalize() + ' - ' + top_alerts_map_byhour_sliderrange['updated_subtype'].str.replace('_', ' ').str.title()
type_subtype_choices = top_alerts_map_byhour_sliderrange['type_subtype'].drop_duplicates().sort_values().tolist()


top_alerts_map_byhour_sliderrange['hour'] = top_alerts_map_byhour_sliderrange['hour'].astype(str)


file_path = "/Users/zhengcui/Desktop/python 2/student30538/problem_sets/ps6/Boundaries - Neighborhoods.geojson"
with open(file_path) as f:
    chicago_geojson = json.load(f)

geo_data = alt.Data(values=chicago_geojson["features"])

#prepare UI,server and diagram
app_ui = ui.page_fluid(
    ui.panel_title("Traffic Alerts Dashboard"),
    ui.input_select(
        "selected_type_subtype",
        "Select Type-Subtype",
        choices=type_subtype_choices,
        selected=type_subtype_choices[0],
    ),
    ui.input_switch("switch_button", "Toggle to switch to range of hours", value=False),
    ui.output_ui("dynamic_slider"),  
    output_widget("traffic_map"),
)

def server(input, output, session):
    @render.ui
    def dynamic_slider():
        if input.switch_button():
            return ui.input_slider(
                "selected_single_hour",
                "Select Single Hour",
                min=0,
                max=23,
                value=12,
                step=1,
            )
        else:
            return ui.input_slider(
                "selected_hour_range",
                "Select Hour Range",
                min=0,
                max=23,
                value=(6, 18),
                step=1,
            )

    @output
    @render_altair
    def traffic_map():
        type_subtype = input.selected_type_subtype()
        if input.switch_button():
            
            selected_hour = f"{input.selected_single_hour():02}:00"

            essential_data = top_alerts_map_byhour_sliderrange[
                (top_alerts_map_byhour_sliderrange["type_subtype"] == type_subtype)
                & (top_alerts_map_byhour_sliderrange["hour"] == selected_hour)
            ]
        else:   
            selected_hour_range = input.selected_hour_range()
            start_hour = f"{selected_hour_range[0]:02}:00"
            end_hour = f"{selected_hour_range[1]:02}:00"

           
            essential_data = top_alerts_map_byhour_sliderrange[
                (top_alerts_map_byhour_sliderrange["type_subtype"] == type_subtype)
                & (top_alerts_map_byhour_sliderrange["hour"] >= start_hour)
                & (top_alerts_map_byhour_sliderrange["hour"] <= end_hour)
            ]
        if essential_data.empty:
            return alt.Chart().mark_text(
                text="No data available for the selected range"
            ).properties(width=600, height=400)

        
        top_10_data = essential_data.nlargest(10, "count")
        return diagram(top_10_data)


def diagram(data):
    geo_map = alt.Chart(alt.Data(geo_data )).mark_geoshape(
        fill="lightgray", stroke="white"
    ).encode(
        tooltip="properties.pri_neigh:N"
    ).properties(
        width=600,
        height=400,
        title="Traffic Alerts Report-Chicago",
    ).project(type="mercator")

    
    scatter_plot = alt.Chart(data).mark_circle(
        stroke="black", strokeWidth=2
    ).encode(
        longitude="longitude:Q",
        latitude="latitude:Q",
        size=alt.Size(
            "count:Q",
            scale=alt.Scale(range=[20, 500]),
            title="Number of Alerts",
        ),
        color=alt.Color(
            "hour:O", scale=alt.Scale(scheme="category10"), title="Hour"
        ),
        tooltip=["longitude", "latitude", "count", "hour"],
    ).properties(
        width=600, height=400
    )

    return geo_map + scatter_plot



app = App(app_ui, server)

