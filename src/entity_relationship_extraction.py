from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from typing import Union
from langchain.schema import AIMessage  # Assuming you're using langchain
from langchain.prompts import PromptTemplate
import re
import json

load_dotenv()


os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
client = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")


def extract_entities_relationships(text):
    # The system prompt instructs the model to produce a valid JSON object.
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

    # Create a prompt template for the user input.
    user_prompt_template = PromptTemplate(
        input_variables=["text"],
        template="Extract entities and relationship tuples from the following text in valid JSON format:\n\n{text}\n\n",
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_template.format(text=text)},
    ]

    # Invoke the AI client (client.invoke should return a JSON-formatted string)
    response = client.invoke(messages)
    print(response)
    return extract_json_from_response(response)


def extract_json_from_response(response):
    # Ensure response is a string (extract content if it's an AIMessage)
    if hasattr(response, "content"):
        response_str = response.content
    else:
        response_str = response

    # Locate and extract the JSON block within backticks
    start_index = response_str.find("```")
    end_index = response_str.rfind("```")

    if start_index != -1 and end_index != -1:
        # Extract only the content between the backticks
        json_str = response_str[start_index + 3 : end_index].strip()
    else:
        # If no backticks are found, assume the entire response is JSON
        json_str = response_str.strip()

    try:
        # Parse the cleaned JSON string
        json_response = json.loads(json_str)
    except json.JSONDecodeError as e:
        print("Error parsing JSON response:", e)
        json_response = {}

    return json_response


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


def get_entities_relationships(raw_text):
    content_json = extract_entities_relationships(raw_text)

    print(content_json)
    entities = content_json["Entities"]
    relationships = content_json["Relationships"]

    # entities, relationships = parse_llm_response_content(content)
    return entities, relationships
