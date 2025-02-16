from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from typing import Union
from langchain.schema import AIMessage  # Assuming you're using langchain
from langchain.prompts import PromptTemplate
import re
import json
import instructor
import openai

load_dotenv()


from pydantic import BaseModel, Field
from typing import List, Tuple


os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
api_key = os.getenv("GROQ_API_KEY")

base_url = "https://api.groq.com/openai/v1"
# client = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")


system_prompt = """
You are a helper tool for a knowledge graph builder application. Your task is to extract entities and relationships from the text provided by the user, and output a valid JSON object with no additional text.

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

# Initialize the OpenAI client with Instructor
client = instructor.patch(
    openai.OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.environ.get("GROQ_API_KEY"),
    ),
    mode=instructor.Mode.JSON,
)


def extract_knowledge_graph(text: str) -> KnowledgeGraph:
    response = client.chat.completions.create(
        model="Llama3-8b-8192",
        response_model=KnowledgeGraph,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
    )
    return response


# Example usage
text = "Michael Jackson, born in Gary, Indiana, was a famous singer known as the King of Pop. He passed away in Los Angeles in 2009."
result = extract_knowledge_graph(text)
print(result)


def convert_to_chunks(file_path, max_words_per_chunk):
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


# def extract_entities_relationships(text):
#     # The system prompt instructs the model to produce a valid JSON object.
#     # Create a prompt template for the user input.
#     user_prompt_template = PromptTemplate(
#         input_variables=["text"],
#         template="Extract entities and relationship tuples from the following text in valid JSON format:\n\n{text}\n\n",
#     )

#     messages = [
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": user_prompt_template.format(text=text)},
#     ]

#     # Invoke the AI client (client.invoke should return a JSON-formatted string)
#     response = client.invoke(messages)
#     print(response)
#     return extract_json_from_response(response)


# def extract_json_from_response(response):
#     # Ensure response is a string (extract content if it's an AIMessage)
#     if hasattr(response, "content"):
#         response_str = response.content
#     else:
#         response_str = response

#     # Locate and extract the JSON block within backticks
#     # start_index = response_str.find("```")
#     # end_index = response_str.rfind("```")
#     start_index = response_str.find("<JSON>")
#     end_index = response_str.find("</JSON>")  # end_index = response_str.rfind("

#     if start_index != -1 and end_index != -1:
#         # Extract only the content between the backticks
#         json_str = response_str[start_index + 3 : end_index].strip()
#     else:
#         # If no backticks are found, assume the entire response is JSON
#         json_str = response_str.strip()

#     try:
#         # Parse the cleaned JSON string
#         json_response = json.loads(json_str)
#     except json.JSONDecodeError as e:
#         print("Error parsing JSON response:", e)
#         json_response = {}

#     return json_response


# def parse_llm_response_content(content: Union[str, AIMessage]):
#     # If content is an AIMessage, extract the content string
#     if isinstance(content, AIMessage):
#         content = content.content

#     # Extract entities
#     # entities_match = re.search(r"Entities: (\[.*?\])", content, re.DOTALL)
#     # entities_match = re.search(r"Entities:\s*(\[[^\]]*\])", content, re.DOTALL)
#     entities_match = re.search(r"Entities:\s*(\[[\s\S]*?\])", content)

#     entities = eval(entities_match.group(1)) if entities_match else []

#     # Extract relationships
#     relationships_match = re.search(r"Relationships: (\[.*?\])", content, re.DOTALL)
#     relationships = eval(relationships_match.group(1)) if relationships_match else []

#     # Count entities and relationships
#     # nEntities = len(entities)
#     # nRelationships = len(relationships)
#     print(entities, entities)
#     return entities, relationships


def get_entities_relationships1(raw_text):
    result = extract_knowledge_graph(raw_text)
    print(".\n", result)
    entities = result.Entities
    relationships = result.Relationships

    # entities, relationships = parse_llm_response_content(content)
    return entities, relationships


def get_entities_relationships2(file_path, wordsPerChunk):
    """
    Chunk the input text, process each chunk, and combine results.
    """
    chunks = convert_to_chunks(file_path, wordsPerChunk)
    all_entities = []
    all_relationships = []
    i = 1
    print("Number of chunks: ", len(chunks))
    for chunk in chunks:
        # Extract entities and relationships for each chunk
        # content_json = extract_entities_relationships(chunk)
        print("chunk for chunk", i, ".\n", chunk)

        # Extract entities and relationships for each chunk using the new function
        entities, relationships = extract_knowledge_graph(chunk)

        # Print entities and relationships for each chunk
        print(
            "Entities and realtionships have been extracted successfully for chunk ",
            i,
            ".\n",
            entities,
            relationships,
        )

        i = i + 1
        # Aggregate entities and relationships
        all_entities.extend(entities)
        all_relationships.extend(relationships)

    # Remove duplicates from entities
    # all_entities = list(set(all_entities))
    print("All entities and realtionships have been extracted successfully.")
    return all_entities, all_relationships
