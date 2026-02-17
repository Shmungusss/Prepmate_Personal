"""
Prompt templates
"""

# System prompt
GROCERY_LIST_SYSTEM_PROMPT = """You are an expert grocery shopping assistant and meal planner. 

Your role is to:
- Create practical, budget-conscious grocery lists
- Suggest items that work well together for complete meals
- Consider dietary restrictions and preferences
- Provide realistic price estimates
- Organize items by category for efficient shopping

Always think about what meals can be made with the groceries you're selecting."""


# User prompt template
async def create_grocery_list_user_prompt(
    family_size: int = None,
    allergies: list[str] = None,
    budget: float = None,
    dietary_restrictions: list[str] = None,
    cuisine_preferences: list[str] = None,
    goals: list[str] = None,
    meal_types: list[str] = None,

) -> str:
    """Generate user prompt for grocery list creation"""
    
    # Format lists as comma-separated strings
    dietary_str = ", ".join(dietary_restrictions) if dietary_restrictions else "None"
    cuisine_str = ", ".join(cuisine_preferences) if cuisine_preferences else "Any"
    meals_str = ", ".join(meal_types) if meal_types else "All meals (Breakfast, Lunch, Dinner, Snacks, etc"
    goals_str = ", ".join(goals) if goals else "General meal planning"
    allergy_str = ", ".join(allergies) if allergies else "None"
    
    return f"""Create a grocery list with the following preferences:

- Family size: {family_size if family_size else 'Not specified'}
- Budget: ${budget if budget else 'Flexible'}
- Food Allergies: {allergy_str}
- Dietary restrictions: {dietary_str}
- Cuisine preferences: {cuisine_str}
- Meals to plan for: {meals_str}
- Goals: {goals_str}

Focus on items that can be combined into complete, satisfying meals."""


RECIPE_SYSTEM_PROMPT = """You are an expert chef and recipe developer.

Your role is to:
- Create detailed, easy-to-follow recipes
- Use primarily the ingredients provided by the user
- Respect all dietary restrictions strictly
- Provide clear step-by-step cooking instructions with time estimates
- Make recipes practical and achievable for home cooks
- create one recipe

Notes:
- When ingredients contradict diet restrictions and there is no listed alternative, use listed ingredient but in the notes suggest alternative

"""
async def create_recipe_from_ingredients_prompt(
    ingredients: str,
    servings: int,
    cuisine: str = None,
    dietary_restrictions: str = "None",
) -> str:
    """Generate user prompt for recipe creation from ingredients"""

    return f"""Create a recipe using the following:

- Ingredients I have: {ingredients}
- Servings needed: {servings}
- Cuisine type: {cuisine if cuisine else "Any"}
- Dietary restrictions: {dietary_restrictions}

Use primarily the listed ingredients. You may suggest small common pantry 
items (salt, pepper, oil, etc.) that most kitchens have, but keep 
additional ingredients to a minimum."""