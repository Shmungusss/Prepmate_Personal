from sqlalchemy.orm import Session
from db_models import DBRecipe, DBRecipeIngredient, DBRecipeStep, DBGroceryList, DBGroceryItem, DBPantryItem, DBMealPlan, DBPlannedMeal
from models import Recipe, GroceryList
from schemas import PantryItemCreate, PantryItemUpdate
import json


def save_recipe_to_db(db: Session, recipe: Recipe, from_meal_plan: bool = False) -> DBRecipe:
    """Save a Pydantic Recipe model to the database"""

    # Create the main recipe record
    db_recipe = DBRecipe(
        title=recipe.title,
        description=recipe.description,
        cuisine=recipe.cuisine.value,
        meal_type=recipe.meal_type.value,
        difficulty=recipe.difficulty.value,
        prep_time_minutes=recipe.prep_time_minutes,
        cook_time_minutes=recipe.cook_time_minutes,
        total_time_minutes=recipe.total_time_minutes,
        servings=recipe.servings,
        dietary_tags=json.dumps(recipe.dietary_tags) if recipe.dietary_tags else None,
        tips=json.dumps(recipe.tips) if recipe.tips else None,
        notes=recipe.notes,
        from_meal_plan=from_meal_plan,
    )
    
    db.add(db_recipe)
    db.flush()  # Get the recipe ID before adding related items
    
    # Add ingredients
    for ingredient in recipe.ingredients:
        db_ingredient = DBRecipeIngredient(
            recipe_id=db_recipe.id,
            name=ingredient.name,
            quantity=ingredient.quantity,
            unit=ingredient.unit,
            notes=ingredient.notes,
            optional=ingredient.optional,
            location=ingredient.location,
            category=ingredient.category,
        )
        db.add(db_ingredient)
    
    # Add instructions
    for step in recipe.instructions:
        db_step = DBRecipeStep(
            recipe_id=db_recipe.id,
            step_number=step.step_number,
            instruction=step.instruction
        )
        db.add(db_step)
    
    db.commit()
    db.refresh(db_recipe)
    
    return db_recipe


def save_grocery_list_to_db(db: Session, grocery_list: GroceryList) -> DBGroceryList:
    """Save a Pydantic GroceryList model to the database"""
    
    # Create the main grocery list record
    db_grocery_list = DBGroceryList(
        title=grocery_list.title,
        total_estimated_cost=grocery_list.total_estimated_cost,
        dietary_preferences=json.dumps(grocery_list.dietary_preferences) if grocery_list.dietary_preferences else None,
        serves=grocery_list.serves,
        notes=grocery_list.notes
    )
    
    db.add(db_grocery_list)
    db.flush()  # Get the grocery list ID
    
    # Add items
    for item in grocery_list.items:
        db_item = DBGroceryItem(
            grocery_list_id=db_grocery_list.id,
            name=item.name,
            quantity=item.quantity,
            unit=item.unit,
            category=item.category.value,
            estimated_price=item.estimated_price,
            notes=item.notes
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_grocery_list)
    
    return db_grocery_list


def get_all_recipes(db: Session):
    """Retrieve all user-saved recipes (excludes meal-plan-only recipes)"""
    return db.query(DBRecipe).filter(DBRecipe.from_meal_plan == False).all()


def promote_recipe_to_collection(db: Session, recipe_id: int) -> DBRecipe | None:
    """Mark a meal-plan recipe as saved to the user's collection"""
    recipe = db.query(DBRecipe).filter(DBRecipe.id == recipe_id).first()
    if not recipe:
        return None
    recipe.from_meal_plan = False
    db.commit()
    db.refresh(recipe)
    return recipe


def get_recipe_by_id(db: Session, recipe_id: int):
    """Retrieve a single recipe by ID"""
    return db.query(DBRecipe).filter(DBRecipe.id == recipe_id).first()


def get_all_grocery_lists(db: Session):
    """Retrieve all grocery lists from database"""
    return db.query(DBGroceryList).all()


def get_grocery_list_by_id(db: Session, list_id: int):
    """Retrieve a single grocery list by ID"""
    return db.query(DBGroceryList).filter(DBGroceryList.id == list_id).first()


def delete_recipe(db: Session, recipe_id: int) -> bool:
    """Delete a recipe and all related data"""
    recipe = get_recipe_by_id(db, recipe_id)
    if recipe:
        db.delete(recipe)
        db.commit()
        return True
    return False


# ── Pantry ────────────────────────────────────────────
def get_all_pantry_items(db: Session):
    return db.query(DBPantryItem).order_by(DBPantryItem.id).all()

def create_pantry_item(db: Session, item: PantryItemCreate) -> DBPantryItem:
    db_item = DBPantryItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def bulk_create_pantry_items(db: Session, items: list[PantryItemCreate]) -> list[DBPantryItem]:
    db_items = [DBPantryItem(**item.model_dump()) for item in items]
    db.add_all(db_items)
    db.commit()
    for i in db_items:
        db.refresh(i)
    return db_items

def update_pantry_item(db: Session, item_id: int, patch: PantryItemUpdate) -> DBPantryItem | None:
    item = db.query(DBPantryItem).filter(DBPantryItem.id == item_id).first()
    if not item:
        return None
    for field, value in patch.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item

def delete_pantry_item(db: Session, item_id: int) -> bool:
    item = db.query(DBPantryItem).filter(DBPantryItem.id == item_id).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def delete_grocery_list(db: Session, list_id: int) -> bool:
    """Delete a grocery list and all related items"""
    grocery_list = get_grocery_list_by_id(db, list_id)
    if grocery_list:
        db.delete(grocery_list)
        db.commit()
        return True
    return False


# ── Meal Plan CRUD ─────────────────────────────────────

def save_meal_plan(db: Session, plan_data):
    """Save a meal plan and its planned meals to the database"""
    db_plan = DBMealPlan(
        name=plan_data.name,
        start_date=plan_data.start_date,
        end_date=plan_data.end_date,
        servings=plan_data.servings,
    )
    db.add(db_plan)
    db.flush()
    for meal in plan_data.meals:
        db.add(DBPlannedMeal(
            meal_plan_id=db_plan.id,
            date=meal.date,
            meal_type=meal.meal_type,
            recipe_id=meal.recipe_id,
        ))
    db.commit()
    db.refresh(db_plan)
    return db_plan


def get_all_meal_plans(db: Session):
    return db.query(DBMealPlan).order_by(DBMealPlan.created_at.desc()).all()


def get_meal_plan_by_id(db: Session, plan_id: int):
    return db.query(DBMealPlan).filter(DBMealPlan.id == plan_id).first()


def delete_meal_plan(db: Session, plan_id: int) -> bool:
    plan = get_meal_plan_by_id(db, plan_id)
    if not plan:
        return False
    db.delete(plan)
    db.commit()
    return True


def update_planned_meal_recipe(db: Session, plan_id: int, date: str, meal_type: str, new_recipe_id: int) -> bool:
    meal = (
        db.query(DBPlannedMeal)
        .filter(
            DBPlannedMeal.meal_plan_id == plan_id,
            DBPlannedMeal.date == date,
            DBPlannedMeal.meal_type == meal_type,
        )
        .first()
    )
    if not meal:
        return False
    meal.recipe_id = new_recipe_id
    db.commit()
    return True