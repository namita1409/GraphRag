import streamlit as st
from entity_relationship_extraction import get_entities_relationships
from visualize_graph import plot_knowledge_graph

# Streamlit app
st.title("Knowledge Graph Generator from Raw Text")

# Read raw text from an existing file in the same directory
st.write("Reading raw_text file...")
text_file_path = "./data/raw_text.txt"
with open(text_file_path, "r") as file:
    raw_text = file.read()


# Extract entities and relationships from the raw text
with st.spinner("Extracting entities and relationships..."):
    entities, relationships = get_entities_relationships(raw_text)

# Display the extracted entities and relationships
st.write("### Extracted Entities")
st.write(entities)

st.write("### Extracted Relationship Tuples")
st.write(relationships)

# Display the knowledge graph
st.write("### Knowledge Graph")
plot_knowledge_graph(entities, relationships)
