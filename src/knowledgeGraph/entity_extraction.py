
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

    relations_file = output_dir / "relations.json"

    entity_relations_file = output_dir / "entity_relations.json"



    # Create output directory if it doesn't exist

    output_dir.mkdir(exist_ok=True)



    # Load existing data or initialize

    try:

        with open(entities_file, 'r') as f:

            all_entities = set(json.load(f))

    except (FileNotFoundError, json.JSONDecodeError):

        all_entities = set()



    try:

        with open(relations_file, 'r') as f:

            all_relations = set(json.load(f))

    except (FileNotFoundError, json.JSONDecodeError):

        all_relations = set()



    try:

        with open(entity_relations_file, 'r') as f:

            all_entity_relations = json.load(f)

    except (FileNotFoundError, json.JSONDecodeError):

        all_entity_relations = []



    # Load chunk status

    with open(chunk_status_file, 'r') as f:

        chunk_status = json.load(f)



    # Collect all chunk content

    all_chunks = []

    for file_info in chunk_status.values():

        for chunk_meta in file_info.get("chunks", []):

            chunk_path = project_root / chunk_meta["chunk_path"]

            if chunk_path.exists():

                with open(chunk_path, 'r') as f:

                    all_chunks.append(f.read())



    # Initialize the Knowledge Graph Generator

    # Make sure to have your Gemini API key set as an environment variable GOOGLE_API_KEY

    kg = KGGen(model="gemini/gemini-flash")



    # Generate the knowledge graph from all chunks at once

    if all_chunks:

        try:

            # Since the library might not handle a very large list of texts in one go,

            # let's batch it if necessary. For now, we try with the full list.

            print(f"Processing {len(all_chunks)} chunks...")

            graph = kg.generate(input_data=all_chunks)

            

            for source, relationship, target in graph.relations:

                if source and target and relationship:

                    all_entities.add(source)

                    all_entities.add(target)

                    all_relations.add(relationship)

                    

                    new_relation = {"source": source, "target": target, "relationship": relationship}

                    if new_relation not in all_entity_relations:

                        all_entity_relations.append(new_relation)



        except Exception as e:

            print(f"Error generating knowledge graph: {e}")



    # Save the updated data

    print("Saving updated entities and relations...")

    with open(entities_file, 'w') as f:

        json.dump(list(all_entities), f, indent=4)



    with open(relations_file, 'w') as f:

        json.dump(list(all_relations), f, indent=4)



    with open(entity_relations_file, 'w') as f:

        json.dump(all_entity_relations, f, indent=4)

    print("Done.")





if __name__ == "__main__":

    extract_and_store_entities_relations_from_server()


