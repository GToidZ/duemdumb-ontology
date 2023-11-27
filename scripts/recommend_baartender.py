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

    # We can check if the recipe satisfies with inventory by checking number of existing ingredients w/ number of ingredients in recipe (using COUNT())

SELECT ?bartender (?asking AS ?cocktail) WHERE {
	
	{
		SELECT ?asking (COUNT(?ingredient) AS ?requiredIngredients) WHERE {
            ?asking rdf:type :Cocktail;
			    :hasEntry ?e.
			?e :hasIngredient ?ingredient.
		} GROUP BY ?asking
	}

	{
		SELECT ?bartender ?targetBartender ?answering ?inv (COUNT(?equal) AS ?hasIngredients) WHERE {
			?answering rdf:type :Cocktail;
                :hasEntry ?e.
            
            {
                SELECT ?bartender ?targetBartender ?inv ?ing ?equal WHERE {
                    ?bartender rdf:type :Bartender.
                    ?targetBartender rdf:type :Bartender;
                        :hasInventory ?inv.
                    ?e :hasIngredient ?ing.
                    BIND((?bartender = ?targetBartender && ?inv = ?ing) AS ?equal)
                }
			}
                      
            FILTER(?equal = true)
		} GROUP BY ?answering ?bartender
	}
	
    FILTER(?asking = ?answering)
    FILTER(?bartender = ?targetBartender)
	FILTER(?requiredIngredients = ?hasIngredients)
}
""")

table = PrettyTable()
table.field_names = [
    "bartender",
    "cocktail",
]
table.align = "l"

for row in results:
    table.add_row([
        row.bartender,
        row.cocktail,
    ])

print(table.get_string())
with open(outfile, "w+") as f:
    f.write(table.get_html_string())