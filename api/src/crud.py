from sqlalchemy.orm import Session
from db_models import DBRecipe, DBRecipeIngredient, DBRecipeStep, DBGroceryList, DBGroceryItem
from models import Recipe, GroceryList
import json


def save_recipe_to_db(db: Session, recipe: Recipe) -> DBRecipe:
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
        notes=recipe.notes
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
            optional=ingredient.optional
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
    """Retrieve all recipes from database"""
    return db.query(DBRecipe).all()


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


def delete_grocery_list(db: Session, list_id: int) -> bool:
    """Delete a grocery list and all related items"""
    grocery_list = get_grocery_list_by_id(db, list_id)
    if grocery_list:
        db.delete(grocery_list)
        db.commit()
        return True
    return False