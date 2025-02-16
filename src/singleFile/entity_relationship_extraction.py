from openai import OpenAI
import os
import re
import ast
import json
import re
from typing import Union
from langchain.schema import AIMessage  # Assuming you're using langchain

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from largeFile.KnowledgeGraph import KnowledgeGraph

from dotenv import load_dotenv

load_dotenv()
## load the GROQ API Key
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

# llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")

import instructor
import openai

# Initialize the OpenAI client with Instructor
client = instructor.patch(
    openai.OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.environ.get("GROQ_API_KEY"),
    ),
    mode=instructor.Mode.JSON,
)


# def extract_entities_relationships(text):
#     messages = [
#         {
#             "role": "system",
#             "content": """"
#   You are a helper tool for a knowedge graph builder application. Your task is to extract entities and relationships from the text provided by the user.
#   Format the output in such a way that it can be directly parsed into Python lists.
#   I do not want the innner working or code; I just need the output

#   The format should include:

#   1. A list of **Entities** in Python list format.
#   2. A list of **Relationships**, where each relationship is represented as a tuple in the format: (Entity 1, "Relationship", Entity 2).

#   Here is the format to follow:

#   Entities: ["Entity 1", "Entity 2", ..., "Entity N"]

#   Relationships: [("Entity 1", "Relationship", "Entity 2"), ..., ("Entity X", "Relationship", "Entity Y")]

#   Example Input:
#   Extract entities and relationships from the following text:
#   "Michael Jackson, born in Gary, Indiana, was a famous singer known as the King of Pop. He passed away in Los Angeles in 2009."

#   Expected Output:

#   Entities: ["Michael Jackson", "Gary, Indiana", "Los Angeles", "singer", "King of Pop", "2009"]

#   Relationships: [
#       ("Michael Jackson", "born in", "Gary, Indiana"),
#       ("Michael Jackson", "profession", "singer"),
#       ("Michael Jackson", "referred to as", "King of Pop"),
#       ("Michael Jackson", "passed away in", "Los Angeles"),
#       ("Michael Jackson", "date of death", "2009")
#   ]

#    Please make sure that output confirms to the expected output format and please double check the output

#   """,
#         },
#         {
#             "role": "user",
#             "content": f"Extract entities and relationship tuples from the following text:\n\n{text}\n\n",
#         },
#     ]

#     response = llm.invoke(messages)
#     return response


system_prompt = """
You are a helper tool for a knowledge graph builder application. Your task is to extract entities and relationships from the text provided by the user, and output a valid JSON object with no additional text or new line character
I do not want the innner working or code; I just need the output

The JSON should conform to this schema:
{
    "Entities": ["Entity 1", "Entity 2", ...],
    "Relationships": [
        ["Entity 1", "Relationship", "Entity 2"],
        ...
    ]
}

Example Input:
"Michael Jackson, born in Gary, Indiana, was a famous singer known as the King of Pop. He passed away in Los Angeles in 2009."

Expected Output:
{"Entities": ["Michael Jackson", "Gary, Indiana", "Los Angeles", "singer", "King of Pop", "2009"],
 "Relationships": [
     ["Michael Jackson", "born in", "Gary, Indiana"],
     ["Michael Jackson", "profession", "singer"],
     ["Michael Jackson", "referred to as", "King of Pop"],
     ["Michael Jackson", "passed away in", "Los Angeles"],
     ["Michael Jackson", "date of death", "2009"]
 ]}

"""


def extract_knowledge_graph(text: str) -> KnowledgeGraph:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        response_model=KnowledgeGraph,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
    )
    return response


import ast


# def parse_llm_response_content(content):
def parse_llm_response_content(content: Union[str, AIMessage]):
    # If content is an AIMessage, extract the content string
    if isinstance(content, AIMessage):
        content = content.content

    # Split the output into entities and relationships sections
    entity_section = content.split("Entities:")[1].split("Relationships:")[0].strip()
    relationship_section = content.split("Relationships:")[1].strip()

    # Use ast.literal_eval to safely evaluate the string into Python lists
    entities = ast.literal_eval(entity_section)
    relationships = ast.literal_eval(relationship_section)

    return entities, relationships


def get_entities_relationships(raw_text):
    # content = extract_entities_relationships(raw_text)
    result = extract_knowledge_graph(raw_text)
    # entities, relationships = parse_llm_response_content(content)
    entities, relationships = result.Entities, result.Relationships
    return entities, relationships
