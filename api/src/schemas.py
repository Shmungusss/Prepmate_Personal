from typing import Optional 
from pydantic import BaseModel

class GroceryListRequest(BaseModel):
    dietary_restrictions: Optional[list[str]] = None
    allergies: Optional[list[str]] = None
    budget: Optional[float] = None
    family_size: Optional[int] = None
    cuisine_preferences: Optional[list[str]] = None
    meal_types: Optional[list[str]] = None
    goals: Optional[list[str]] = None


class RecipeFromIngredients(BaseModel):
    ingredients: str
    dietary_restrictions: Optional[list[str]] = None
    servings: Optional[int] = None
    cuisine: Optional[str]= None

class RecipeFromName(BaseModel):
    recipe: str
    dietary_restrictions: Optional[list[str]] = None
    servings: Optional[int] = None

class RecipeFromText(BaseModel):
    text: str

