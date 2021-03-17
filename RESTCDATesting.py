#! /usr/bin/python3

import requests
import pprint
import argparse
from cdapython import unique_terms

def getProjects(testmode, verbose):
    if testmode:
        projectlist = ["TCGA-UCS"]
    else:
        projectlist = unique_terms("ResearchSubject.associated_project")
    return projectlist

def runQuery(querystring, limit, verbose):
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

def countQuery(project):
    querystring = "SELECT count(*) FROM gdc-bq-sample.cda_mvp.v2, UNNEST(ResearchSubject) AS _ResearchSubject WHERE (_ResearchSubject.associated_project = '{}')".format(project)
    return querystring

def samplePerDataCategory(project):
    querystring = "SELECT _Specimen.id, _FILE.data_category FROM gdc-bq-sample.cda_mvp.v3, UNNEST(ResearchSubject) AS _ResearchSubject, UNNEST(_ResearchSubject.Specimen) AS _Specimen, UNNEST(_Specimen.File) AS _File, UNNEST(_File.associated_project) as _project WHERE _project= '{}'".format(project)
    return querystring

def parseSamplePerDataCategory(results, verbose):
    finaldata = {}
    workingdata = {}
    for result in results['result']:
        if result['data_category'] in workingdata.keys():
            if result['id'] not in workingdata[result['data_category']]:
                workingdata[result['data_category']].append(result['id'])
        else:
            workingdata[result['data_category']] = [result['id']]
    if verbose:
        pprint.pprint(workingdata)
    for category, idlist in workingdata.items():
        finaldata[category] = len(idlist)
    return finaldata


def main(args):
    countdata = {}
    projectlist = getProjects(args.testmode, args.verbose)
    if args.testmode:
        limit = None
    else:
        limit = 50000
    
    for project in projectlist:
        querystring = samplePerDataCategory(project)
        result = runQuery(querystring, limit, args.verbose)
        if args.verbose:
            pprint.pprint(result)
        finaldata = parseSamplePerDataCategory(result, args.verbose)
        if args.verbose:
            pprint.pprint(finaldata)
        countdata[project] = finaldata
    if args.verbose:
        pprint.pprint(countdata)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action = "store_true", help = "Enable verbose errors")
    parser.add_argument("-t", "--testmode", action = "store_true", help = "Run in test mode")

    args = parser.parse_args()
    main(args)