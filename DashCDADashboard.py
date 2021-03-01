#!/usr/bin/python3

from cdapython import Q, unique_terms
import plotly.graph_objects as go 
import dash
import dash_bootstrap_components as dbc 
import dash_html_components as html
import dash_core_components as dcc
import pprint
import pandas as pd

def getProjectList(testmode):
    if testmode:
        projectlist = ["TCGA-UCS"]
    else:
        projectlist = unique_terms("ResearchSubject.associated_project")
    return projectlist

def getProjectCounts(projectlist):
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
    fig.show()

#def listPieChart(jsondata):
#    for project, datahash in jsondata.items():
#        for datatype, count in datahash.items():




def main():
    projectlist = getProjectList(True)
    #pprint.pprint(projectlist)
    finaldata = getProjectCounts(projectlist)
    #pprint.pprint(finaldata)
    df = getDataFrame(finaldata)
    #pprint.pprint(df) 

#

#Initialize the program
dashboard = dash.Dash(external_stylesheets = dbc.themes.BOOTSTRAP)
dashboard.layout = html.Div(
       children = [
           #title row
           dbc.Row(html.H1("CRDC Dashboard"), justify = "center", align = "center", className = "h-50"),
           #Add a break
           html.Hr(),
           #Second Row
           dbc.Row(
               children = [
                   #First column dropdown or checklist
                   dbc.Col(html.Span("Dropdown or checkbox"), width = 3),
                   #Graph is second column
                   dbc.Col(html.Span("Graph here"), width = 9)
                ]
            )
        ]
)

if __name__ == "__main__":
    #main()
    dashboard.run_server()