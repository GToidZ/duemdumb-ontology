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

SELECT ?bartender ?inv where{
    ?cocktail rdf:type :Cocktail;
        :hasEntry ?e.
    ?e :hasIngredient ?ing.

    { SELECT ?bartender WHERE{
        ?bartender rdf:type :Bartender
            :hasInventory ?inv
    } 
    }
        
}
	
""")

table = PrettyTable()
table.field_names = [
    "bartender",
    "inv"
]
table.align = "l"

for row in results:
    table.add_row([row.bartender,
                    row.inv])

print(table.get_string())
with open(outfile, "w+") as f:
    f.write(table.get_html_string())