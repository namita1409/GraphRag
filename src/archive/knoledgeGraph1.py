import os
import re

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from dotenv import load_dotenv
from typing import Union
from langchain.schema import AIMessage  # Assuming you're using langchain
from langchain.prompts import PromptTemplate

import networkx as nx
import matplotlib.pyplot as plt

load_dotenv()

## load the GROQ API Key
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")


def extract_entities_relationships(text):
    # Define the system prompt as a multi-line string.
    system_prompt = """
You are a helper tool for a knowledge graph builder application. Your task is to extract entities and relationships from the text provided by the user. Format the output in such a way that it can be directly parsed into Python lists.

The format should include:
  - A list of **Entities** in Python list format.
  - A list of **Relationships**, where each relationship is represented as a tuple in the format: (Entity 1, "Relationship", Entity 2).

Here is the format to follow:

Entities: ["Entity 1", "Entity 2", ..., "Entity N"]

Relationships: [("Entity 1", "Relationship", "Entity 2"), ..., ("Entity X", "Relationship", "Entity Y")]

Example Input:
Extract entities and relationships from the following text:
"Michael Jackson, born in Gary, Indiana, was a famous singer known as the King of Pop. He passed away in Los Angeles in 2009."

Expected Output:

Entities: ["Michael Jackson", "Gary, Indiana", "Los Angeles", "singer", "King of Pop", "2009"]

Relationships: [
    ("Michael Jackson", "born in", "Gary, Indiana"),
    ("Michael Jackson", "profession", "singer"),
    ("Michael Jackson", "referred to as", "King of Pop"),
    ("Michael Jackson", "passed away in", "Los Angeles"),
    ("Michael Jackson", "date of death", "2009")
]
"""

    # Create a prompt template for the user input.
    user_prompt_template = PromptTemplate(
        input_variables=["text"],
        template="Extract entities and relationship tuples from the following text:\n\n{text}\n\n",
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_template.format(text=text)},
    ]

    response = llm.invoke(messages)
    return response


def parse_llm_response_content(content: Union[str, AIMessage]):
    # If content is an AIMessage, extract the content string
    if isinstance(content, AIMessage):
        content = content.content

    # Extract entities
    entities_match = re.search(r"Entities: (\[.*?\])", content, re.DOTALL)
    entities = eval(entities_match.group(1)) if entities_match else []

    # Extract relationships
    relationships_match = re.search(r"Relationships: (\[.*?\])", content, re.DOTALL)
    relationships = eval(relationships_match.group(1)) if relationships_match else []

    # Count entities and relationships
    # nEntities = len(entities)
    # nRelationships = len(relationships)

    return entities, relationships


raw_text = "Sarah is an avid traveler who recently visited New York City. During her trip, she saw the Statue of Liberty, which was designed by Frédéric Auguste Bartholdi and completed in 1886. Sarah also visited the Empire State Building, which was completed in 1931 and was designed by Shreve, Lamb & Harmon. Sarah took a memorable photo in front of the Brooklyn Bridge, which was designed by John A. Roebling and completed in 1883. She also visited Central Park, a large public park in New York City."
content = extract_entities_relationships(raw_text)
entities, relationships = parse_llm_response_content(content)
print("\n Entity list (Python):\n ", entities)
print("\n Relationship tuple list (Python):\n", relationships)


def plot_knowledge_graph(entities, relationships):
    G = nx.DiGraph()
    for entity1, relationship, entity2 in relationships:
        G.add_edge(entity1, entity2, label=relationship)

    pos = nx.spring_layout(G)
    plt.figure(figsize=(8, 6))
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="skyblue",
        node_size=5000,
        edge_color="black",
        font_size=10,
    )
    edge_labels = {
        (entity1, entity2): relationship
        for entity1, relationship, entity2 in relationships
    }
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red")

    plt.title("Knowledge Graph")
    plt.show()


plot_knowledge_graph(entities, relationships)
