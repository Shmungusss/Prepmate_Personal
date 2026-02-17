# PrepMate System Architecture

## Overview

PrepMate is a full-stack web application that helps users generate recipes based on available ingredients and create grocery lists. The system uses AI to intelligently generate recipes and manage ingredient inventories.

## Technology Stack

### Frontend
- **Framework**: Vue.js 3 (Composition API)
- **Build Tool**: Vite
- **Routing**: Vue Router 4
- **Styling**: Scoped CSS
- **HTTP Client**: Fetch API
- **Port**: 3000 (development)

### Backend
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn (ASGI)
- **Database**: TBD (Week 4 - recommend PostgreSQL)
- **AI Integration**: OpenAI API
- **Port**: 8000 (development)

### External Services
- **AI Provider**: OpenAI GPT-4
- **Database**: PostgreSQL (planned)

## High-Level Architecture

```mermaid
graph TB
    User[User Browser] --> Frontend[Vue.js Frontend<br/>Port 3000]
    Frontend --> Backend[FastAPI Backend<br/>Port 8000]
    Backend --> DB[(Database<br/>PostgreSQL)]
    Backend --> OpenAI[OpenAI API<br/>GPT-4]
    Backend --> Cache[Redis Cache<br/>Optional]
    
    style User fill:#e1f5ff
    style Frontend fill:#4fc3f7
    style Backend fill:#66bb6a
    style DB fill:#ffa726
    style OpenAI fill:#ab47bc
    style Cache fill:#ffca28
```

## Detailed System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
        Router[Vue Router]
        Components[Vue Components]
        Services[API Services]
    end
    
    subgraph "API Layer"
        CORS[CORS Middleware]
        Routes[API Routes]
        Controllers[Request Handlers]
        Validation[Input Validation]
    end
    
    subgraph "Business Logic Layer"
        RecipeService[Recipe Service]
        GroceryService[Grocery List Service]
        IngredientService[Ingredient Service]
        UserService[User Service]
        AIService[AI Integration Service]
    end
    
    subgraph "Data Layer"
        ORM[Database ORM]
        Cache[Cache Layer]
        DB[(PostgreSQL)]
    end
    
    subgraph "External Services"
        OpenAI[OpenAI API]
    end
    
    Browser --> Router
    Router --> Components
    Components --> Services
    Services --> CORS
    CORS --> Routes
    Routes --> Controllers
    Controllers --> Validation
    Validation --> RecipeService
    Validation --> GroceryService
    Validation --> IngredientService
    Validation --> UserService
    
    RecipeService --> AIService
    RecipeService --> ORM
    GroceryService --> ORM
    IngredientService --> ORM
    UserService --> ORM
    
    AIService --> OpenAI
    ORM --> Cache
    ORM --> DB
    
    style Browser fill:#e1f5ff
    style OpenAI fill:#ab47bc
    style DB fill:#ffa726
```

## Component Interaction Flow

### Recipe Generation Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant OpenAI
    participant Database
    
    User->>Frontend: Fill recipe form<br/>(ingredients, servings, etc.)
    User->>Frontend: Click "Generate Recipe"
    Frontend->>Frontend: Validate input
    Frontend->>Backend: POST /api/recipes/generate
    Backend->>Backend: Validate request
    Backend->>OpenAI: Generate recipe prompt
    OpenAI-->>Backend: Recipe JSON
    Backend->>Database: Save recipe
    Database-->>Backend: Recipe ID
    Backend-->>Frontend: Recipe response
    Frontend->>User: Display recipe
```

### Grocery List Generation Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Database
    
    User->>Frontend: View recipe
    User->>Frontend: Click "Add to Grocery List"
    Frontend->>Backend: POST /api/grocery-lists/add-recipe
    Backend->>Database: Get recipe ingredients
    Database-->>Backend: Ingredient list
    Backend->>Database: Check user pantry
    Database-->>Backend: Available ingredients
    Backend->>Backend: Calculate missing items
    Backend->>Database: Create/update grocery list
    Database-->>Backend: Grocery list ID
    Backend-->>Frontend: Grocery list response
    Frontend->>User: Display grocery list
```

## Data Flow Architecture

```mermaid
graph LR
    subgraph "Frontend State"
        FormData[Form Data]
        RecipeData[Recipe Data]
        GroceryData[Grocery List Data]
    end
    
    subgraph "API Layer"
        Request[HTTP Request]
        Response[HTTP Response]
    end
    
    subgraph "Backend Processing"
        Validation[Validation]
        BusinessLogic[Business Logic]
        AIProcessing[AI Processing]
    end
    
    subgraph "Data Storage"
        Database[(Database)]
        Cache[(Cache)]
    end
    
    FormData --> Request
    Request --> Validation
    Validation --> BusinessLogic
    BusinessLogic --> AIProcessing
    BusinessLogic --> Database
    BusinessLogic --> Cache
    Database --> BusinessLogic
    Cache --> BusinessLogic
    BusinessLogic --> Response
    Response --> RecipeData
    Response --> GroceryData
    
    style FormData fill:#e1f5ff
    style RecipeData fill:#e1f5ff
    style GroceryData fill:#e1f5ff
    style Database fill:#ffa726
    style Cache fill:#ffca28
```

## Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        HTTPS[HTTPS/TLS]
        CORS[CORS Policy]
        Auth[Authentication]
        Valid[Input Validation]
        Sanitize[Data Sanitization]
        RateLimit[Rate Limiting]
    end
    
    subgraph "API Gateway"
        Gateway[API Gateway]
    end
    
    subgraph "Backend Services"
        Services[Business Logic]
    end
    
    Client[Client] --> HTTPS
    HTTPS --> CORS
    CORS --> Gateway
    Gateway --> Auth
    Auth --> Valid
    Valid --> Sanitize
    Sanitize --> RateLimit
    RateLimit --> Services
    
    style Client fill:#e1f5ff
    style HTTPS fill:#66bb6a
    style Auth fill:#ff7043
```

## Deployment Architecture (Future)

```mermaid
graph TB
    subgraph "Production Environment"
        LB[Load Balancer]
        FE1[Frontend Instance 1]
        FE2[Frontend Instance 2]
        BE1[Backend Instance 1]
        BE2[Backend Instance 2]
        DB[(Primary DB)]
        DBR[(Read Replica)]
        Redis[(Redis Cache)]
    end
    
    subgraph "External"
        CDN[CDN]
        OpenAI[OpenAI API]
    end
    
    Users[Users] --> CDN
    CDN --> LB
    LB --> FE1
    LB --> FE2
    FE1 --> BE1
    FE1 --> BE2
    FE2 --> BE1
    FE2 --> BE2
    BE1 --> DB
    BE1 --> DBR
    BE1 --> Redis
    BE2 --> DB
    BE2 --> DBR
    BE2 --> Redis
    BE1 --> OpenAI
    BE2 --> OpenAI
    
    style Users fill:#e1f5ff
    style CDN fill:#4fc3f7
    style DB fill:#ffa726
    style OpenAI fill:#ab47bc
```

## Key Architectural Decisions

### 1. Separation of Concerns
- **Frontend**: Handles UI/UX, user interactions, and presentation logic
- **Backend**: Manages business logic, data persistence, and external API integrations
- **Database**: Stores persistent data with proper relationships

### 2. RESTful API Design
- Clear resource-based endpoints
- Standard HTTP methods (GET, POST, PUT, DELETE)
- JSON for data exchange
- Stateless communication

### 3. AI Integration Strategy
- Backend handles all AI API calls (keeps API keys secure)
- Caching of common recipe requests to reduce costs
- Fallback mechanisms if AI service is unavailable

### 4. Scalability Considerations
- Stateless backend design for horizontal scaling
- Database connection pooling
- Caching layer for frequently accessed data
- Async processing for long-running tasks

### 5. Security Best Practices
- CORS configuration for frontend-backend communication
- Input validation on both frontend and backend
- Environment variables for sensitive configuration
- API rate limiting to prevent abuse

## Performance Optimization

### Frontend
- Component lazy loading
- Code splitting with Vite
- Image optimization
- Local state management to reduce API calls

### Backend
- Database query optimization
- Response caching
- Async/await for non-blocking operations
- Connection pooling

### Database
- Proper indexing on frequently queried fields
- Query optimization
- Read replicas for scaling reads

## Monitoring & Logging (Future)

```mermaid
graph LR
    App[Application] --> Logs[Logging Service]
    App --> Metrics[Metrics Collection]
    App --> Errors[Error Tracking]
    
    Logs --> Dashboard[Monitoring Dashboard]
    Metrics --> Dashboard
    Errors --> Dashboard
    
    Dashboard --> Alerts[Alert System]
    
    style App fill:#4fc3f7
    style Dashboard fill:#66bb6a
    style Alerts fill:#ff7043
```

## Technology Choices Rationale

### Why Vue.js?
- Gentle learning curve
- Excellent documentation
- Composition API for better code organization
- Strong ecosystem with Vue Router and Vite

### Why FastAPI?
- High performance (based on Starlette/Pydantic)
- Automatic API documentation (Swagger/OpenAPI)
- Type hints for better code quality
- Async support for concurrent requests
- Easy integration with Python AI libraries

### Why PostgreSQL? (Planned)
- Robust relational database
- ACID compliance
- JSON support for flexible data
- Strong community and tooling
- Free and open source

### Why OpenAI?
- State-of-the-art language models
- Reliable API with good documentation
- Structured output capabilities
- Cost-effective for recipe generation
- Easy integration

## Future Enhancements

1. **User Authentication**: JWT-based authentication system
2. **Real-time Updates**: WebSocket support for collaborative features
3. **Mobile Apps**: React Native or Flutter mobile applications
4. **Analytics**: User behavior tracking and recipe popularity metrics
5. **Social Features**: Recipe sharing and community ratings
6. **Search**: Full-text search for recipes and ingredients
7. **Notifications**: Email/push notifications for grocery reminders

## Conclusion

This architecture provides a solid foundation for PrepMate, with clear separation of concerns, scalability in mind, and room for future growth. The tech stack choices balance developer productivity, performance, and maintainability.
