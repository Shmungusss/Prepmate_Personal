from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone


class DBUser(Base):
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    
    # User preferences
    default_servings = Column(Integer, default=4)
    dietary_restrictions = Column(Text, nullable=True)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)
    
    # Relationships (ready for future use when connecting users to recipes/lists)
    # recipes = relationship("DBRecipe", back_populates="user")
    # grocery_lists = relationship("DBGroceryList", back_populates="user")


class DBRecipe(Base):
    """Database model for storing recipes"""
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    cuisine = Column(String, nullable=False)
    meal_type = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    
    # Time fields
    prep_time_minutes = Column(Integer, nullable=False)
    cook_time_minutes = Column(Integer, nullable=False)
    total_time_minutes = Column(Integer, nullable=False)
    
    # Servings
    servings = Column(Integer, nullable=False)
    
    # Additional info stored as JSON strings
    dietary_tags = Column(Text, nullable=True)  # Store as JSON string
    tips = Column(Text, nullable=True)  # Store as JSON string
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # If True, recipe was auto-generated for a meal plan and is not shown in the saved recipes collection
    from_meal_plan = Column(Boolean, default=False, nullable=False)

    # Relationships
    ingredients = relationship("DBRecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    instructions = relationship("DBRecipeStep", back_populates="recipe", cascade="all, delete-orphan")


class DBRecipeIngredient(Base):
    """Database model for recipe ingredients"""
    __tablename__ = "recipe_ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    
    name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    optional = Column(Boolean, default=False)
    location = Column(String, nullable=True)
    category = Column(String, nullable=True)

    # Relationship
    recipe = relationship("DBRecipe", back_populates="ingredients")


class DBRecipeStep(Base):
    """Database model for recipe instructions"""
    __tablename__ = "recipe_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    
    step_number = Column(Integer, nullable=False)
    instruction = Column(Text, nullable=False)
    
    # Relationship
    recipe = relationship("DBRecipe", back_populates="instructions")


class DBPantryItem(Base):
    """Database model for pantry items"""
    __tablename__ = "pantry_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    quantity = Column(String, nullable=True)
    unit = Column(String, nullable=True)
    location = Column(String, nullable=False, default='pantry')
    category = Column(String, nullable=False, default='Other')
    added_at = Column(String, nullable=True)


class DBGroceryList(Base):
    """Database model for storing grocery lists"""
    __tablename__ = "grocery_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    
    total_estimated_cost = Column(Float, nullable=True)
    dietary_preferences = Column(Text, nullable=True)  # Store as JSON string
    serves = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    items = relationship("DBGroceryItem", back_populates="grocery_list", cascade="all, delete-orphan")


class DBGroceryItem(Base):
    """Database model for grocery list items"""
    __tablename__ = "grocery_items"

    id = Column(Integer, primary_key=True, index=True)
    grocery_list_id = Column(Integer, ForeignKey("grocery_lists.id"), nullable=False)

    name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    category = Column(String, nullable=False)
    estimated_price = Column(Float, nullable=True)
    notes = Column(String, nullable=True)

    # Relationship
    grocery_list = relationship("DBGroceryList", back_populates="items")


class DBMealPlan(Base):
    """Database model for meal plans"""
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    servings = Column(Integer, nullable=False, default=2)
    created_at = Column(DateTime, default=datetime.utcnow)
    meals = relationship("DBPlannedMeal", back_populates="meal_plan", cascade="all, delete-orphan")


class DBPlannedMeal(Base):
    """Database model for individual planned meals within a meal plan"""
    __tablename__ = "planned_meals"

    id = Column(Integer, primary_key=True, index=True)
    meal_plan_id = Column(Integer, ForeignKey("meal_plans.id"), nullable=False)
    date = Column(String, nullable=False)
    meal_type = Column(String, nullable=False)  # breakfast/lunch/dinner/snack
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=True)
    meal_plan = relationship("DBMealPlan", back_populates="meals")
    recipe = relationship("DBRecipe")