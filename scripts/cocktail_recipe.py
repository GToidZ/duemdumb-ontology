import os
import sys
import rdflib.graph as g
from pathlib import Path
from prettytable import PrettyTable

name = Path(__file__).stem
directory = os.path.dirname(__file__)
ontology = os.path.abspath(os.path.join(directory, "..", "ontologies", "DuemDumb_V2.1.rdf"))
outfile = os.path.abspath(os.path.join(directory, "..", "out", f"{name}.html"))

graph = g.Graph()
graph.parse(ontology, format='xml')

def cocktail_recipe(cocktail: str) -> str:
    return """
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
        
        FILTER (?c = :%s)
}
    """ % cocktail

if __name__ == "__main__":
    
    table = PrettyTable()
    table.field_names = [
        "Ingredient",
        "Amount",
        "Unit",
    ]
    table.align = "l"
    
    cocktail = "BlackRussian"  # Define your Cocktail individual
    
    try:
        cocktail = sys.argv[1]
    except:
        pass
    
    query_str = cocktail_recipe(cocktail)
    
    for row in graph.query(query_str):
        table.add_row([row.ing.fragment,
                    round(float(row.amount), 2),
                    row.unit.fragment])

    print(table.get_string())
    with open(outfile, "w+") as f:
        f.write(f"<link href='styles.css' rel='stylesheet' /><h1>{cocktail}</h1><br>" + 
        table.get_html_string()
        )