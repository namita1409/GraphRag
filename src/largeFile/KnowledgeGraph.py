from pydantic import BaseModel, Field
from typing import List, Tuple


class KnowledgeGraph(BaseModel):
    Entities: List[str] = Field(description="List of entities extracted from the text")
    Relationships: List[Tuple[str, str, str]] = Field(
        description="List of relationship tuples [Entity1, Relationship, Entity2]"
    )
