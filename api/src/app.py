from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from openai import OpenAI
from schemas import *
import prompts
from models import GroceryList, Recipe
from utils import call_llm, extract_parsed_response
client = OpenAI()


app = FastAPI(title="API", version="0.1.0")


# CORS middleware to allow Vue frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vue dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "hello, working"}


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "api",
        "version": "0.1.0"
    }

@app.post("/grocery-lists/generate/from-preferences")
async def generate_list(request: GroceryListRequest):
    try:
        # Create prompt with unpacked arguments
        user_prompt = await prompts.create_grocery_list_user_prompt(
            family_size=request.family_size,
            budget=request.budget,
            dietary_restrictions=request.dietary_restrictions,
            allergies=request.allergies,
            cuisine_preferences=request.cuisine_preferences,
            meal_types=request.meal_types,
            goals=request.goals
        )
        
        # Call OpenAI API
        response = await call_llm(client, system_prompt=prompts.GROCERY_LIST_SYSTEM_PROMPT, user_prompt=user_prompt, structured_output=GroceryList)
    
        List = extract_parsed_response(response)

        # TODO Save the list into DB

        return List.model_dump()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating grocery list: {str(e)}") 


@app.post("/recipe/generate/from-ingredients")
async def generate_single_recipe(request: SingleRecipeRequest):
    try:
        # Create prompt with unpacked arguments
        user_prompt = await prompts.create_recipe_from_ingredients_prompt(
            ingredients=request.ingredients,
            servings=request.servings,
            dietary_restrictions=request.dietary_restrictions,
            cuisine=request.cuisine,
        )
        
        # Call OpenAI API
        response = await call_llm(client, system_prompt=prompts.RECIPE_SYSTEM_PROMPT, user_prompt=user_prompt, structured_output=Recipe)

        # TODO Save the recipe into DB?
    
        recipe = extract_parsed_response(response.output)

        if not recipe:
            raise HTTPException(status_code=500, detail="LLM failed to produce a parsed recipe.")

        print(recipe.model_dump())
        return recipe.model_dump()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recipe: {str(e)}") 




if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)