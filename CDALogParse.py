#!/usr/bin/python3

import argparse
import requests
import pprint

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

def buildIDQuery(caseid):
    query = (
        'SELECT _ResearchSubject.associated_project, _identifier.system FROM gdc-bq-sample.cda_mvp.v3, UNNEST(ResearchSubject) AS _ResearchSubject, '
        'UNNEST(_ResearchSubject.Specimen) AS _Specimen, UNNEST(_ResearchSubject.identifier) AS _identifier WHERE _Specimen.derived_from_subject = "{}"'.format(caseid)
    )
    return query

def parseResults(results):
    for case in results['result']:
        proj = case['associated_project']
        repo = case['system']
    return proj, repo

def getProject(caseid):
    query = buildIDQuery(caseid)
    result = runAPIQuery(query, None)
    project, repo = parseResults(result)
    return project, repo



def cleanIt(value, delimiter):
    templist = value.split(delimiter)
    return templist[0]

def cleanField(value):
    list 

def main(args):
    fh = open(args.filename, "r")
    headers = "ID\tField\tGDC Value\tPDC Value\tProject\tProject Repo\n"
    ofh = open(args.output, "w")
    ofh.write(headers)
    for line in fh:
        if "INFO" not in line:
            linelist = line.split("\t")
            for entry in linelist:
                entrylist = entry.split(":")
                caseid = cleanIt(entrylist[3], "_")
                caseid = caseid.strip()
                field = cleanIt(entrylist[4], ' ')
                field = field.strip()
                gdcvalue = entrylist[5]
                gdcvalue = gdcvalue.strip()
                pdcvalue = entrylist[6]
                pdcvalue = pdcvalue.strip()
                project, repo = getProject(caseid)
                print(("ID: %s\tField: %s\tGDC: %s\tPDC: %s\tProject: %s\t ProjectRepo: %s\n") % (caseid, field, gdcvalue, pdcvalue, project, repo))
                ofh.write(("%s\t%s\t%s\t%s\t%s\t%s\n") % (caseid, field, gdcvalue, pdcvalue, project, repo))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", required = True, help="CDA Log file name")
    parser.add_argument("-o", "--output", required = True, help = "Output file")

    args = parser.parse_args()
    main(args)
