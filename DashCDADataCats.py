#!/usr/bin/python3

from cdapython import unique_terms
import dash
import dash_bootstrap_components as dbc 
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pprint
import requests

def runAPIQuery(querystring, limit):
    #Using a limit:
    if limit is not None:
        cdaURL = "https://cda.cda-dev.broadinstitute.org/api/v1/sql-query/v3?limit={}".format(str(limit))
    else:
        cdaURL = 'https://cda.cda-dev.broadinstitute.org/api/v1/sql-query/v3'
    headers = {'accept' : 'application/json', 'Content-Type' : 'text/plain'}

    request = requests.post(cdaURL, headers = headers, data = querystring)

    if request.status_code == 200:
        return request.json()
    else:
        raise Exception ("Query failed code {}. {}".format(request.status_code,querystring))

def getDataCategories(testmode):
    if testmode:
        datacatlist = ["Biospecimen", "DNA Methylation", "Raw Mass Spectra"]
        #datacatlist = ["Raw Mass Spectra"]
    else:
        datacatlist = unique_terms("ResearchSubject.Specimen.File.data_category")
    return datacatlist

def checklistData(projectlist):
    checklistdata = []
    for project in projectlist:
        #Python is interpreting None as the python None, not a string and that kills the checkboxlist
        if project is None:
            checklistdata.append({'label' : 'None', 'value': 'None'})
        else:
            checklistdata.append({'label' : project, 'value' : project})
    return checklistdata

def buildDataCategoryQuery(catlist):
    baseq = (
        'SELECT COUNT(DISTINCT _ResearchSubject.id) as idcount,  _File.data_category as datacat, _identifier.system AS repo FROM gdc-bq-sample.cda_mvp.v3, '
        'UNNEST(ResearchSubject) AS _ResearchSubject, UNNEST(_ResearchSubject.Specimen) AS _Specimen, UNNEST(_Specimen.File) AS _File, '
        'UNNEST(_ResearchSubject.identifier) AS _identifier WHERE '
    )
    counter = 1
    for category in catlist:
        if counter > 1:
            baseq = baseq + ' OR '
        baseq = baseq + '( _File.data_category = "{}" )'.format(category)
        counter += 1
    
    baseq = baseq + ' GROUP BY _File.data_category,  _identifier.system'
    return baseq

def nodeParsedQuery(jsondata):
    finaldata = {}
    workingdata = {}
    #will return {system:[{data category: case count}]}
      
    for result in jsondata['result']:
        if result['repo'] not in finaldata.keys():
            finaldata[result['repo']] = [{result['datacat'] : result['idcount']}]
        else:
            finaldata[result['repo']].append({result['datacat'] : result['idcount']})
    return finaldata

def plotlyBarChart(graphdata):
    data = []
    for repo, dataarray in graphdata.items():
        catlist = []
        countlist = []
        for entry in dataarray:
            for datacat,rsid in entry.items():
                catlist.append(datacat)
                countlist.append(rsid)
        data.append({'x': catlist, 'y': countlist, 'type': 'bar', 'name': repo})
    fig = {
        'data' : data, 'layout' : {'title': 'Case Counts by Repository'}
    }
    return fig


########################
#  PROGRAM STARTS HERE #
########################

# Get the datacategories
datacatlist = getDataCategories(False)
datacatchecklist = checklistData(datacatlist)


#Initialize the program
#dashboard = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
dashboard = dash.Dash(external_stylesheets=['https://codepen.io/chriddyp/bWLwgP.css'])


# HTML Layout Section
dashboard.layout = html.Div(
    children = [
        #Title Row
        dbc.Row(html.H1("CDA Dashboard"), justify="center", align="center", className="h-50"),
        #Line break so it looks nicer
        html.Hr(),
        # Second Row for checklist and graph
        dbc.Row(
            children = [
                # First Column
                dbc.Col(
                    children = [
                        html.Span("Select a Datatype"),
                        dcc.Checklist(id = "datacatchecklist", options = datacatchecklist,style = {"display" : "block", 'border': '2px blue solid'})
                    ], width = 1
                ),
                dbc.Col(
                    children = [
                        html.Span("Cases in each selected Data Category"),
                        html.Div(id="graphcontainer"),
                        #xdcc.Graph(id="catbarchart", figure = fig)
                    ], width = 3
                )
            ]
        ),
        #Third row for execute button
        dbc.Row(
            children = [
                html.Button('Update Graph', id = 'graphUpdateButton')
            ]
        )
    ]
)

#################
#   Callbacks   #
#################

@dashboard.callback(
    Output(component_id = 'graphcontainer', component_property = 'children'),
    [Input(component_id = 'graphUpdateButton', component_property= 'n_clicks')],
    [State(component_id='datacatchecklist', component_property='value')]
)
def updateGraph(n_clicks, datacatchecklist):
    if datacatchecklist is not None:
        pprint.pprint(datacatchecklist)
        query = buildDataCategoryQuery(datacatchecklist)
        pprint.pprint(query)
        result = runAPIQuery(query, 1000)
        pprint.pprint(result)
        graphdata = nodeParsedQuery(result)
        pprint.pprint(graphdata)
        fig = plotlyBarChart(graphdata)
        return dcc.Graph(id='barchart', figure = fig)


if __name__ == "__main__":
    dashboard.run_server(debug = True) 
