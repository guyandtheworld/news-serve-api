import json
import requests
import xmltodict

from SPARQLWrapper import SPARQLWrapper, JSON


def wiki_search(search_query):
    response = requests.get("https://en.wikipedia.org/w/api.php?action=query&list=search&prop=info&inprop=url&utf8=&format=json&origin=*&srlimit=20&srsearch={}".format(search_query))
    results = json.loads(response.text)
    search_result = results["query"]["search"]
    data = []
    for i in range(0, len(search_result)-1):
        result = {}
        result["title"] = search_result[i]["title"]
        result["summary"] = search_result[i]["snippet"]
        result["url"] = "https://en.wikipedia.org/wiki/{}".format(result["title"])
        data.append(result)
    return data


def dbpedia_search(search_query):
    headers = {"Content-type": "application/json;"}
    response = requests.get("http://lookup.dbpedia.org/api/search/PrefixSearch?QueryString={}".format(search_query), headers=headers)
    result = xmltodict.parse(response.text)
    return result


def lei_search(search_query):
    response = requests.get("https://api.leilex.com/API/LEI/AutoComplete/?query={}&filterType=Name".format(search_query))
    result = json.loads(response.text)
    return result


def get_anchors(entity):
    anchors = {}
    anchors["wiki"] = wiki_search(entity)
    anchors["dbpedia"] = dbpedia_search(entity)
    anchors["lei"] = lei_search(entity)
    return anchors


def get_alias(entity):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    # From https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples#Cats
    query = """SELECT ?alias WHERE { SERVICE wikibase:mwapi { bd:serviceParam wikibase:api \
               "EntitySearch" . bd:serviceParam wikibase:endpoint "www.wikidata.org" . \
               bd:serviceParam mwapi:search "%s" . bd:serviceParam mwapi:language "en" . \
               bd:serviceParam wikibase:limit 1 . ?item wikibase:apiOutputItem mwapi:item . \
               ?num wikibase:apiOrdinal true . } ?item skos:altLabel ?alias }""" % entity

    sparql.setQuery(query)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    aliases = []

    for value in results['results']['bindings']:
        aliases.append(value['alias']['value'])

    aliases = list(set((aliases)))
    return aliases
