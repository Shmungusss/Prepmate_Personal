# Database Migrations Guide

This project uses **Alembic** for database migrations, allowing you to version control your database schema changes.

## Setup

### 1. Install Alembic

```bash
pip install alembic
```

(Already included in `requirements.txt`)

### 2. Initialize (Already Done)

The alembic folder structure is already set up. If you need to reinitialize:

```bash
alembic init alembic
```

## Common Commands

### Create a New Migration

When you change your models in `db_models.py`, create a migration:

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add user table"

# Or create empty migration to write manually
alembic revision -m "Add user table"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Downgrade to base (empty database)
alembic downgrade base
```

### View Migration History

```bash
# Show current version
alembic current

# Show all revisions
alembic history

# Show what will be applied
alembic heads
```

## Initial Migration (For This Project)

Since we already have tables created by SQLAlchemy, here's how to sync Alembic:

### Option 1: Fresh Start (Recommended for Development)

```bash
# Delete existing database
rm grocery_recipe.db

# Create initial migration
alembic revision --autogenerate -m "Initial migration - all tables"

# Apply it
alembic upgrade head

# Seed with test data
python seed_database.py
```

### Option 2: Stamp Existing Database

If you want to keep existing data:

```bash
# Create migration
alembic revision --autogenerate -m "Initial migration"

# Mark database as current without running migration
alembic stamp head
```

## Workflow for Schema Changes

1. **Make changes** to `db_models.py`

```python
# Example: Add a new field
class DBRecipe(Base):
    # ... existing fields ...
    rating = Column(Float, nullable=True)  # NEW FIELD
```

2. **Generate migration**

```bash
alembic revision --autogenerate -m "Add rating to recipes"
```

3. **Review the migration** in `alembic/versions/xxxx_add_rating_to_recipes.py`

4. **Apply the migration**

```bash
alembic upgrade head
```

5. **Test** your changes

```bash
python app.py
# Or run tests
pytest tests/
```

## Migration File Structure

```
alembic/
├── versions/
│   ├── 001_initial_migration.py
│   ├── 002_add_user_table.py
│   └── 003_add_rating_field.py
├── env.py          # Migration environment config
└── script.py.mako  # Template for new migrations
```

Each migration file has:
- `upgrade()` - How to apply the change
- `downgrade()` - How to reverse the change

## Example Migration File

```python
"""Add rating to recipes

Revision ID: abc123
Revises: def456
Create Date: 2024-02-23 10:30:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123'
down_revision = 'def456'

def upgrade() -> None:
    op.add_column('recipes', sa.Column('rating', sa.Float(), nullable=True))

def downgrade() -> None:
    op.drop_column('recipes', 'rating')
```

## Troubleshooting

### "Can't locate revision identified by 'xxxx'"

```bash
# Check current state
alembic current

# Stamp to specific revision
alembic stamp head
```

### Migration conflicts

```bash
# View history
alembic history

# Manually edit migration files to resolve conflicts
# Then apply
alembic upgrade head
```

### Start fresh

```bash
rm grocery_recipe.db
rm -rf alembic/versions/*.py
alembic revision --autogenerate -m "Fresh start"
alembic upgrade head
```

## Best Practices

1. **Always review** auto-generated migrations before applying
2. **Test migrations** on a copy of production data
3. **Never edit** applied migrations - create new ones
4. **Commit migrations** to git along with model changes
5. **Document** complex migrations with comments

## Integration with Your Workflow

### Development

```bash
# Make model changes
# Generate migration
alembic revision --autogenerate -m "description"
# Review migration file
# Apply migration
alembic upgrade head
# Test
python app.py
```

### Testing

```bash
# Tests should use a separate test database
# See tests/conftest.py for setup
pytest tests/
```

### Production Deployment

```bash
# On production server
git pull
alembic upgrade head  # Apply any pending migrations
# Restart your API server
```

## Week 2 Thursday Milestone Checklist

- [x] All four core tables exist (User, Recipe, GroceryList, Ingredient)
- [x] Alembic is set up and configured
- [x] Initial migration created
- [x] Database can be seeded with test data
- [x] Migrations are documented

Run this to verify:
```bash
# Apply migrations
alembic upgrade head

# Seed database
python seed_database.py

# Check tables exist
sqlite3 grocery_recipe.db ".tables"

# Should show: grocery_items, grocery_lists, recipe_ingredients, recipe_steps, recipes, users
```
