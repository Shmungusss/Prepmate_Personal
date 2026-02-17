# PrepMate Integration Guide

## Overview

This document describes how the PrepMate frontend (Vue.js) and backend (FastAPI) communicate, including API endpoints, data formats, and integration patterns.

## System Architecture

```mermaid
graph LR
    User[User] --> Frontend[Vue.js Frontend<br/>localhost:3000]
    Frontend --> Backend[FastAPI Backend<br/>localhost:8000]
    Backend --> DB[(Database)]
    Backend --> OpenAI[OpenAI API]
    
    style User fill:#e1f5ff
    style Frontend fill:#4fc3f7
    style Backend fill:#66bb6a
    style DB fill:#ffa726
    style OpenAI fill:#ab47bc
```

## Communication Protocol

### Protocol Details
- **Protocol**: REST API over HTTP/HTTPS
- **Data Format**: JSON
- **Content-Type**: `application/json`
- **Authentication**: TBD (JWT tokens recommended for future)
- **CORS**: Enabled for `localhost:3000` and `localhost:5173`

### API Base URLs

| Environment | Frontend URL | Backend URL |
|------------|--------------|-------------|
| Development | `http://localhost:3000` | `http://localhost:8000` |
| Production | TBD | TBD |

## Frontend Service Layer

### API Service Structure

```
web/
├── src/
│   ├── services/
│   │   ├── api.js              # Base API configuration
│   │   ├── recipeService.js    # Recipe-related API calls
│   │   ├── groceryService.js   # Grocery list API calls
│   │   └── ingredientService.js # Ingredient management API calls
```

### Base API Configuration (`api.js`)

```javascript
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
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    return await response.json()
  }
}
```

## Request/Response Flows

### 1. Recipe Generation Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant AI as OpenAI
    participant DB as Database
    
    U->>F: Fill form & click Generate
    F->>F: Validate input locally
    F->>B: POST /api/recipes/generate
    Note over F,B: Request Body:<br/>{ingredients, servings, cuisine, dietary}
    B->>B: Validate request
    B->>AI: Send recipe generation prompt
    AI-->>B: Return generated recipe
    B->>DB: Save recipe to database
    DB-->>B: Return recipe ID
    B-->>F: Recipe JSON response
    Note over B,F: Response:<br/>{id, title, ingredients, steps}
    F->>F: Update UI with recipe
    F->>U: Display recipe
```

**Frontend Code Example:**
```javascript
// In Home.vue
import { generateRecipe } from '@/services/recipeService'

async function onGenerateRecipe() {
  try {
    generating.value = true
    const recipe = await generateRecipe({
      ingredients: ingredients.value,
      servings: servings.value,
      cuisine: cuisine.value,
      dietary: dietary.value
    })
    // Display recipe to user
    recipeData.value = recipe
  } catch (error) {
    console.error('Recipe generation failed:', error)
  } finally {
    generating.value = false
  }
}
```

### 2. Grocery List Creation Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant DB as Database
    
    U->>F: Click "Add to Grocery List"
    F->>B: POST /api/grocery-lists/add-recipe
    Note over F,B: Request Body:<br/>{recipe_id, user_id}
    B->>DB: Get recipe ingredients
    DB-->>B: Ingredient list
    B->>DB: Check user's pantry
    DB-->>B: Available ingredients
    B->>B: Calculate missing items
    B->>DB: Create/update grocery list
    DB-->>B: Grocery list ID
    B-->>F: Grocery list JSON
    Note over B,F: Response:<br/>{id, items, total_cost}
    F->>U: Display grocery list
```

### 3. Ingredient Management Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant DB as Database
    
    U->>F: Add ingredient to pantry
    F->>B: POST /api/ingredients
    Note over F,B: Request Body:<br/>{name, quantity, unit, category}
    B->>B: Validate ingredient data
    B->>DB: Save ingredient
    DB-->>B: Ingredient ID
    B-->>F: Ingredient JSON
    F->>U: Update pantry display
```

## API Endpoints Overview

### Core Endpoints

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|---------|
| GET | `/` | Health check / welcome | ✅ Implemented |
| GET | `/api/health` | Detailed health status | ✅ Implemented |
| POST | `/api/recipes/generate` | Generate recipe from ingredients | 🔄 Week 4 |
| GET | `/api/recipes/:id` | Get recipe by ID | 🔄 Week 4 |
| POST | `/api/grocery-lists/add-recipe` | Add recipe to grocery list | 🔄 Week 5 |
| GET | `/api/grocery-lists/:id` | Get grocery list | 🔄 Week 5 |
| POST | `/api/ingredients` | Add ingredient to pantry | 🔄 Week 5 |
| GET | `/api/ingredients` | List user's ingredients | 🔄 Week 5 |

## Error Handling

### Standard Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid ingredients provided",
    "details": {
      "field": "ingredients",
      "issue": "At least one ingredient is required"
    }
  }
}
```

### HTTP Status Codes

| Status Code | Meaning | Usage |
|------------|---------|-------|
| 200 | OK | Successful GET/PUT |
| 201 | Created | Successful POST |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing/invalid authentication |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |

### Frontend Error Handling Pattern

```javascript
try {
  const response = await fetch(`${API_BASE_URL}/api/recipes/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(recipeRequest)
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.message || `HTTP ${response.status}`)
  }
  
  return await response.json()
} catch (error) {
  console.error('API Error:', error)
  // Display user-friendly error message
  showErrorMessage(error.message)
}
```

## CORS Configuration

### Backend (FastAPI)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        # Add production URLs here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend Environment Variables

Create `.env` file in frontend:
```
VITE_API_BASE_URL=http://localhost:8000
```

## Data Validation

### Frontend Validation
- Required fields checking
- Input format validation
- Length limits
- Type checking

### Backend Validation
- Pydantic models for request validation
- Business logic validation
- Database constraint checks

### Example: Recipe Request Validation

**Frontend:**
```javascript
function validateRecipeRequest(data) {
  if (!data.ingredients || data.ingredients.trim().length === 0) {
    throw new Error('At least one ingredient is required')
  }
  if (data.servings < 1 || data.servings > 10) {
    throw new Error('Servings must be between 1 and 10')
  }
  return true
}
```

**Backend:**
```python
from pydantic import BaseModel, validator

class RecipeRequest(BaseModel):
    ingredients: str
    servings: int
    cuisine: str = ""
    dietary: str = ""
    
    @validator('ingredients')
    def ingredients_not_empty(cls, v):
        if not v.strip():
            raise ValueError('At least one ingredient is required')
        return v
    
    @validator('servings')
    def servings_valid_range(cls, v):
        if v < 1 or v > 10:
            raise ValueError('Servings must be between 1 and 10')
        return v
```

## State Management

### Frontend State Flow

```mermaid
graph TD
    UserInput[User Input] --> ComponentState[Component State]
    ComponentState --> APICall[API Call]
    APICall --> Loading[Loading State]
    APICall --> Success[Success State]
    APICall --> Error[Error State]
    Success --> DisplayData[Display Data]
    Error --> ErrorMessage[Error Message]
    
    style UserInput fill:#e1f5ff
    style Success fill:#66bb6a
    style Error fill:#ff7043
```

### Example: Recipe State Management

```javascript
import { ref } from 'vue'

export default {
  setup() {
    // State
    const recipe = ref(null)
    const loading = ref(false)
    const error = ref(null)
    
    // Action
    async function generateRecipe(params) {
      loading.value = true
      error.value = null
      
      try {
        const data = await recipeService.generate(params)
        recipe.value = data
      } catch (err) {
        error.value = err.message
      } finally {
        loading.value = false
      }
    }
    
    return { recipe, loading, error, generateRecipe }
  }
}
```

## Testing Integration

### Frontend Testing
```javascript
// Test API service
import { describe, it, expect, vi } from 'vitest'
import { generateRecipe } from '@/services/recipeService'

describe('recipeService', () => {
  it('should generate recipe with valid input', async () => {
    const mockRecipe = { id: 1, title: 'Test Recipe' }
    global.fetch = vi.fn(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockRecipe)
      })
    )
    
    const result = await generateRecipe({
      ingredients: 'chicken, rice',
      servings: 2
    })
    
    expect(result).toEqual(mockRecipe)
  })
})
```

### Backend Testing
```python
# Test API endpoint
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_generate_recipe():
    response = client.post("/api/recipes/generate", json={
        "ingredients": "chicken, rice",
        "servings": 2,
        "cuisine": "italian",
        "dietary": ""
    })
    assert response.status_code == 200
    assert "title" in response.json()
```

## Performance Considerations

### Request Optimization
- Debounce user input for search/autocomplete
- Batch multiple requests when possible
- Cache frequently accessed data
- Use pagination for large datasets

### Response Optimization
- Return only necessary fields
- Compress responses (gzip)
- Use appropriate HTTP caching headers
- Implement server-side pagination

## Security Best Practices

1. **Never expose API keys in frontend code**
   - All AI API calls go through backend
   - Use environment variables

2. **Validate all inputs**
   - Frontend validation for UX
   - Backend validation for security

3. **Use HTTPS in production**
   - Encrypt data in transit

4. **Implement rate limiting**
   - Prevent abuse and excessive API costs

5. **Sanitize user input**
   - Prevent XSS and injection attacks

## Development Workflow

### Local Development Setup

1. **Start Backend:**
   ```bash
   cd api
   python app.py
   # Server runs on http://localhost:8000
   ```

2. **Start Frontend:**
   ```bash
   cd web
   npm run dev
   # Server runs on http://localhost:3000
   ```

3. **Verify Connection:**
   - Open `http://localhost:3000`
   - Use "Backend Connection Test" section
   - Both endpoints should return success

### Environment Configuration

**Backend `.env`:**
```
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost/prepmate
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Frontend `.env`:**
```
VITE_API_BASE_URL=http://localhost:8000
```

## Deployment Considerations

### Production Checklist
- [ ] Set proper CORS origins for production URLs
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS/TLS
- [ ] Implement rate limiting
- [ ] Set up error monitoring (e.g., Sentry)
- [ ] Configure logging
- [ ] Set up database connection pooling
- [ ] Implement caching strategy
- [ ] Set up CI/CD pipeline
- [ ] Configure health check endpoints

## Troubleshooting

### Common Issues

1. **CORS Error**
   - Verify backend CORS configuration includes frontend URL
   - Check that requests include proper headers

2. **Connection Refused**
   - Ensure backend is running on correct port
   - Check `VITE_API_BASE_URL` environment variable

3. **422 Unprocessable Entity**
   - Request body doesn't match expected schema
   - Check Pydantic model in backend

4. **500 Internal Server Error**
   - Check backend logs for stack trace
   - Verify database connection
   - Check external API (OpenAI) status

## Next Steps

### Week 4 Implementation
1. Implement recipe generation endpoint
2. Add OpenAI integration
3. Create database models
4. Add comprehensive error handling

### Week 5 Implementation
1. Implement grocery list endpoints
2. Add ingredient management
3. Implement user pantry functionality
4. Add recipe saving and favorites

## Conclusion

This integration guide provides the foundation for seamless communication between the PrepMate frontend and backend. Following these patterns ensures consistency, maintainability, and scalability as the project grows.
