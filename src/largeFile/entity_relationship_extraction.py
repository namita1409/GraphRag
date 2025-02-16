from openai import OpenAI
import os
import re
import ast
import json
import re
from typing import Union
from langchain.schema import AIMessage  # Assuming you're using langchain
from concurrent.futures import ThreadPoolExecutor

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
You are a helper tool for a knowledge graph builder application. Your task is to extract entities and relationships from the text provided by the user and output a valid JSON object with no additional text or new line characters.

Your task is to output a single valid JSON object that adheres strictly to below schema

The JSON must strictly conform to this schema:
{
    "Entities": ["Entity 1", "Entity 2", ...],
    "Relationships": [
        ["Entity 1", "Relationship", "Entity 2"],
    ]
}

Rules:
1. Ensure all relationships are strictly in the format ["Entity1", "Relationship", "Entity2"].
2. Do not include duplicate entities or relationships.
3. Do not include null, empty, or invalid values.
4. Ensure proper escaping of special characters (e.g., quotes, commas).
5. Do not include any additional text outside of the JSON object.
6. Output only the JSON object and nothing else.


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

from time import sleep


def extract_knowledge_graph(text: str) -> KnowledgeGraph:
    sleep(1)
    response = client.chat.completions.create(
        # model="llama-3.1-8b-instant",
        # model="mixtral-8x7b-32768",
        model="deepseek-r1-distill-qwen-32b",
        response_model=KnowledgeGraph,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
    )
    return response


def extract_knowledge_graph_with_retry(text: str, retries=3):
    for attempt in range(retries):
        try:
            return extract_knowledge_graph(text)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2**attempt)  # Exponential backoff
            continue
    raise Exception("Failed to extract knowledge graph after multiple attempts")


import ast


# def parse_llm_response_content(content):
# def parse_llm_response_content(content: Union[str, AIMessage]):
#     # If content is an AIMessage, extract the content string
#     if isinstance(content, AIMessage):
#         content = content.content

#     # Split the output into entities and relationships sections
#     entity_section = content.split("Entities:")[1].split("Relationships:")[0].strip()
#     relationship_section = content.split("Relationships:")[1].strip()

#     # Use ast.literal_eval to safely evaluate the string into Python lists
#     entities = ast.literal_eval(entity_section)
#     relationships = ast.literal_eval(relationship_section)
#     print(entities, relationship_section)
#     return entities, relationships


# def get_entities_relationships(file_path, wordsPerChunk=2665):
#     chunks = convert_to_chunks(file_path, wordsPerChunk)
#     all_entities = []
#     all_relationships = []
#     i = 1
#     print("Number of chunks: ", len(chunks))
#     for chunk in chunks:
#         # Extract entities and relationships for each chunk by calling llm
#         content = extract_entities_relationships(chunk)
#         print(
#             "Entities and realtionships have been extracted successfully for chunk ",
#             i,
#             ".\n",
#         )
#         entities, relationships = parse_llm_response_content(content)
#         print(
#             "Entities and realtionships have been parsed successfully for chunk ",
#             i,
#             ".\n",
#         )
#         i = i + 1
#         # Aggregate entities and relationships
#         all_entities.extend(entities)
#         all_relationships.extend(relationships)

#     # Remove duplicates from entities
#     all_entities = list(set(all_entities))
#     # all_relationships = list(set(all_relationships))

#     print(
#         "All entities and realtionships have been extracted successfully.", all_entities
#     )

#     return all_entities, all_relationships

import time


def process_chunk(chunk, chunk_index):
    # Extract entities and relationships for the chunk
    # content = extract_entities_relationships(chunk)
    result = extract_knowledge_graph_with_retry(chunk)
    print(
        f"Entities and relationships have been extracted successfully for chunk {chunk_index}."
    )

    # Parse the llm response content concurrently
    # entities, relationships = parse_llm_response_content(content)
    entities, relationships = result.Entities, result.Relationships
    print(
        f"Entities and relationships have been parsed successfully for chunk {chunk_index}."
    )
    return entities, relationships


def get_entities_relationships(file_path, wordsPerChunk=2665):
    # Split the file into chunks
    chunks = convert_to_chunks(file_path, wordsPerChunk)
    all_entities = []
    all_relationships = []

    print("Number of chunks:", len(chunks))
    max_workers = 3
    # Process each chunk concurrently using ThreadPoolExecutor
    # with ThreadPoolExecutor() as executor:
    #     # executor.map passes each chunk along with its index (starting at 1)
    #     results = list(executor.map(process_chunk, chunks, range(1, len(chunks) + 1)))

    results = []
    delay_seconds = 1
    batch_size = 1

    with ThreadPoolExecutor(max_workers=2) as executor:
        # Process chunks in batches
        for i in range(0, len(chunks), batch_size):
            # Slice the current batch of chunks
            batch_chunks = chunks[i : i + batch_size]
            # Create an index range for the current batch
            batch_indices = range(i + 1, i + len(batch_chunks) + 1)
            # Submit batch tasks concurrently, with at most 2 threads running
            batch_results = list(
                executor.map(process_chunk, batch_chunks, batch_indices)
            )
            results.extend(batch_results)
            # Pause between batches
            time.sleep(delay_seconds)

    # Aggregate results from all threads
    for entities, relationships in results:
        all_entities.extend(entities)
        all_relationships.extend(relationships)

    # Remove duplicate entities if required
    all_entities = list(set(all_entities))

    print(
        "All entities and relationships have been extracted successfully.", all_entities
    )
    return all_entities, all_relationships


def convert_to_chunks(file_path, max_words_per_chunk):

    print("file path: ", file_path)
    chunks = []
    current_chunk = []
    current_word_count = 0

    with open(file_path, "r") as file:
        for line in file:
            words = line.split()
            current_word_count += len(words)
            if current_word_count < max_words_per_chunk:
                current_chunk.append(line.strip())
            else:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_word_count = 0
                current_word_count += len(words)
                current_chunk.append(line.strip())

        # Add any remaining text in the last chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        print("\nChunks created.\n")
        return chunks
