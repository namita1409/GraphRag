import streamlit as st
from archive.entity_relationship_extraction import get_entities_relationships1
from archive.entity_relationship_extraction import get_entities_relationships2
from pydantic import BaseModel, Field
from typing import List, Tuple


from archive.visualize_graph import plot_knowledge_graph

# Streamlit app
st.title("Knowledge Graph Generator from Raw Text")

# Read raw text from an existing file in the same directory
st.write("Reading raw_text file...")
text_file_path_small = "./data/raw_text_small.txt"
text_file_path_large = "./data/raw_text_large.txt"
wordsPerChunk = 2665

# with open(text_file_path_large, "r") as file:
#     raw_text = file.read()

with open(text_file_path_small, "r") as file:
    raw_text = file.read()

# Extract entities and relationships from the raw text
with st.spinner("Extracting entities and relationships..."):
    entities, relationships = get_entities_relationships1(raw_text)
    # entities, relationships = get_entities_relationships2(
    #     text_file_path_large, wordsPerChunk
    # )


# Display the extracted entities and relationships
st.write("### Extracted Entities")
st.write(entities)

st.write("### Extracted Relationship Tuples")
st.write(relationships)

# Display the knowledge graph
st.write("### Knowledge Graph")
plot_knowledge_graph(entities, relationships)
