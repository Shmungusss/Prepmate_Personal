# PrepMate API Documentation

## Overview

The PrepMate API provides endpoints for recipe generation, grocery list management, and ingredient tracking. All endpoints return JSON responses and follow RESTful conventions.

**Base URL:** `http://localhost:8000` (development)

**API Version:** v0.1.0

## Table of Contents

- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Health & Status](#health--status)
  - [Recipes](#recipes)
  - [Grocery Lists](#grocery-lists)
  - [Ingredients](#ingredients)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

## Authentication

**Current Status:** Not implemented (Week 3-4)

**Future Implementation:** JWT-based authentication
- Login endpoint will return JWT token
- Include token in `Authorization` header: `Bearer <token>`
- Tokens expire after 24 hours

## Endpoints

### Health & Status

#### Check API Health

Get the current health status of the API.

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "api",
  "version": "0.1.0",
  "timestamp": "2024-02-10T15:30:00Z"
}
```

---

### Recipes

#### Generate Recipe

Generate a recipe based on available ingredients and preferences.

```http
POST /api/recipes/generate
```

**Request Body:**
```json
{
  "ingredients": "chicken, rice, garlic, onions",
  "servings": 4,
  "cuisine": "italian",
  "dietary": "gluten-free"
}
```

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ingredients` | string | Yes | Comma-separated list of ingredients |
| `servings` | integer | Yes | Number of servings (1-10) |
| `cuisine` | string | No | Preferred cuisine type |
| `dietary` | string | No | Dietary restrictions/preferences |

**Response:** (201 Created)
```json
{
  "id": "recipe_123",
  "title": "Italian Chicken and Rice",
  "description": "A delicious gluten-free Italian dish",
  "servings": 4,
  "prep_time": 15,
  "cook_time": 30,
  "total_time": 45,
  "difficulty": "medium",
  "ingredients": [
    {
      "name": "chicken breast",
      "quantity": 500,
      "unit": "g",
      "category": "protein"
    },
    {
      "name": "rice",
      "quantity": 2,
      "unit": "cups",
      "category": "grains"
    }
  ],
  "instructions": [
    {
      "step": 1,
      "description": "Preheat oven to 180°C"
    },
    {
      "step": 2,
      "description": "Season chicken with salt and pepper"
    }
  ],
  "nutrition": {
    "calories": 450,
    "protein": 35,
    "carbs": 50,
    "fat": 12
  },
  "created_at": "2024-02-10T15:30:00Z"
}
```

**Errors:**
- `400 Bad Request` - Invalid input (missing ingredients, invalid servings)
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - OpenAI API error

---

#### Get Recipe by ID

Retrieve a previously generated recipe.

```http
GET /api/recipes/{recipe_id}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `recipe_id` | string | Unique recipe identifier |

**Response:** (200 OK)
```json
{
  "id": "recipe_123",
  "title": "Italian Chicken and Rice",
  "description": "A delicious gluten-free Italian dish",
  "servings": 4,
  "ingredients": [...],
  "instructions": [...],
  "nutrition": {...}
}
```

**Errors:**
- `404 Not Found` - Recipe doesn't exist

---

#### List User Recipes

Get all recipes created by the user.

```http
GET /api/recipes
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 10 | Max recipes to return (1-50) |
| `offset` | integer | 0 | Pagination offset |
| `cuisine` | string | - | Filter by cuisine type |
| `search` | string | - | Search in recipe titles |

**Example:**
```http
GET /api/recipes?limit=20&offset=0&cuisine=italian
```

**Response:** (200 OK)
```json
{
  "recipes": [
    {
      "id": "recipe_123",
      "title": "Italian Chicken and Rice",
      "servings": 4,
      "created_at": "2024-02-10T15:30:00Z"
    }
  ],
  "total": 45,
  "limit": 20,
  "offset": 0
}
```

---

#### Delete Recipe

Delete a recipe by ID.

```http
DELETE /api/recipes/{recipe_id}
```

**Response:** (204 No Content)

**Errors:**
- `404 Not Found` - Recipe doesn't exist
- `403 Forbidden` - Not authorized to delete this recipe

---

### Grocery Lists

#### Add Recipe to Grocery List

Add a recipe's ingredients to the grocery list.

```http
POST /api/grocery-lists/add-recipe
```

**Request Body:**
```json
{
  "recipe_id": "recipe_123",
  "exclude_owned": true
}
```

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `recipe_id` | string | Yes | Recipe to add to list |
| `exclude_owned` | boolean | No | Exclude ingredients already in pantry (default: true) |

**Response:** (200 OK)
```json
{
  "grocery_list_id": "list_456",
  "items_added": [
    {
      "name": "chicken breast",
      "quantity": 500,
      "unit": "g",
      "category": "protein",
      "checked": false
    }
  ],
  "items_excluded": [
    {
      "name": "rice",
      "reason": "already_in_pantry"
    }
  ]
}
```

---

#### Get Grocery List

Retrieve the current grocery list.

```http
GET /api/grocery-lists/{list_id}
```

**Response:** (200 OK)
```json
{
  "id": "list_456",
  "created_at": "2024-02-10T15:30:00Z",
  "updated_at": "2024-02-10T16:00:00Z",
  "items": [
    {
      "id": "item_789",
      "name": "chicken breast",
      "quantity": 500,
      "unit": "g",
      "category": "protein",
      "checked": false,
      "notes": "organic preferred"
    }
  ],
  "total_items": 12,
  "checked_items": 3
}
```

---

#### Update Grocery List Item

Update an item's status or details.

```http
PATCH /api/grocery-lists/items/{item_id}
```

**Request Body:**
```json
{
  "checked": true,
  "quantity": 600,
  "notes": "bought organic"
}
```

**Response:** (200 OK)
```json
{
  "id": "item_789",
  "name": "chicken breast",
  "quantity": 600,
  "unit": "g",
  "checked": true,
  "notes": "bought organic"
}
```

---

#### Clear Checked Items

Remove all checked items from the grocery list.

```http
POST /api/grocery-lists/{list_id}/clear-checked
```

**Response:** (200 OK)
```json
{
  "items_removed": 3,
  "remaining_items": 9
}
```

---

### Ingredients

#### Add Ingredient to Pantry

Add an ingredient to the user's pantry.

```http
POST /api/ingredients
```

**Request Body:**
```json
{
  "name": "rice",
  "quantity": 2,
  "unit": "kg",
  "category": "grains",
  "expiration_date": "2024-06-01"
}
```

**Response:** (201 Created)
```json
{
  "id": "ing_101",
  "name": "rice",
  "quantity": 2,
  "unit": "kg",
  "category": "grains",
  "expiration_date": "2024-06-01",
  "added_at": "2024-02-10T15:30:00Z"
}
```

---

#### Get Pantry Ingredients

List all ingredients in the user's pantry.

```http
GET /api/ingredients
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | Filter by category |
| `expiring_soon` | boolean | Only show items expiring within 7 days |

**Response:** (200 OK)
```json
{
  "ingredients": [
    {
      "id": "ing_101",
      "name": "rice",
      "quantity": 2,
      "unit": "kg",
      "category": "grains",
      "expiration_date": "2024-06-01"
    }
  ],
  "total": 15,
  "categories": ["protein", "grains", "vegetables", "dairy"]
}
```

---

#### Update Ingredient

Update ingredient quantity or details.

```http
PATCH /api/ingredients/{ingredient_id}
```

**Request Body:**
```json
{
  "quantity": 1.5,
  "expiration_date": "2024-07-01"
}
```

**Response:** (200 OK)
```json
{
  "id": "ing_101",
  "name": "rice",
  "quantity": 1.5,
  "unit": "kg",
  "expiration_date": "2024-07-01"
}
```

---

#### Delete Ingredient

Remove an ingredient from pantry.

```http
DELETE /api/ingredients/{ingredient_id}
```

**Response:** (204 No Content)

---

## Data Models

### Recipe

```typescript
interface Recipe {
  id: string
  title: string
  description: string
  servings: number
  prep_time: number          // minutes
  cook_time: number          // minutes
  total_time: number         // minutes
  difficulty: "easy" | "medium" | "hard"
  cuisine: string
  ingredients: Ingredient[]
  instructions: Step[]
  nutrition: NutritionInfo
  created_at: string         // ISO 8601 datetime
  updated_at: string         // ISO 8601 datetime
}
```

### Ingredient

```typescript
interface Ingredient {
  id?: string
  name: string
  quantity: number
  unit: string               // "g", "kg", "ml", "l", "cups", "tbsp", "tsp", "pieces"
  category: string           // "protein", "grains", "vegetables", "dairy", "spices"
  expiration_date?: string   // ISO 8601 date
  notes?: string
}
```

### Step

```typescript
interface Step {
  step: number
  description: string
  duration?: number          // minutes
  temperature?: number       // celsius
}
```

### NutritionInfo

```typescript
interface NutritionInfo {
  calories: number           // per serving
  protein: number            // grams
  carbs: number             // grams
  fat: number               // grams
  fiber?: number            // grams
  sugar?: number            // grams
  sodium?: number           // mg
}
```

### GroceryList

```typescript
interface GroceryList {
  id: string
  user_id: string
  items: GroceryItem[]
  total_items: number
  checked_items: number
  created_at: string
  updated_at: string
}
```

### GroceryItem

```typescript
interface GroceryItem {
  id: string
  name: string
  quantity: number
  unit: string
  category: string
  checked: boolean
  notes?: string
  recipe_id?: string         // If added from a recipe
}
```

---

## Error Handling

### Error Response Format

All errors follow this structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "field_name",
      "issue": "specific issue description"
    }
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `NOT_FOUND` | 404 | Resource doesn't exist |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `OPENAI_ERROR` | 500 | AI service error |
| `DATABASE_ERROR` | 500 | Database error |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

### Example Error Responses

**Validation Error:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid servings value",
    "details": {
      "field": "servings",
      "issue": "Servings must be between 1 and 10"
    }
  }
}
```

**Not Found:**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Recipe not found",
    "details": {
      "recipe_id": "recipe_999"
    }
  }
}
```

**Rate Limit:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many recipe generation requests",
    "details": {
      "retry_after": 60,
      "limit": "10 requests per minute"
    }
  }
}
```

---

## Rate Limiting

**Current Limits:**
- Recipe generation: 10 requests per minute per user
- Other endpoints: 100 requests per minute per user

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1707579600
```

When rate limit is exceeded, wait for the time specified in `X-RateLimit-Reset` (Unix timestamp).

---

## Request Examples

### Generate Italian Recipe

```bash
curl -X POST http://localhost:8000/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": "pasta, tomatoes, garlic, olive oil, basil",
    "servings": 2,
    "cuisine": "italian",
    "dietary": "vegetarian"
  }'
```

### Add Recipe to Grocery List

```bash
curl -X POST http://localhost:8000/api/grocery-lists/add-recipe \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_id": "recipe_123",
    "exclude_owned": true
  }'
```

### Get Pantry Ingredients

```bash
curl -X GET "http://localhost:8000/api/ingredients?category=protein"
```

---

## Pagination

For list endpoints that support pagination:

**Request:**
```http
GET /api/recipes?limit=20&offset=40
```

**Response includes:**
```json
{
  "recipes": [...],
  "total": 156,
  "limit": 20,
  "offset": 40,
  "has_more": true
}
```

**Pagination Parameters:**
- `limit` - Number of items per page (max: 50)
- `offset` - Number of items to skip

**Calculate pages:**
- Page 1: `offset=0`, `limit=20`
- Page 2: `offset=20`, `limit=20`
- Page 3: `offset=40`, `limit=20`

---

## Versioning

**Current Version:** v0.1.0

API version is included in response headers:
```http
X-API-Version: 0.1.0
```

Future versions will use URL versioning:
```
/v2/api/recipes/generate
```

---

## Development vs Production

### Development (localhost:8000)
- Verbose error messages
- Detailed stack traces
- No rate limiting
- CORS enabled for all origins

### Production (TBD)
- Generic error messages
- Errors logged server-side
- Strict rate limiting
- CORS limited to approved domains
- HTTPS required

---

## WebSocket Support (Future)

For real-time features like collaborative grocery lists:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/grocery-list/list_456')

ws.onmessage = (event) => {
  const update = JSON.parse(event.data)
  console.log('Grocery list updated:', update)
}
```

---

## Testing the API

### Using the Frontend Test Tools

The Vue frontend includes a "Backend Connection Test" section:
1. Open http://localhost:3000
2. Expand "Backend Connection Test"
3. Click "Test Health Endpoint"

### Using curl

```bash
# Health check
curl http://localhost:8000/api/health

# Generate recipe
curl -X POST http://localhost:8000/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{"ingredients": "chicken, rice", "servings": 2}'
```

### Using Postman

1. Import the Postman collection (TBD)
2. Set environment variable `BASE_URL=http://localhost:8000`
3. Run requests from collection

---

## Changelog

### v0.1.0 (Week 3-4)
- Initial API setup
- Health check endpoints
- Recipe generation endpoint (planned)
- Basic CORS configuration

### v0.2.0 (Week 5) - Planned
- Grocery list endpoints
- Ingredient management
- User pantry functionality

### v0.3.0 (Week 6) - Planned
- User authentication
- Recipe saving and favorites
- Search functionality

---

## Support

For API issues or questions:
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check integration guide and architecture docs
- **Team Channel**: Ask in Slack/Discord #api-help

---

## Conclusion

This API provides a comprehensive interface for managing recipes, grocery lists, and ingredients. All endpoints follow RESTful conventions and return consistent JSON responses. See the Integration Guide for detailed implementation examples.
