import pandas as pd
from rdflib import Graph, URIRef, Literal
from SPARQLWrapper import SPARQLWrapper, JSON

def run_sparql_query(query: str, endpoint: str) -> pd.DataFrame:
    """
    Executes a SPARQL query against a specified endpoint 
    and returns results in a pandas DataFrame.
    """
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    data = process_query_results(results)
    columns = results["head"]["vars"]
    df = pd.DataFrame(data, columns=columns)
    return df

def process_query_results(results: dict) -> list:
    """
    Converts SPARQL JSON results into a list of dictionaries.
    """
    data = []
    for result in results["results"]["bindings"]:
        row = {}
        for var in result:
            row[var] = result[var]["value"]
        data.append(row)
    return data

def convert_to_jsonld(df: pd.DataFrame) -> str:
    """
    Converts the DataFrame SPARQL results into JSON-LD format.
    """
    graph = Graph()
    for _, row in df.iterrows():
        if 'building' in df.columns:
            subject_uri = URIRef(row['building'])
        else:
            subject_uri = Literal(row.iloc[0])

        for col in df.columns:
            predicate_uri = URIRef(f"http://example.org/{col}")
            if str(row[col]).startswith("http"):
                object_val = URIRef(row[col])
            else:
                object_val = Literal(row[col])

            graph.add((subject_uri, predicate_uri, object_val))

    return graph.serialize(format='json-ld', indent=4)
