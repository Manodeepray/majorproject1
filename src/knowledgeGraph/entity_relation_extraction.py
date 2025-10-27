
import os

import json

import sys

from pathlib import Path

from kg_gen import KGGen



# Add the project root to the Python path

project_root = Path(__file__).parent.parent.parent

sys.path.append(str(project_root))



def extract_and_store_entities_relations_from_server():

    """

    Extracts entities and relations from processed chunks using kg-gen

    and stores them in JSON files.

    """

    # Define paths

    logs_dir = project_root / "database" / "logs"

    output_dir = project_root / "database" / "entityRelation"

    chunk_status_file = logs_dir / "chunk_status.json"

    

    entities_file = output_dir / "entities.json"

    edges_file = output_dir / "edges.json"

    relations_file = output_dir / "entity_relations.json"



    # Create output directory if it doesn't exist

    output_dir.mkdir(exist_ok=True)






    # Load chunk status

    with open(chunk_status_file, 'r') as f:

        chunk_status = json.load(f)



    # Collect all chunk content

    all_chunks = ""

    for file_info in chunk_status.values():

        for chunk_meta in file_info.get("chunks", []) :

            chunk_path = project_root / chunk_meta["chunk_path"]

            if chunk_path.exists()and  chunk_meta["er_extraction"] == False:

                with open(chunk_path, 'r') as f:

                    all_chunks += f.read()
                chunk_meta["er_extraction"] = True


    # Initialize the Knowledge Graph Generator

    # Make sure to have your Gemini API key set as an environment variable GOOGLE_API_KEY

    kg = KGGen(model="gemini/gemini-2.5-flash",api_key=os.environ["GEMINI_API_KEY"])



    # Generate the knowledge graph from all chunks at once

    if all_chunks:

        try:

            # Since the library might not handle a very large list of texts in one go,

            # let's batch it if necessary. For now, we try with the full list.

            print(f"Processing {len(all_chunks)} chunks...")

            graph = kg.generate(input_data=all_chunks,
                                chunk_size=5000,  # Process text in chunks of 5000 chars
                                cluster=False      # Cluster similar entities and relations
                                )


            current_entities = graph.entities
            current_edges = graph.edges
            current_relations = graph.relations
            
        



        except Exception as e:

            print(f"Error generating knowledge graph: {e}")




    def load_set_from_json(filename):
        """Loads a list from a JSON file and converts it to a set."""
        if not os.path.exists(filename):
            return set()  # Return an empty set if file doesn't exist
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data)
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"⚠️ Warning: Could not decode {filename}. Starting with an empty set.")
            return set()

    def load_relations_from_json(filename):
        """Loads a list of lists from JSON and converts to a set of tuples."""
        if not os.path.exists(filename):
            return set()
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                list_of_lists = json.load(f)
                # Convert each inner list to a tuple to make it hashable for the set
                return {tuple(relation) for relation in list_of_lists}
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"⚠️ Warning: Could not decode {filename}. Starting with an empty set.")
            return set()

    # --- 4. Helper Function for Saving Data ---

    def save_to_json(data, filename):
        """Saves data to a JSON file with pretty-printing (indent=4)."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # indent=4 makes the JSON file human-readable
                json.dump(data, f, indent=4)
            print(f"✅ Successfully saved data to {filename}")
        except Exception as e:
            print(f"❌ Error saving {filename}: {e}")

    # --- 5. Main Load -> Merge -> Save Logic ---

    print("--- Loading Previous Data ---")
    old_entities = load_set_from_json(entities_file)
    old_edges = load_set_from_json(edges_file)
    old_relations = load_relations_from_json(relations_file)

    print(f"Loaded {len(old_entities)} entities, {len(old_edges)} edges, and {len(old_relations)} relations.")


    print("\n--- Merging Data ---")

    # Merge simple sets using the union operator
    all_entities = old_entities.union(current_entities)
    all_edges = old_edges.union(current_edges)
    all_relations = old_relations.union(current_relations)

    print(f"Merged to {len(all_entities)} entities, {len(all_edges)} edges, and {len(all_relations)} relations.")


    print("\n--- Saving Merged Data ---")

    # Convert back to JSON-compatible formats (lists) before saving
    save_to_json(list(all_entities), entities_file)
    save_to_json(list(all_edges), edges_file)
    save_to_json([list(r) for r in all_relations], relations_file)

    print("\nDone.")


def extract_entities_relations_from_context(text:str):

    """

    Extracts entities and relations from retrieved data using kg-gen



    """






    # Initialize the Knowledge Graph Generator

    # Make sure to have your Gemini API key set as an environment variable GOOGLE_API_KEY

    kg = KGGen(model="gemini/gemini-2.5-flash",api_key=os.environ["GEMINI_API_KEY"])



    # Generate the knowledge graph from all chunks at once

    if text:

        try:

            # Since the library might not handle a very large list of texts in one go,

            # let's batch it if necessary. For now, we try with the full list.

            print(f"Processing text chunks...")

            graph = kg.generate(input_data=text)


            current_entities = graph.entities
            current_edges = graph.edges
            current_relations = graph.relations
            
        



        except Exception as e:

            print(f"Error generating knowledge graph: {e}")
        
        return current_entities , current_edges , current_relations 
    
    return None , None , None

if __name__ == "__main__":

    extract_and_store_entities_relations_from_server()


