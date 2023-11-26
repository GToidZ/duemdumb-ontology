import os
import rdflib.graph as g
from pathlib import Path
from prettytable import PrettyTable

name = Path(__file__).stem
directory = os.path.dirname(__file__)
ontology = os.path.abspath(os.path.join(directory, "..", "ontologies", "DuemDumb_V2.1.rdf"))
outfile = os.path.abspath(os.path.join(directory, "..", "out", f"{name}.html"))

graph = g.Graph()
graph.parse(ontology, format='xml')

results = graph.query("""
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <http://www.semanticweb.org/lone_lee/ontologies/2023/10/DuemDumb#>

SELECT ?clab
	(sum(?avol) AS ?alcoholVol)
	(sum(?tvol) AS ?totalVol)
    ((sum(?avol)/sum(?tvol))*100 as ?abv)
    	WHERE {
		?c rdf:type :Cocktail;
		:hasEntry ?e.

		?e :hasIngredient ?ingredient;
			:hasAmount ?amount;
			:useMeasurement ?measurement.

		OPTIONAL {
            ?c rdfs:label ?clab.
		}
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
}
GROUP BY ?clab
""")

table = PrettyTable()
table.field_names = [
    "Cocktail",
    "Alcohol Volume (ml)",
    "Total Fluid Volume (ml)",
    "Alcohol by Volume (%)"
]
table.align = "l"

for row in results:
    table.add_row([row.clab,
                   round(float(row.alcoholVol), 2),
                   round(float(row.totalVol), 2),
                   round(float(row.abv), 2)])

print(table.get_string())
with open(outfile, "w+") as f:
    f.write(table.get_html_string())