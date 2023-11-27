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

            # This query asks for a list of ingredients required for each recipes.

            ?asking rdf:type :Cocktail;
			    :hasEntry ?e.
			?e :hasIngredient ?ingredient.
		} GROUP BY ?asking
	}

	{
		SELECT ?bartender ?targetBartender ?answering ?inv (COUNT(?equal) AS ?hasIngredients) WHERE {

            # This query asks if any bartender has ingredients for each recipes.

			?answering rdf:type :Cocktail;
                :hasEntry ?e.

            {
                SELECT ?bartender ?targetBartender ?inv ?ing ?equal WHERE {
                    
                    # The reason we specify `?bartender` and `?targetBartender` is that,
                    # we can be more sure that the bartender we are checking does not share inventories,
                    # we may be able to use DISTINCT or make more subquries
                    # but this pretty much works.
                    
                    ?bartender rdf:type :Bartender.
                    ?targetBartender rdf:type :Bartender;
                        :hasInventory ?inv.
                    ?e :hasIngredient ?ing.
                    
                    # The `?equal` variable is used to indicate whether a specific bartender has an ingredient.
                    
                    BIND((?bartender = ?targetBartender && ?inv = ?ing) AS ?equal)
                }
			}

            FILTER(?equal = true)
		} GROUP BY ?answering ?bartender
	}

    # We want to filter and satisfy these conditions:
        # The cocktail recipe where the system asks must be identical to one that bartender does.
        # The bartender must be the same person, so inventories are assumed to be not shared.
        # The count of required ingredients is the same as the size of list where bartender has valid ingredients for a recipe.

    FILTER(?asking = ?answering)
    FILTER(?bartender = ?targetBartender)
	FILTER(?requiredIngredients = ?hasIngredients)
} ORDER BY ?bartender
""")

table = PrettyTable()
table.field_names = [
    "Bartender",
    "Cocktail with Ingredients Available",
]
table.align = "l"

for row in results:
    table.add_row([
        row.bartender.fragment,
        row.cocktail.fragment,
    ])

print(table.get_string())
with open(outfile, "w+") as f:
    f.write("<link href='styles.css' rel='stylesheet' />" + table.get_html_string())