from typing import List
from pydantic import BaseModel, Field

class ContentIdea(BaseModel):
    topic: str = Field(description="Main topic of the short or video")
    hook: str = Field(description="Hook style like curiosity, shock, controversy, etc")
    quote: str = Field(description="Powerful or viral quote used in the content")
    why: str = Field(description="Why this idea or quote will work")

class ContentIdeasList(BaseModel):
    contentList: List[ContentIdea]

class ShortScript(BaseModel):
    final_short_text: str = Field(
        ...,
        description="Full final narration text for the short"
    )
    phrases: List[str] = Field(
        ...,
        min_length=1,
        description="Sequential phrases split from the final_short_text for timing and subtitle alignment"
    )



class ShortsList(BaseModel):
    shorts: List[ShortScript]