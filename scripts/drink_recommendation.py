import os
from typing import List
import rdflib.graph as g
from pathlib import Path
from prettytable import PrettyTable

name = Path(__file__).stem
directory = os.path.dirname(__file__)
ontology = os.path.abspath(os.path.join(directory, "..", "ontologies", "DuemDumb_V2.1.rdf"))
outfile = os.path.abspath(os.path.join(directory, "..", "out", f"{name}.html"))

graph = g.Graph()
graph.parse(ontology, format='xml')

def drink_recommendation():
    return """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <http://www.semanticweb.org/lone_lee/ontologies/2023/10/DuemDumb#>

SELECT ?o ?c
WHERE {
    ?o rdf:type :Occasion;
        :standardDrinkThreshold ?trsh.
    
    # Retrieve cocktail and its total volume along with ABV.
    # (Yes, we reused the query from 'Listing Cocktail ABVs.')
    { SELECT ?c
	    (sum(?tvol) AS ?totalVol)
        ((sum(?avol)/sum(?tvol))*100 as ?abv)
    WHERE {
        ?c rdf:type :Cocktail;
            :hasEntry ?e.
        
        ?e :hasIngredient ?ingredient;
			:hasAmount ?amount;
			:useMeasurement ?measurement.

        OPTIONAL {
			?ingredient :hasABV ?abv_temp.
		}
		OPTIONAL {
			?measurement rdf:type :LiquidMeasurement;
				 :milliliterMultiplier ?mm_temp.
		}
		BIND(IF(bound(?mm_temp), ?amount * ?mm_temp, 0) AS ?tvol)
		BIND(IF(bound(?abv_temp), ?abv_temp / 100, 0) AS ?abv)
		
		BIND(IF(?abv > 0, ?abv * ?tvol, 0) AS ?avol)
    } GROUP BY ?c }
    
    BIND((?totalVol * (?abv / 100) * 0.79) / 10 AS ?standardDrink)  # Standard drink equivalence
    
    FILTER(?standardDrink <= ?trsh)  # Filter out drink that are less than or equal threshold.
}
    """

if __name__ == "__main__":
    table = PrettyTable()
    table.field_names = [
        "Occasion",
        "Cocktail",
    ]
    table.align = "l"
    
    query_str = drink_recommendation()
    
    for row in graph.query(query_str):
        table.add_row([
            row.o.fragment,
            row.c.fragment,
        ])
    
    print(table.get_string())
    
    with open(outfile, "w+") as f:
        f.write("<link href='styles.css' rel='stylesheet' />" + table.get_html_string())