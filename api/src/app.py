from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Body, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import uvicorn
from openai import OpenAI
from schemas import *
import schemas
import prompts
from models import GroceryList, Recipe, saveRecipe, ReceiptScanResult, DayPlanOutput, MealPlanEntry
from utils import call_llm, call_vision_llm, extract_parsed_response
from database import engine, get_db
import db_models
import crud
from datetime import datetime, timezone
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import base64
import re
import json
import requests as http_requests
import utils
from typing import Any

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

# generate recipe from social media link
@app.post("/recipe/generate/from-link")
async def create_recipe_from_link(
    body: dict = Body(...),
    db: Session = Depends(get_db)
):
    """Accepts a social media link, uses AI to extract and generate a recipe."""
    url = body.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url' in request body")
    try:
        # Placeholder: Replace with actual AI extraction logic as needed
        # For now, just return a dummy recipe structure
        # result = await utils.recipe_from_link(url)
        result = {
            "title": "Extracted Recipe from Link",
            "ingredients": ["ingredient 1", "ingredient 2"],
            "steps": ["Step 1", "Step 2"],
            "tips": ["Tip 1"]
        }
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recipe extraction from link failed: {str(e)}")

# generate grocery list from user preferences
@app.post("/grocery-lists/generate/from-preferences")
async def generate_list(request: GroceryListRequest, db: Session = Depends(get_db), x_user_id: int | None = Header(None, alias="X-User-Id")):
    try:
        user_prompt = await prompts.create_grocery_list_user_prompt(
            family_size=request.family_size,
            budget=request.budget,
            dietary_restrictions=request.dietary_restrictions,
            allergies=request.allergies,
            cuisine_preferences=request.cuisine_preferences,
            meal_types=request.meal_types,
            goals=request.goals
        )

        response = await call_llm(client, system_prompt=prompts.GROCERY_LIST_SYSTEM_PROMPT, user_prompt=user_prompt, structured_output=GroceryList)

        List = extract_parsed_response(response.output)

        db_list = crud.save_grocery_list_to_db(db, List, user_id=x_user_id)

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
        user_prompt = await prompts.create_recipe_from_ingredients_prompt(
            ingredients=request.ingredients,
            servings=request.servings,
            dietary_restrictions=request.dietary_restrictions,
            cuisine=request.cuisine,
            cooking_skill=request.cooking_skill,
        )

        response = await call_llm(client, system_prompt=prompts.RECIPE_FROM_INGREDIENTS_SYSTEM_PROMPT, user_prompt=user_prompt, structured_output=Recipe)

        recipe = extract_parsed_response(response.output)

        if not recipe:
            raise HTTPException(status_code=500, detail="LLM failed to produce a parsed recipe.")

        result = recipe.model_dump()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recipe: {str(e)}")

# generate recipe from name
@app.post("/recipe/generate/from-name")
async def generate_recipe_from_name(request: RecipeFromName, db: Session = Depends(get_db)):
    try:
        user_prompt = await prompts.create_recipe_from_name_prompt(
            recipe=request.recipe,
            servings=request.servings,
            dietary_restrictions=request.dietary_restrictions,
            cooking_skill=request.cooking_skill,
        )

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
        user_prompt = await prompts.create_recipe_from_text_prompt(
            text=request.text,
        )

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


# generate recipe from image
@app.post("/api/recipes/from-image")
async def create_recipe_from_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Accepts an image upload, uses AI vision to extract food or recipe text, and generates a recipe."""
    try:
        image_bytes = await file.read()
        result: dict[str, Any] = await utils.recipe_from_image(image_bytes)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image recognition failed: {str(e)}")


# get all recipes
@app.get("/recipes", response_model=list[saveRecipe])
async def get_all_recipes(db: Session = Depends(get_db), x_user_id: int | None = Header(None, alias="X-User-Id")):
    """Get all saved recipes"""
    recipes = crud.get_all_recipes(db, user_id=x_user_id)
    return recipes

# get recipe by id
@app.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Get a single recipe by ID"""
    recipe = crud.get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

# save a meal-plan recipe to the user's collection
@app.post("/recipes/{recipe_id}/save-to-collection")
async def save_recipe_to_collection(recipe_id: int, db: Session = Depends(get_db), x_user_id: int | None = Header(None, alias="X-User-Id")):
    """Promote a meal-plan recipe into the user's saved recipe collection"""
    recipe = crud.promote_recipe_to_collection(db, recipe_id)
    # If the recipe has no owner and we have a user id, assign it
    if recipe and getattr(recipe, "user_id", None) is None and x_user_id is not None:
        recipe.user_id = x_user_id
        db.commit()
        db.refresh(recipe)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return saveRecipe.model_validate(recipe).model_dump()

# delete recipe by id
@app.delete("/recipes/{recipe_id}")
async def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Delete a recipe"""
    success = crud.delete_recipe(db, recipe_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"message": "Recipe deleted successfully"}


@app.post("/grocery-lists", status_code=201)
async def create_grocery_list(grocery_list: GroceryList, db: Session = Depends(get_db), x_user_id: int | None = Header(None, alias="X-User-Id")):
    """Create a new grocery list and persist it to the database"""
    saved = crud.save_grocery_list_to_db(db, grocery_list, user_id=x_user_id)
    return {
        "id": saved.id,
        "title": saved.title,
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "quantity": item.quantity,
                "unit": item.unit,
                "category": item.category,
                "estimated_price": item.estimated_price,
                "notes": item.notes,
            }
            for item in saved.items
        ],
        "total_estimated_cost": saved.total_estimated_cost,
        "dietary_preferences": json.loads(saved.dietary_preferences) if saved.dietary_preferences else None,
        "serves": saved.serves,
        "notes": saved.notes,
        "created_at": saved.created_at.isoformat() if saved.created_at else None,
    }


@app.put("/grocery-lists/{list_id}")
async def edit_grocery_list(list_id: int, grocery_list: GroceryList, db: Session = Depends(get_db), x_user_id: int | None = Header(None, alias="X-User-Id")):
    """Update an existing grocery list"""
    saved = crud.update_grocery_list(db, list_id, grocery_list, user_id=x_user_id)
    if not saved:
        raise HTTPException(status_code=404, detail="Grocery list not found")
    return {
        "id": saved.id,
        "title": saved.title,
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "quantity": item.quantity,
                "unit": item.unit,
                "category": item.category,
                "estimated_price": item.estimated_price,
                "notes": item.notes,
            }
            for item in saved.items
        ],
        "total_estimated_cost": saved.total_estimated_cost,
        "dietary_preferences": json.loads(saved.dietary_preferences) if saved.dietary_preferences else None,
        "serves": saved.serves,
        "notes": saved.notes,
        "created_at": saved.created_at.isoformat() if saved.created_at else None,
    }


@app.get("/grocery-lists")
async def get_all_grocery_lists(db: Session = Depends(get_db), x_user_id: int | None = Header(None, alias="X-User-Id")):
    """Get all saved grocery lists"""
    lists = crud.get_all_grocery_lists(db, user_id=x_user_id)
    return lists


@app.get("/grocery-lists/{list_id}")
async def get_grocery_list(list_id: int, db: Session = Depends(get_db), x_user_id: int | None = Header(None, alias="X-User-Id")):
    """Get a single grocery list by ID"""
    grocery_list = crud.get_grocery_list_by_id(db, list_id, user_id=x_user_id)
    if not grocery_list:
        raise HTTPException(status_code=404, detail="Grocery list not found")
    return grocery_list


@app.delete("/grocery-lists/{list_id}")
async def delete_grocery_list(list_id: int, db: Session = Depends(get_db), x_user_id: int | None = Header(None, alias="X-User-Id")):
    """Delete a grocery list"""
    grocery_list = crud.get_grocery_list_by_id(db, list_id, user_id=x_user_id)
    if not grocery_list:
        raise HTTPException(status_code=404, detail="Grocery list not found")
    success = crud.delete_grocery_list(db, list_id)
    if not success:
        raise HTTPException(status_code=404, detail="Grocery list not found")
    return {"message": "Grocery list deleted successfully"}

@app.post("/recipes/save", response_model=saveRecipe)
async def save_recipe(recipe: Recipe, db: Session = Depends(get_db), x_user_id: int | None = Header(None, alias="X-User-Id")):
    """Manually save a recipe when user clicks 'Save'"""
    saved = crud.save_recipe_to_db(db, recipe, user_id=x_user_id)
    return saved


# ── User endpoints ─────────────────────────────────────

@app.post("/users/register")
async def register_user(request: UserCreateRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        existing_user = db.query(db_models.DBUser).filter(
            (db_models.DBUser.email == request.email) |
            (db_models.DBUser.username == request.username)
        ).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email or username already exists")

        # NOTE: Password should be hashed with bcrypt in production!
        db_user = db_models.DBUser(
            email=request.email,
            username=request.username,
            hashed_password=request.password,  # TODO: Hash this!
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return {
            "id": db_user.id,
            "email": db_user.email,
            "username": db_user.username,
            "created_at": db_user.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(db_models.DBUser).filter(db_models.DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "created_at": user.created_at.isoformat()
    }


@app.get("/users")
async def get_all_users(db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(db_models.DBUser).all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "created_at": user.created_at.isoformat()
        }
        for user in users
    ]


# ── Pantry endpoints ──────────────────────────────────
@app.get("/pantry/items", response_model=list[schemas.PantryItemOut])
def get_pantry_items(db: Session = Depends(get_db), x_user_id: int | None = Header(None, alias="X-User-Id")):
    return crud.get_all_pantry_items(db, user_id=x_user_id)

@app.post("/pantry/items", response_model=schemas.PantryItemOut, status_code=201)
def create_pantry_item(item: schemas.PantryItemCreate, db: Session = Depends(get_db), x_user_id: int | None = Header(None, alias="X-User-Id")):
    return crud.create_pantry_item(db, item, user_id=x_user_id)

@app.post("/pantry/items/bulk", response_model=list[schemas.PantryItemOut], status_code=201)
def bulk_create_pantry_items(body: schemas.PantryBulkCreate, db: Session = Depends(get_db), x_user_id: int | None = Header(None, alias="X-User-Id")):
    return crud.bulk_create_pantry_items(db, body.items, user_id=x_user_id)

@app.put("/pantry/items/{item_id}", response_model=schemas.PantryItemOut)
def update_pantry_item(item_id: int, patch: schemas.PantryItemUpdate, db: Session = Depends(get_db)):
    item = crud.update_pantry_item(db, item_id, patch)
    if not item:
        raise HTTPException(status_code=404, detail="Pantry item not found")
    return item

@app.delete("/pantry/items/{item_id}")
def delete_pantry_item(item_id: int, db: Session = Depends(get_db)):
    if not crud.delete_pantry_item(db, item_id):
        raise HTTPException(status_code=404, detail="Pantry item not found")
    return {"message": "Deleted"}


def _map_off_category(tags: list) -> str:
    joined = ' '.join(tags).lower()
    if any(x in joined for x in ['meat', 'beef', 'pork', 'poultry', 'chicken', 'turkey', 'seafood', 'fish', 'shrimp', 'salmon', 'tuna']):
        return 'Meat & Seafood'
    if any(x in joined for x in ['dairy', 'milk', 'cheese', 'yogurt', 'butter', 'cream', 'egg']):
        return 'Dairy & Eggs'
    if any(x in joined for x in ['vegetable', 'fruit', 'produce', 'fresh-fruit', 'fresh-vegetable']):
        return 'Produce'
    if any(x in joined for x in ['bread', 'cereal', 'pasta', 'rice', 'grain', 'flour', 'oat', 'tortilla', 'cracker']):
        return 'Grains & Bread'
    if any(x in joined for x in ['beverage', 'drink', 'juice', 'water', 'soda', 'coffee', 'tea', 'broth', 'stock']):
        return 'Beverages'
    if any(x in joined for x in ['spice', 'herb', 'seasoning', 'condiment', 'sauce', 'oil', 'vinegar', 'sugar', 'salt']):
        return 'Pantry Staples'
    return 'Other'


def _parse_off_quantity(qty_str: str):
    if not qty_str:
        return None, None
    match = re.match(r'(\d+(?:\.\d+)?)\s*([a-zA-Z\s]+)', qty_str.strip())
    if match:
        qty = float(match.group(1))
        unit = match.group(2).strip().split('(')[0].strip()
        return qty, unit
    return None, None


@app.get("/pantry/barcode/{upc}")
def lookup_barcode(upc: str):
    """Look up a product by UPC barcode using the Open Food Facts database"""
    try:
        resp = http_requests.get(
            f"https://world.openfoodfacts.org/api/v0/product/{upc}.json",
            headers={"User-Agent": "PrepMate/1.0"},
            timeout=8,
        )
        data = resp.json()

        if data.get("status") != 1 or not data.get("product"):
            raise HTTPException(status_code=404, detail="Product not found")

        product = data["product"]

        name = (
            product.get("product_name_en")
            or product.get("product_name")
            or ""
        ).strip()

        if not name:
            raise HTTPException(status_code=404, detail="Product not found")

        brand = (product.get("brands") or "").split(",")[0].strip()
        category = _map_off_category(product.get("categories_tags") or [])
        qty, unit = _parse_off_quantity(product.get("quantity") or "")

        return {
            "name": name,
            "brand": brand,
            "category": category,
            "quantity": qty,
            "unit": unit or "",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Barcode lookup failed: {str(e)}")


@app.post("/pantry/scan-receipt")
async def scan_receipt(file: UploadFile = File(...)):
    """Scan a grocery receipt image and extract food items using vision AI"""
    try:
        contents = await file.read()
        image_b64 = base64.b64encode(contents).decode("utf-8")
        media_type = file.content_type or "image/jpeg"

        response = await call_vision_llm(
            client,
            system_prompt=prompts.RECEIPT_SCAN_SYSTEM_PROMPT,
            image_b64=image_b64,
            image_media_type=media_type,
            structured_output=ReceiptScanResult,
        )

        result = extract_parsed_response(response.output)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to extract items from receipt")

        return result.model_dump()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scanning receipt: {str(e)}")


# ── Meal Plan endpoints ────────────────────────────────

@app.post("/meal-plans/generate/day")
async def generate_day_plan(request: schemas.DayGenerateRequest, db: Session = Depends(get_db), x_user_id: int | None = Header(None, alias="X-User-Id")):
    try:
        user_prompt = await prompts.create_day_plan_prompt(request)
        response = await call_llm(client, prompts.MEAL_PLAN_SYSTEM_PROMPT, user_prompt, DayPlanOutput)
        day_plan = extract_parsed_response(response.output)
        if not day_plan:
            raise HTTPException(500, "Failed to generate day plan")
        result_entries = []
        for entry in day_plan.entries:
            saved = crud.save_recipe_to_db(db, entry.recipe, from_meal_plan=True, user_id=x_user_id)
            recipe_data = saveRecipe.model_validate(saved).model_dump()
            if recipe_data.get('created_at') and hasattr(recipe_data['created_at'], 'isoformat'):
                recipe_data['created_at'] = recipe_data['created_at'].isoformat()
            result_entries.append({
                "date": entry.date,
                "meal_type": entry.meal_type,
                "recipe": recipe_data,
            })
        return {"entries": result_entries}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error generating day plan: {str(e)}")


@app.post("/meal-plans", status_code=201)
def save_meal_plan_endpoint(plan: schemas.MealPlanCreate, db: Session = Depends(get_db), x_user_id: int | None = Header(None, alias="X-User-Id")):
    saved = crud.save_meal_plan(db, plan, user_id=x_user_id)
    return {
        "id": saved.id,
        "name": saved.name,
        "start_date": saved.start_date,
        "end_date": saved.end_date,
        "servings": saved.servings,
        "created_at": saved.created_at.isoformat() if saved.created_at else None,
    }


@app.get("/meal-plans")
def get_meal_plans(db: Session = Depends(get_db), x_user_id: int | None = Header(None, alias="X-User-Id")):
    plans = crud.get_all_meal_plans(db, user_id=x_user_id)
    return [
        {
            "id": p.id,
            "name": p.name,
            "start_date": p.start_date,
            "end_date": p.end_date,
            "servings": p.servings,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in plans
    ]


@app.get("/meal-plans/{plan_id}")
def get_meal_plan(plan_id: int, db: Session = Depends(get_db), x_user_id: int | None = Header(None, alias="X-User-Id")):
    plan = crud.get_meal_plan_by_id(db, plan_id, user_id=x_user_id)
    if not plan:
        raise HTTPException(404, "Meal plan not found")
    meals_out = []
    for meal in plan.meals:
        recipe_data = None
        if meal.recipe:
            rd = saveRecipe.model_validate(meal.recipe).model_dump()
            if rd.get('created_at') and hasattr(rd['created_at'], 'isoformat'):
                rd['created_at'] = rd['created_at'].isoformat()
            recipe_data = rd
        meals_out.append({
            "id": meal.id,
            "date": meal.date,
            "meal_type": meal.meal_type,
            "recipe_id": meal.recipe_id,
            "recipe": recipe_data,
        })
    return {
        "id": plan.id,
        "name": plan.name,
        "start_date": plan.start_date,
        "end_date": plan.end_date,
        "servings": plan.servings,
        "created_at": plan.created_at.isoformat() if plan.created_at else None,
        "meals": meals_out,
    }


@app.delete("/meal-plans/{plan_id}")
def delete_meal_plan_endpoint(plan_id: int, db: Session = Depends(get_db)):
    if not crud.delete_meal_plan(db, plan_id):
        raise HTTPException(404, "Meal plan not found")
    return {"message": "Deleted"}


class UpdatePlannedMealBody(BaseModel):
    date: str
    meal_type: str
    recipe_id: int

@app.put("/meal-plans/{plan_id}/meals")
def update_planned_meal(plan_id: int, body: UpdatePlannedMealBody, db: Session = Depends(get_db)):
    success = crud.update_planned_meal_recipe(db, plan_id, body.date, body.meal_type, body.recipe_id)
    if not success:
        raise HTTPException(404, "Planned meal not found")
    return {"message": "Updated"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

@app.post("/users/login")
async def login_user(request: UserLoginRequest, db: Session = Depends(get_db)):
    """Login user - check credentials against database"""
    try:
        identifier = request.username_or_email or request.email
        if not identifier:
            raise HTTPException(status_code=400, detail="Username or email is required")

        user = db.query(db_models.DBUser).filter(
            (db_models.DBUser.email == identifier) | (db_models.DBUser.username == identifier)
        ).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username/email or password")
        
        # Check password (NOTE: This is plain text comparison - use bcrypt in production!)
        if user.hashed_password != request.password:
            raise HTTPException(status_code=401, detail="Invalid username/email or password")
        
        # Update last login time
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        
        # Return user data (in production, return a JWT token instead)
        return {
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "default_servings": user.default_servings,
                "dietary_restrictions": json.loads(user.dietary_restrictions) if user.dietary_restrictions else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")