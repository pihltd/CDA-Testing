#!/usr/bin/python3

from cdapython import unique_terms
import dash
import dash_bootstrap_components as dbc 
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
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
        raise Exception ("Query failed code {}. {}".format(request.status_code,query))

def getDataCategories(testmode):
    if testmode:
        datacatlist = ["Biospecimen", "DNA Methylation"]
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
    baseq = 'SELECT _ResearchSubject.id as RID, _ResearchSubject.associated_project AS RPR, _File.data_category AS FDC, _identifier.system AS SYS FROM gdc-bq-sample.cda_mvp.v3, UNNEST(ResearchSubject) AS _ResearchSubject, UNNEST(_ResearchSubject.Specimen) AS _Specimen, UNNEST(_Specimen.File) AS _File, UNNEST(_ResearchSubject.identifier) AS _identifier WHERE'
    counter = 1
    for category in catlist:
        if counter > 1:
            baseq = baseq + ' OR '
        baseq = baseq + ' _File.data_category = "{}"'.format(category)
        counter += 1
    return baseq

def nodeParsedQuery(jsondata):
    finaldata = {}
    workingdata = {}
    #Will return{system:{data category: [case id]}}
    # FDC = File Data Category
    # RID = ResearchSubject ID
    # RPR - Research project
    # SYS - Repository

    for result in jsondata['result']:
        if result['SYS'] not in workingdata.keys():
            workingdata[result['SYS']] = [{result['FDC']: result['RID']}]
        elif {result['FDC']: result['RID']} not in workingdata['SYS']:
            workingdata['SYS'].append({result['FDC']: result['RID']})
    
    for repo, catlist in workingdata.items():
        temphash = {}
        for datacat, rsid in catlist.items():
            if datacat in temphash.keys():
                temphash[datacat].append(rsid)


########################
#  PROGRAM STARTS HERE #
########################

# Get the datacategories
datacatlist = getDataCategories(True)
datacatchecklist = checklistData(datacatlist)
#baseq = buildDataCategoryQuery(datacatlist)
#pprint.pprint(baseq)
#result = runAPIQuery(baseq, 10)
#pprint.pprint(result)

#Initialize the program
dashboard = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
#dashboard = dash.Dash(external_stylesheets=['https://codepen.io/chriddyp/bWLwgP.css'])


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
                        html.Div(id="graphcontainer")
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


if __name__ == "__main__":
    dashboard.run_server(debug = True) 
