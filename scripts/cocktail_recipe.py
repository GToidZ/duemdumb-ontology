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

COCKTAIL_NAME = "BlackRussian"  # Define your cocktail individual

results = graph.query("""
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <http://www.semanticweb.org/lone_lee/ontologies/2023/10/DuemDumb#>

SELECT ?ing ?amount ?unit
    WHERE {
		?c rdf:type :Cocktail;
		:hasEntry ?e.

		?e :hasIngredient ?ing;
			:hasAmount ?amount;
			:useMeasurement ?unit.
} VALUES ?c { :%s }
""" % COCKTAIL_NAME)

table = PrettyTable()
table.field_names = [
    "Ingredient",
    "Amount",
    "Unit",
]
table.align = "l"

for row in results:
    table.add_row([row.ing,
                   round(float(row.amount), 2),
                   row.unit])

print(table.get_string())
with open(outfile, "w+") as f:
    f.write(f"<h1>{COCKTAIL_NAME}</h1><br>" + 
    table.get_html_string()
    )