
from typing import Optional, List, Any, ForwardRef
from pydantic import BaseModel, ConfigDict

# First declare all models to handle forward refs
class UserSchema(BaseModel):
    """Pydantic schema for User"""
    model_config = ConfigDict(from_attributes=True, exclude_defaults=True)
    
    id: int
    
    username: str
    
    email: str

    
    posts: List["PostSchema"] = []


class PostSchema(BaseModel):
    """Pydantic schema for Post"""
    model_config = ConfigDict(from_attributes=True, exclude_defaults=True)
    
    id: int
    
    title: str
    
    content: str
    
    user_id: int

    



# Update forward references
UserSchema.model_rebuild()
PostSchema.model_rebuild()