from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


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