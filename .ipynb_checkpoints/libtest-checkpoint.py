#!/usr/bin/python3
from cdapython import unique_terms
import pprint

def main():
    list = unique_terms("ResearchSubject.associated_project")
    pprint.pprint(list)