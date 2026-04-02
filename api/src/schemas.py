from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

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
    cooking_skill: str = "intermediate"  # "beginner" | "intermediate" | "advanced"

class RecipeFromName(BaseModel):
    recipe: str
    dietary_restrictions: Optional[list[str]] = None
    servings: Optional[int] = None
    cooking_skill: str = "intermediate"  # "beginner" | "intermediate" | "advanced"

class RecipeFromText(BaseModel):
    text: str


class PantryItemCreate(BaseModel):
    name: str
    quantity: Optional[str] = ''
    unit: Optional[str] = ''
    location: str = 'pantry'
    category: str = 'Other'
    added_at: Optional[str] = None

class PantryItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[str] = None
    unit: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None

class PantryItemOut(BaseModel):
    id: int
    name: str
    quantity: Optional[str] = ''
    unit: Optional[str] = ''
    location: str
    category: str
    added_at: Optional[str] = None

    class Config:
        from_attributes = True

class PantryBulkCreate(BaseModel):
    items: List[PantryItemCreate]


# ── Ingredient matching ────────────────────────────────

class IngredientInput(BaseModel):
    name: str

class PantryItemInput(BaseModel):
    id: int
    name: str

class IngredientMatchRequest(BaseModel):
    ingredients: List[IngredientInput]
    pantry_items: List[PantryItemInput]

class SingleMatch(BaseModel):
    ingredient_name: str
    pantry_item_id: Optional[int]  # null if no confident match

class IngredientMatchResult(BaseModel):
    matches: List[SingleMatch]


# ── Meal Plan Schemas ──────────────────────────────────

class PantryItemContext(BaseModel):
    name: str
    quantity: Optional[str] = ''
    unit: Optional[str] = ''
    location: Optional[str] = ''
    category: Optional[str] = ''


class PinnedRecipeContext(BaseModel):
    name: str
    meal_type: Optional[str] = None


class PreviousMealContext(BaseModel):
    meal_type: str
    recipe_name: str
    ingredients: List[str]  # ["3 cups flour", "2 eggs", ...]


class PreviousDayContext(BaseModel):
    date: str
    day_of_week: str
    meals: List[PreviousMealContext]


class DayGenerateRequest(BaseModel):
    date: str
    meal_types: List[str]
    servings: int = 2
    goals: List[str] = []
    dietary_restrictions: Optional[str] = None
    cuisine_preferences: List[str] = []
    weekday_cooking_time: str = 'moderate'
    weekend_cooking_time: str = 'moderate'
    pantry_items: List[PantryItemContext] = []
    pinned_recipes: List[PinnedRecipeContext] = []
    previous_days: List[PreviousDayContext] = []
    use_leftovers: bool = False
    pantry_mode: str = "balanced"  # "strict" | "balanced" | "free"
    cooking_skill: str = "intermediate"  # "beginner" | "intermediate" | "advanced"


class PlannedMealCreate(BaseModel):
    date: str
    meal_type: str
    recipe_id: int


class MealPlanCreate(BaseModel):
    name: str
    start_date: str
    end_date: str
    servings: int
    meals: List[PlannedMealCreate]


class MealPlanSummary(BaseModel):
    id: int
    name: str
    start_date: str
    end_date: str
    servings: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PlannedMealOut(BaseModel):
    id: int
    date: str
    meal_type: str
    recipe_id: Optional[int] = None

    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    email: str
    username: str
    password: str
