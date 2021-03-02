#!/usr/bin/python3

from cdapython import Q, unique_terms
import plotly.graph_objects as go 
import dash
import dash_bootstrap_components as dbc 
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pprint
import pandas as pd

def getProjectList(testmode):
    if testmode:
        projectlist = ["TCGA-UCS"]
    else:
        projectlist = unique_terms("ResearchSubject.associated_project")
    return projectlist

def checklistData(projectlist):
    checklistdata = []
    for project in projectlist:
        #Python is interpreting None as the python None, not a string and that kills the checkboxlist
        if project is None:
            checklistdata.append({'label' : 'None', 'value': 'None'})
        else:
            checklistdata.append({'label' : project, 'value' : project})
    return checklistdata

def getProjectCounts(projectlist):
    #TODO figure out next page functions
    finaldata = {}
    for project in projectlist:
        query = Q('ResearchSubject.Specimen.associated_project = ' + '"' + project + '"')
        result = query.run()

        for subject in result:
            cathash = {}
            for specimen in subject['Specimen']:
                for file in specimen['File']:
                    if file['data_category'] in cathash:
                        cathash[file['data_category']] = cathash[file['data_category']] + 1
                    else:
                        cathash[file['data_category']] = 1
            finaldata[project] = cathash
    return finaldata       


def getDataFrame(finaldata):
    df = pd.DataFrame(finaldata)
    df = df.transpose()  
    return df

def dfPieChart(df):
    fig = go.Figure([go.Pie(labels = df[col_lables], values = df[col_values])])
    return fig

def plotlyPieChart(project, labels, values):
    layout = {'title' : project, 'title_x' : 0.5}
    fig = go.Figure(data = [go.Pie(labels = labels, values = values)], layout = layout)
    fig.update_traces(textinfo = 'value')
    return fig

def listPieChartdata(jsondata):
    typelist = []
    countlist = []
    for datatype, count in jsondata.items():
        typelist.append(datatype)
        countlist.append(count)
    return typelist, countlist

#Program starts below
#Get a list of projects
projectlist = getProjectList(False)
checklistdata = checklistData(projectlist)



#Initialize the program
#dashboard = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
dashboard = dash.Dash(external_stylesheets=['https://codepen.io/chriddyp/bWLwgP.css'])

#Layout
dashboard.layout = html.Div(
    children = [
        #Title Row
        dbc.Row(html.H1("CDA Dashboard"), justify="center", align="center", className="h-50"),
        #Line break
        html.Hr(),
        #Second Row
        dbc.Row(children = [
            #First Column
            dbc.Col(
                children = [
                    html.Span("Select a Project"),
                    dcc.Checklist(id = "projectchecklist", options = checklistdata, style = {"display" : "block", 'border': '2px blue solid'})], width = 1),
            #Graph column
            dbc.Col(
                children = [
                    html.Span("Instances of Data Type") ,
                    html.Div(id = 'container'),
                #    dcc.Graph(id = "projectpiechart", figure = piefig)
                ], width = 3)
        ])
    ])

#Callback section
# https://github.com/plotly/dash-recipes/blob/master/dash-add-graphs-dynamically.py
@dashboard.callback(
    (Output(component_id = 'container', component_property = 'children')),
    (Input(component_id = 'projectchecklist', component_property = 'value'))
)
def updateGraph(project):
    if project:
        graphs = []
        print(project)
        print("Getting Count data")
        countdata = getProjectCounts(project)
        #pprint.pprint(countdata)
        print("Starting graph generation")
        for project in countdata:
            typelist, countlist = listPieChartdata(countdata[project])
            piefig = plotlyPieChart(project, typelist, countlist)
            graphs.append(dcc.Graph(id = project, figure = piefig))
        return html.Div(graphs)


if __name__ == "__main__":
    dashboard.run_server(debug = True)