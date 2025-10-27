#chunls to hkg/kg

from src.knowledgeGraph.entity_relation_extraction import *
from src.knowledgeGraph.knowledge_graph_maker import *


def createDatabaseKnowledgeGraph():
    print("extracting entity and relations...")
    extract_and_store_entities_relations_from_server()
    print("building and saving kg...")
    build_and_save_graph()

def create_knowledge_graph_from_context(text: str):
    """
    Creates a knowledge graph from the given text context and saves it as an HTML file.
    """
    print("Extracting entities and relations from context...")
    entities, _, relations = extract_entities_relations_from_context(text)
    
    if entities and relations:
        print("Building and saving knowledge graph from context...")
        build_and_save_graph_from_data(entities, relations, "assets/context_kg.html")
    else:
        print("No entities or relations extracted from the context. Skipping graph creation.")


if __name__ == "__main__":
    createDatabaseKnowledgeGraph()