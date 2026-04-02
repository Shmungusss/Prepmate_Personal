"""
Seed script to populate database with test data
Run this to test your database models
"""

from database import SessionLocal, engine, Base
from db_models import DBUser, DBRecipe, DBRecipeIngredient, DBRecipeStep, DBGroceryList, DBGroceryItem
import json
from datetime import datetime

def seed_database():
    """Populate database with test data for all four core tables"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("🌱 Seeding database with test data...")
        
        # 1. Create test users
        print("\n👤 Creating users...")
        users = [
            DBUser(
                email="john@example.com",
                username="john_chef",
                hashed_password="hashed_password_123",  # In production, use bcrypt
                default_servings=4,
                dietary_restrictions=json.dumps(["vegetarian"])
            ),
            DBUser(
                email="sarah@example.com",
                username="sarah_cook",
                hashed_password="hashed_password_456",
                default_servings=2,
                dietary_restrictions=json.dumps(["gluten-free"])
            ),
            DBUser(
                email="mike@example.com",
                username="mike_foodie",
                hashed_password="hashed_password_789",
                default_servings=6,
                dietary_restrictions=None
            )
        ]
        
        for user in users:
            db.add(user)
        db.commit()
        print(f"✅ Created {len(users)} users")
        
        # 2. Create test recipes with ingredients and steps
        print("\n🍳 Creating recipes...")
        
        # Recipe 1: Spaghetti Carbonara
        recipe1 = DBRecipe(
            title="Classic Spaghetti Carbonara",
            description="A traditional Italian pasta dish with eggs, cheese, and pancetta",
            cuisine="italian",
            meal_type="dinner",
            difficulty="medium",
            prep_time_minutes=10,
            cook_time_minutes=20,
            total_time_minutes=30,
            servings=4,
            dietary_tags=None,
            tips=json.dumps(["Use room temperature eggs", "Reserve pasta water for sauce"]),
            notes="Traditional Roman recipe"
        )
        db.add(recipe1)
        db.flush()
        
        # Add ingredients for recipe 1
        ingredients1 = [
            DBRecipeIngredient(recipe_id=recipe1.id, name="spaghetti", quantity=1.0, unit="lb", optional=False),
            DBRecipeIngredient(recipe_id=recipe1.id, name="eggs", quantity=4.0, unit="count", optional=False),
            DBRecipeIngredient(recipe_id=recipe1.id, name="pancetta", quantity=6.0, unit="oz", optional=False),
            DBRecipeIngredient(recipe_id=recipe1.id, name="parmesan cheese", quantity=1.0, unit="cup", optional=False),
            DBRecipeIngredient(recipe_id=recipe1.id, name="black pepper", quantity=1.0, unit="tsp", optional=False),
        ]
        
        for ing in ingredients1:
            db.add(ing)
        
        # Add steps for recipe 1
        steps1 = [
            DBRecipeStep(recipe_id=recipe1.id, step_number=1, instruction="Bring a large pot of salted water to boil. Cook spaghetti according to package directions."),
            DBRecipeStep(recipe_id=recipe1.id, step_number=2, instruction="While pasta cooks, dice pancetta and cook in a large skillet until crispy."),
            DBRecipeStep(recipe_id=recipe1.id, step_number=3, instruction="In a bowl, whisk eggs with grated parmesan cheese."),
            DBRecipeStep(recipe_id=recipe1.id, step_number=4, instruction="Drain pasta, reserving 1 cup pasta water. Add hot pasta to skillet with pancetta."),
            DBRecipeStep(recipe_id=recipe1.id, step_number=5, instruction="Remove from heat. Quickly stir in egg mixture, adding pasta water as needed to create a creamy sauce."),
        ]
        
        for step in steps1:
            db.add(step)
        
        # Recipe 2: Chicken Stir Fry
        recipe2 = DBRecipe(
            title="Quick Chicken Stir Fry",
            description="Healthy and delicious chicken and vegetable stir fry",
            cuisine="chinese",
            meal_type="dinner",
            difficulty="easy",
            prep_time_minutes=15,
            cook_time_minutes=15,
            total_time_minutes=30,
            servings=4,
            dietary_tags=json.dumps(["gluten-free", "dairy-free"]),
            tips=json.dumps(["Cut chicken into uniform pieces for even cooking"]),
            notes="Use tamari for gluten-free option"
        )
        db.add(recipe2)
        db.flush()
        
        ingredients2 = [
            DBRecipeIngredient(recipe_id=recipe2.id, name="chicken breast", quantity=1.5, unit="lbs", optional=False),
            DBRecipeIngredient(recipe_id=recipe2.id, name="broccoli", quantity=2.0, unit="cups", optional=False),
            DBRecipeIngredient(recipe_id=recipe2.id, name="bell peppers", quantity=2.0, unit="count", optional=False),
            DBRecipeIngredient(recipe_id=recipe2.id, name="soy sauce", quantity=3.0, unit="tbsp", optional=False),
            DBRecipeIngredient(recipe_id=recipe2.id, name="ginger", quantity=1.0, unit="tbsp", optional=False),
        ]
        
        for ing in ingredients2:
            db.add(ing)
        
        steps2 = [
            DBRecipeStep(recipe_id=recipe2.id, step_number=1, instruction="Cut chicken into bite-sized pieces."),
            DBRecipeStep(recipe_id=recipe2.id, step_number=2, instruction="Heat oil in a wok or large skillet over high heat."),
            DBRecipeStep(recipe_id=recipe2.id, step_number=3, instruction="Cook chicken until golden, about 5-7 minutes. Remove and set aside."),
            DBRecipeStep(recipe_id=recipe2.id, step_number=4, instruction="Add vegetables to pan and stir-fry for 3-4 minutes."),
            DBRecipeStep(recipe_id=recipe2.id, step_number=5, instruction="Return chicken to pan, add sauce, and toss to combine."),
        ]
        
        for step in steps2:
            db.add(step)
        
        db.commit()
        print(f"✅ Created 2 recipes with ingredients and steps")
        
        # 3. Create test grocery lists with items
        print("\n🛒 Creating grocery lists...")
        
        # Grocery List 1
        list1 = DBGroceryList(
            title="Weekly Meal Prep",
            total_estimated_cost=125.50,
            dietary_preferences=json.dumps(["vegetarian"]),
            serves=4,
            notes="For 4 people, 7 days"
        )
        db.add(list1)
        db.flush()
        
        items1 = [
            DBGroceryItem(grocery_list_id=list1.id, name="Bananas", quantity=6.0, unit="count", category="produce", estimated_price=2.99),
            DBGroceryItem(grocery_list_id=list1.id, name="Spinach", quantity=1.0, unit="lb", category="produce", estimated_price=3.49),
            DBGroceryItem(grocery_list_id=list1.id, name="Milk", quantity=1.0, unit="gallon", category="dairy", estimated_price=4.29),
            DBGroceryItem(grocery_list_id=list1.id, name="Eggs", quantity=18.0, unit="count", category="dairy", estimated_price=5.99),
            DBGroceryItem(grocery_list_id=list1.id, name="Bread", quantity=2.0, unit="loaves", category="bakery", estimated_price=4.98),
            DBGroceryItem(grocery_list_id=list1.id, name="Rice", quantity=2.0, unit="lbs", category="pantry", estimated_price=3.99),
            DBGroceryItem(grocery_list_id=list1.id, name="Pasta", quantity=2.0, unit="boxes", category="pantry", estimated_price=2.98),
            DBGroceryItem(grocery_list_id=list1.id, name="Canned Tomatoes", quantity=4.0, unit="cans", category="pantry", estimated_price=4.76),
        ]
        
        for item in items1:
            db.add(item)
        
        # Grocery List 2
        list2 = DBGroceryList(
            title="Party Supplies",
            total_estimated_cost=75.00,
            dietary_preferences=None,
            serves=12,
            notes="For weekend BBQ"
        )
        db.add(list2)
        db.flush()
        
        items2 = [
            DBGroceryItem(grocery_list_id=list2.id, name="Ground Beef", quantity=3.0, unit="lbs", category="meat", estimated_price=14.97),
            DBGroceryItem(grocery_list_id=list2.id, name="Hamburger Buns", quantity=2.0, unit="packages", category="bakery", estimated_price=5.98),
            DBGroceryItem(grocery_list_id=list2.id, name="Lettuce", quantity=2.0, unit="heads", category="produce", estimated_price=3.98),
            DBGroceryItem(grocery_list_id=list2.id, name="Tomatoes", quantity=4.0, unit="count", category="produce", estimated_price=4.00),
            DBGroceryItem(grocery_list_id=list2.id, name="Chips", quantity=3.0, unit="bags", category="snacks", estimated_price=8.97),
            DBGroceryItem(grocery_list_id=list2.id, name="Soda", quantity=2.0, unit="cases", category="beverages", estimated_price=12.98),
        ]
        
        for item in items2:
            db.add(item)
        
        db.commit()
        print(f"✅ Created 2 grocery lists with items")
        
        print("\n" + "="*50)
        print("✅ DATABASE SEEDING COMPLETE!")
        print("="*50)
        print("\nSummary:")
        print(f"  👤 Users: {len(users)}")
        print(f"  🍳 Recipes: 2 (with {len(ingredients1) + len(ingredients2)} ingredients)")
        print(f"  🛒 Grocery Lists: 2 (with {len(items1) + len(items2)} items)")
        print("\nYou can now:")
        print("  - View data at http://localhost:8000/docs")
        print("  - Query: GET /recipes, /grocery-lists, /users")
        print("  - Use DB Browser to explore: grocery_recipe.db")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Starting database seed...")
    seed_database()
