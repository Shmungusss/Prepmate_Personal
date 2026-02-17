# PrepMate Project Structure

## Repository Overview

PrepMate consists of two main repositories that work together to create the complete application.

```mermaid
graph TB
    subgraph "prepmate-api Repository"
        API[API Code]
        APIDocs[API Documentation]
        APITests[API Tests]
    end
    
    subgraph "prepmate-web Repository"
        Web[Frontend Code]
        WebAssets[Static Assets]
        WebTests[Frontend Tests]
    end
    
    API --> Web
    
    style API fill:#66bb6a
    style Web fill:#4fc3f7
```

## Directory Structure

### Backend Repository (`prepmate-api`)

```
prepmate-api/
├── app.py                      # Main FastAPI application entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore rules
├── README.md                  # Backend setup instructions
│
├── api/                       # API package (Week 4+)
│   ├── __init__.py
│   ├── main.py               # FastAPI app initialization
│   ├── config.py             # Configuration management
│   │
│   ├── routes/               # API route handlers
│   │   ├── __init__.py
│   │   ├── recipes.py        # Recipe endpoints
│   │   ├── grocery_lists.py  # Grocery list endpoints
│   │   └── ingredients.py    # Ingredient endpoints
│   │
│   ├── services/             # Business logic layer
│   │   ├── __init__.py
│   │   ├── recipe_service.py
│   │   ├── grocery_service.py
│   │   ├── ingredient_service.py
│   │   └── openai_service.py # AI integration
│   │
│   ├── models/               # Database models
│   │   ├── __init__.py
│   │   ├── recipe.py
│   │   ├── grocery_list.py
│   │   ├── ingredient.py
│   │   └── user.py
│   │
│   ├── schemas/              # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── recipe.py
│   │   ├── grocery_list.py
│   │   └── ingredient.py
│   │
│   └── utils/                # Utility functions
│       ├── __init__.py
│       ├── validators.py
│       └── helpers.py
│
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_recipes.py
│   ├── test_grocery_lists.py
│   └── test_ingredients.py
│
└── docs/                     # Documentation
    ├── README.md             # Documentation index
    ├── ARCHITECTURE.md       # System architecture
    ├── API_DOCUMENTATION.md  # API reference
    ├── INTEGRATION_GUIDE.md  # Frontend-Backend integration
    ├── DATABASE_SCHEMA.md    # Database design
    ├── BACKEND_SETUP.md      # Development setup
    └── OPENAI_INTEGRATION.md # AI service integration
```

### Frontend Repository (`prepmate-web`)

```
prepmate-web/
├── index.html                # HTML entry point
├── package.json              # npm dependencies
├── package-lock.json         # Dependency lock file
├── vite.config.js           # Vite configuration
├── .env.example             # Example environment variables
├── .gitignore               # Git ignore rules
├── README.md                # Frontend setup instructions
│
├── public/                  # Static assets
│   ├── vite.svg
│   └── favicon.ico
│
└── src/                     # Source code
    ├── main.js              # Vue app entry point
    ├── App.vue              # Root component
    │
    ├── router/              # Vue Router configuration
    │   └── index.js
    │
    ├── views/               # Page components
    │   ├── Home.vue         # Landing/recipe generator page
    │   ├── RecipeDetail.vue # Individual recipe view (Week 4+)
    │   ├── GroceryList.vue  # Grocery list page (Week 5+)
    │   └── Pantry.vue       # Ingredient manager (Week 5+)
    │
    ├── components/          # Reusable components (Week 4+)
    │   ├── RecipeCard.vue
    │   ├── IngredientList.vue
    │   ├── GroceryItem.vue
    │   └── LoadingSpinner.vue
    │
    ├── services/            # API service layer
    │   ├── api.js           # Base API configuration
    │   ├── recipeService.js # Recipe API calls
    │   ├── groceryService.js # Grocery list API calls
    │   └── ingredientService.js # Ingredient API calls
    │
    ├── composables/         # Vue composables (Week 5+)
    │   ├── useRecipes.js
    │   └── useGroceryList.js
    │
    ├── utils/               # Utility functions
    │   ├── validators.js
    │   └── formatters.js
    │
    └── assets/              # Static assets
        ├── styles/
        │   └── global.css
        └── images/
```

## File Naming Conventions

### Backend (Python)
- **Files**: Use snake_case (e.g., `recipe_service.py`)
- **Classes**: Use PascalCase (e.g., `RecipeService`)
- **Functions**: Use snake_case (e.g., `generate_recipe()`)
- **Constants**: Use UPPER_SNAKE_CASE (e.g., `MAX_INGREDIENTS`)

### Frontend (JavaScript/Vue)
- **Vue Components**: Use PascalCase (e.g., `RecipeCard.vue`)
- **JavaScript files**: Use camelCase (e.g., `recipeService.js`)
- **Functions**: Use camelCase (e.g., `generateRecipe()`)
- **Constants**: Use UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)

## Key Files Explained

### Backend Files

#### `app.py` (Current)
- FastAPI application entry point
- CORS middleware configuration
- Basic health check endpoints
- Development server startup

#### `api/config.py` (Week 4)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "PrepMate API"
    API_VERSION: str = "0.1.0"
    
    # Database
    DATABASE_URL: str
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    
    # Security
    CORS_ORIGINS: list = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
```

#### `api/routes/recipes.py` (Week 4)
- Recipe generation endpoint
- Recipe retrieval endpoints
- Recipe management endpoints

#### `api/services/openai_service.py` (Week 4)
- OpenAI API integration
- Recipe generation prompts
- Response parsing and validation

### Frontend Files

#### `src/main.js`
- Vue app initialization
- Router setup
- Global plugins registration

#### `src/router/index.js`
- Route definitions
- Navigation guards (future: authentication)

#### `src/services/api.js`
```javascript
// Base API configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = {
  async request(endpoint, options = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || `HTTP ${response.status}`)
    }

    return await response.json()
  },

  get(endpoint) {
    return this.request(endpoint, { method: 'GET' })
  },

  post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }
}
```

## Environment Variables

### Backend `.env`
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/prepmate

# OpenAI API
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Server
HOST=0.0.0.0
PORT=8000
```

### Frontend `.env`
```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Feature Flags (optional)
VITE_ENABLE_ANALYTICS=false
```

## Dependencies

### Backend (`requirements.txt`)
```
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.5.0
pydantic-settings==2.1.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
openai==1.3.0
python-dotenv==1.0.0
pytest==7.4.3
httpx==0.25.1
```

### Frontend (`package.json`)
```json
{
  "dependencies": {
    "vue": "^3.5.24",
    "vue-router": "^4.6.4"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^6.0.1",
    "vite": "^7.2.4",
    "vitest": "^1.0.0"
  }
}
```

## Git Workflow

### Branch Strategy
```
main
├── develop
│   ├── feature/recipe-generation
│   ├── feature/grocery-lists
│   ├── feature/ingredient-manager
│   └── feature/user-auth
└── hotfix/critical-bug
```

### Branch Naming Convention
- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `hotfix/critical-issue` - Critical production fixes
- `docs/documentation-update` - Documentation only

### Commit Message Format
```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(recipes): add recipe generation endpoint

Implements OpenAI integration for generating recipes
based on user ingredients and preferences.

Closes #12
```

```
fix(cors): add missing CORS origin

Added localhost:5173 to allowed CORS origins
for Vite dev server compatibility.
```

## Code Organization Principles

### 1. Separation of Concerns
- **Routes**: Handle HTTP requests/responses
- **Services**: Business logic and external API calls
- **Models**: Database schema and ORM
- **Schemas**: Request/response validation

### 2. DRY (Don't Repeat Yourself)
- Extract common functionality into utilities
- Use composables/mixins for shared Vue logic
- Create reusable components

### 3. Single Responsibility
- Each file/module should have one clear purpose
- Keep functions small and focused
- Components should be atomic when possible

### 4. Dependency Injection
- Pass dependencies as parameters
- Use dependency injection in FastAPI
- Easier testing and maintenance

## Testing Structure

### Backend Tests
```
tests/
├── conftest.py              # Pytest fixtures
├── test_recipes.py          # Recipe endpoint tests
├── test_grocery_lists.py    # Grocery list tests
├── test_ingredients.py      # Ingredient tests
└── test_openai_service.py   # AI service tests
```

### Frontend Tests (Future)
```
src/
├── components/
│   └── __tests__/
│       └── RecipeCard.spec.js
├── services/
│   └── __tests__/
│       └── recipeService.spec.js
└── views/
    └── __tests__/
        └── Home.spec.js
```

## Documentation Structure

All documentation lives in `prepmate-api/docs/`:

1. **README.md** - Documentation index
2. **ARCHITECTURE.md** - System design and diagrams
3. **API_DOCUMENTATION.md** - Complete API reference
4. **INTEGRATION_GUIDE.md** - Frontend-backend integration
5. **DATABASE_SCHEMA.md** - Database design (Week 4)
6. **BACKEND_SETUP.md** - Development setup guide
7. **OPENAI_INTEGRATION.md** - AI service integration (Week 4)

## Development Workflow

### Adding a New Feature

1. **Create feature branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Backend: Add route, service, model**
   - Define Pydantic schema in `api/schemas/`
   - Create database model in `api/models/`
   - Implement business logic in `api/services/`
   - Add route handler in `api/routes/`
   - Write tests in `tests/`

3. **Frontend: Add service and component**
   - Create API service function in `src/services/`
   - Build Vue component in `src/components/` or `src/views/`
   - Update router if needed
   - Style component

4. **Test integration**
   - Run backend tests: `pytest`
   - Manual testing with frontend
   - Check browser console for errors

5. **Create pull request**
   - Descriptive title and description
   - Link to related issues
   - Request team review

## Best Practices

### Backend
- Use type hints for all functions
- Validate all input with Pydantic models
- Handle errors gracefully with try/except
- Use async/await for I/O operations
- Keep routes thin, logic in services
- Write docstrings for all functions

### Frontend
- Use Composition API (not Options API)
- Extract reusable logic to composables
- Keep components small and focused
- Use props for parent-child communication
- Emit events for child-parent communication
- Handle loading and error states

### Both
- Write meaningful commit messages
- Keep functions under 50 lines when possible
- Add comments for complex logic
- Update documentation when changing behavior
- Run tests before committing
- Use environment variables for configuration

## Conclusion

This structure provides a scalable foundation for PrepMate. As the project grows, new directories and files can be added following these established patterns and conventions.
