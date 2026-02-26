from fastapi import FastAPI,HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from openai import OpenAI
from schemas import *
import prompts
from models import GroceryList, Recipe, saveRecipe
from utils import call_llm, extract_parsed_response
from database import engine, get_db
import db_models
import crud
from datetime import datetime, timezone
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

client = OpenAI()

# Create all database tables
db_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API", version="0.1.0")


# CORS middleware to allow Vue frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vue dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def api_error(code: str, message: str, details: dict | None = None):
    return {"error": {"code": code, "message": message, "details": details or {}}}

# ---------- Validation errors ----------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first = exc.errors()[0] if exc.errors() else {"loc": ["body"], "msg": "Invalid request"}
    field = first.get("loc", ["body"])[-1]
    issue = first.get("msg", "Invalid request data")

    return JSONResponse(
        status_code=400,
        content=api_error(
            "VALIDATION_ERROR",
            "Invalid request data",
            {"field": str(field), "issue": issue},
        ),
    )

# ---------- HTTPException formatter ----------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    status = exc.status_code

    code_map = {
        400: "VALIDATION_ERROR",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_ERROR",
    }
    code = code_map.get(status, "INTERNAL_ERROR")

    return JSONResponse(
        status_code=status,
        content=api_error(code, str(exc.detail), {}),
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=api_error("INTERNAL_ERROR", "Unexpected server error", {}),
    )

@app.get("/")
async def root():
    return {"message": "hello, working"}


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "api",
        "version": "0.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# generate grcoery list from user prefrences 
@app.post("/grocery-lists/generate/from-preferences")
async def generate_list(request: GroceryListRequest, db: Session = Depends(get_db)):
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
    
        List = extract_parsed_response(response.output)

        # Save the list to database
        db_list = crud.save_grocery_list_to_db(db, List)
        
        # Add database ID to response
        result = List.model_dump()

        return result
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected server error")
 

# generate recipe from ingredients 
@app.post("/recipe/generate/from-ingredients")
async def generate_single_recipe(request: RecipeFromIngredients, db: Session = Depends(get_db)):
    try:
        # Create prompt with unpacked arguments
        user_prompt = await prompts.create_recipe_from_ingredients_prompt(
            ingredients=request.ingredients,
            servings=request.servings,
            dietary_restrictions=request.dietary_restrictions,
            cuisine=request.cuisine,
        )
        
        # Call OpenAI API
        response = await call_llm(client, system_prompt=prompts.RECIPE_FROM_INGREDIENTS_SYSTEM_PROMPT, user_prompt=user_prompt, structured_output=Recipe)
    
        recipe = extract_parsed_response(response.output)

        if not recipe:
            raise HTTPException(status_code=500, detail="LLM failed to produce a parsed recipe.")

        
        # Add database ID to response
        result = recipe.model_dump()

        return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recipe: {str(e)}") 

# generate recipe from name 
@app.post("/recipe/generate/from-name")
async def generate_recipe_from_name(request: RecipeFromName, db: Session = Depends(get_db)):
    try:
        # Create prompt with unpacked arguments
        user_prompt = await prompts.create_recipe_from_name_prompt(
            recipe=request.recipe,
            servings=request.servings,
            dietary_restrictions=request.dietary_restrictions,
        )
        
        # Call OpenAI API
        response = await call_llm(client, system_prompt=prompts.RECIPE_FROM_NAME_SYSTEM_PROMPT, user_prompt=user_prompt, structured_output=Recipe)

    
        recipe = extract_parsed_response(response.output)

        if not recipe:
            raise HTTPException(status_code=500, detail="LLM failed to produce a parsed recipe.")
        
        result = recipe.model_dump()

        return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recipe: {str(e)}") 

# generate recipe from text 
@app.post("/recipe/generate/from-text")
async def generate_recipe_from_text(request: RecipeFromText, db: Session = Depends(get_db)):
    try:
        # Create prompt with unpacked arguments
        user_prompt = await prompts.create_recipe_from_text_prompt(
            text=request.text,
        )
        
        # Call OpenAI API
        response = await call_llm(client, system_prompt=prompts.RECIPE_FROM_TEXT_SYSTEM_PROMPT, user_prompt=user_prompt, structured_output=Recipe)

    
        recipe = extract_parsed_response(response.output)

        if not recipe:
            raise HTTPException(status_code=500, detail="LLM failed to produce a parsed recipe.")
        
        result = recipe.model_dump()

        return result
            
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected server error")



# get all recipes 
@app.get("/recipes", response_model=list[saveRecipe])
async def get_all_recipes(db: Session = Depends(get_db)):
    """Get all saved recipes"""
    recipes = crud.get_all_recipes(db)
    return recipes

# get recipe by id 
@app.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Get a single recipe by ID"""
    recipe = crud.get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

# delete recipe by id
@app.delete("/recipes/{recipe_id}")
async def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Delete a recipe"""
    success = crud.delete_recipe(db, recipe_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"message": "Recipe deleted successfully"}


@app.get("/grocery-lists")
async def get_all_grocery_lists(db: Session = Depends(get_db)):
    """Get all saved grocery lists"""
    lists = crud.get_all_grocery_lists(db)
    return lists


@app.get("/grocery-lists/{list_id}")
async def get_grocery_list(list_id: int, db: Session = Depends(get_db)):
    """Get a single grocery list by ID"""
    grocery_list = crud.get_grocery_list_by_id(db, list_id)
    if not grocery_list:
        raise HTTPException(status_code=404, detail="Grocery list not found")
    return grocery_list


@app.delete("/grocery-lists/{list_id}")
async def delete_grocery_list(list_id: int, db: Session = Depends(get_db)):
    """Delete a grocery list"""
    success = crud.delete_grocery_list(db, list_id)
    if not success:
        raise HTTPException(status_code=404, detail="Grocery list not found")
    return {"message": "Grocery list deleted successfully"}

@app.post("/recipes/save", response_model=saveRecipe)
async def save_recipe(recipe: Recipe, db: Session = Depends(get_db)):
    """Manually save a recipe when user clicks 'Save'"""
    
    # Save the recipe to database
    saved = crud.save_recipe_to_db(db, recipe)
    return saved

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)