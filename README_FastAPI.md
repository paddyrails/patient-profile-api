# FastAPI Interview Guide — 30 Questions with Detailed Answers

> **Python Web Framework** | FastAPI + Pydantic + SQLAlchemy | Covering fundamentals, routing, validation, DI, database, security, testing, and deployment

---

## Table of Contents

- [Section 1: Questions](#section-1-questions)
- [Section 2: Questions & Answers](#section-2-questions--answers)
- [Section 3: Implementation Tracker](#section-3-implementation-tracker)

---

## Section 1: Questions

| #   | Category              | Question                                                                                  |
| --- | --------------------- | ----------------------------------------------------------------------------------------- |
| 1   | Fundamentals          | What is FastAPI and what makes it different from Flask and Django REST Framework?         |
| 2   | Fundamentals          | FastAPI is built on top of two key libraries. What are they and what role does each play? |
| 3   | Fundamentals          | What is the difference between `def` and `async def` for route handlers in FastAPI?       |
| 4   | Fundamentals          | How does FastAPI automatically generate interactive API documentation?                    |
| 5   | Fundamentals          | How do Python type hints power FastAPI's validation, serialization, and documentation?    |
| 6   | Fundamentals          | What is ASGI and how does it differ from WSGI?                                            |
| 7   | Routing               | What is the difference between path parameters, query parameters, and request body?       |
| 8   | Routing               | How does FastAPI handle request validation errors?                                        |
| 9   | Routing               | What is an `APIRouter` and how do you organize a large application?                       |
| 10  | Routing               | How do you handle file uploads in FastAPI?                                                |
| 11  | Routing               | How do you implement API versioning in FastAPI?                                           |
| 12  | Routing               | How do you return different HTTP status codes and custom headers?                         |
| 13  | Pydantic              | What is the difference between Pydantic `BaseModel` and SQLAlchemy ORM model?             |
| 14  | Pydantic              | How do you create separate schemas for Create, Update, and Response?                      |
| 15  | Pydantic              | How do you add custom validation logic in a Pydantic model?                               |
| 16  | Pydantic              | What is `from_attributes=True` and why is it needed?                                      |
| 17  | Pydantic              | How does FastAPI handle nested Pydantic models?                                           |
| 18  | Dependency Injection  | Explain FastAPI's dependency injection with `Depends()`.                                  |
| 19  | Dependency Injection  | How do you create a `get_db` dependency for database sessions?                            |
| 20  | Dependency Injection  | How do you implement `get_current_user` authentication dependency?                        |
| 21  | Dependency Injection  | What is the difference between a dependency with `yield` and a regular dependency?        |
| 22  | Database              | Walk through setting up SQLAlchemy with FastAPI.                                          |
| 23  | Database              | What is Alembic and how do you use it for migrations?                                     |
| 24  | Database              | How do you use async database access in FastAPI?                                          |
| 25  | Middleware & Security | What is middleware in FastAPI? Write a request logging example.                           |
| 26  | Middleware & Security | How would you implement rate limiting?                                                    |
| 27  | Middleware & Security | How do you secure FastAPI with OAuth2 and JWT?                                            |
| 28  | Middleware & Security | How does FastAPI handle CORS?                                                             |
| 29  | Testing & Deployment  | How do you write tests and override dependencies?                                         |
| 30  | Testing & Deployment  | Design a production deployment for 10K requests/second.                                   |

---

## Section 2: Questions & Answers

---

### Q1. What is FastAPI and what makes it different from Flask and Django REST Framework?

**Answer:** FastAPI is a modern, high-performance Python web framework for building APIs. It's built on Starlette (for the web layer) and Pydantic (for data validation), using Python type hints to provide automatic validation, serialization, and documentation.

| Feature            | Flask                            | Django REST Framework        | FastAPI                                              |
| ------------------ | -------------------------------- | ---------------------------- | ---------------------------------------------------- |
| **Performance**    | Moderate (WSGI)                  | Moderate (WSGI)              | Very fast (ASGI, async-native)                       |
| **Type Hints**     | Optional, no framework use       | Optional, no framework use   | Core to everything — validation, docs, serialization |
| **Validation**     | Manual or Flask-Marshmallow      | Serializers (manual)         | Automatic via Pydantic                               |
| **API Docs**       | Swagger via extension            | Browsable API built-in       | Swagger + ReDoc auto-generated                       |
| **Async Support**  | Limited (Flask 2.0+)             | Limited                      | Native async/await                                   |
| **Learning Curve** | Low                              | High (Django ecosystem)      | Low-Medium                                           |
| **Ecosystem**      | Massive (extensions)             | Massive (Django batteries)   | Growing, Python standard libs                        |
| **Best For**       | Small-medium apps, microservices | Full-featured web apps + API | High-performance APIs, microservices                 |

```python
# Flask — manual validation, no type hints
@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = db.get(order_id)
    if not order:
        return jsonify({"error": "Not found"}), 404
    return jsonify(order.to_dict())

# FastAPI — type hints drive everything
@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Not found")
    return order
    # Validation, serialization, documentation — all automatic
```

---

### Q2. FastAPI is built on top of two key libraries. What are they and what role does each play?

**Answer:**

**Starlette** — the web framework foundation. It provides the HTTP handling, routing, WebSocket support, middleware, CORS, sessions, static files, and the `TestClient`. FastAPI is literally a subclass of Starlette's application class. Starlette handles the ASGI protocol and async request/response cycle.

**Pydantic** — the data validation and serialization layer. It provides `BaseModel` for defining request/response schemas with type hints, automatic validation with detailed error messages, JSON serialization/deserialization, and settings management via `BaseSettings`. Pydantic is what makes the "type hints → validation → docs" magic possible.

```python
from fastapi import FastAPI        # built on Starlette
from pydantic import BaseModel     # data validation

class OrderCreate(BaseModel):      # Pydantic handles validation
    merchant_id: str
    total: float
    items: list[str]

app = FastAPI()                    # Starlette handles HTTP

@app.post("/orders")
async def create_order(order: OrderCreate):  # Pydantic validates the body
    return {"status": "created", "merchant": order.merchant_id}
```

There's also **Uvicorn** which is the standard ASGI server used to run FastAPI applications, but it's not a dependency of FastAPI itself — it's the runtime.

---

### Q3. What is the difference between `def` and `async def` for route handlers in FastAPI?

**Answer:** FastAPI handles both, but they execute differently under the hood:

**`async def`** — runs directly on the async event loop. The function must use `await` for any I/O operations. If you call blocking code inside an `async def` without await, you'll freeze the entire event loop and block all other requests.

**`def`** (synchronous) — FastAPI automatically runs it in a **threadpool** (`anyio.to_thread`), so it won't block the event loop. This is safe for blocking I/O like synchronous database drivers.

```python
# CORRECT — async with async I/O
@app.get("/orders/{id}")
async def get_order(id: int):
    order = await async_db.fetch_one("SELECT * FROM orders WHERE id = $1", id)
    return order  # non-blocking, event loop stays free

# CORRECT — sync function, FastAPI runs it in threadpool automatically
@app.get("/orders/{id}")
def get_order(id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    return order  # blocking, but safe because it's in a threadpool

# WRONG — blocking call inside async def
@app.get("/orders/{id}")
async def get_order(id: int):
    order = db.query(Order).filter(Order.id == id).first()  # BLOCKS EVENT LOOP!
    return order  # all other requests freeze while this runs
```

**Rule of thumb:** Use `async def` when you have truly async libraries (asyncpg, httpx, aioredis). Use plain `def` when you're using synchronous libraries (SQLAlchemy sync, requests). Never mix blocking calls inside `async def`.

---

### Q4. How does FastAPI automatically generate interactive API documentation?

**Answer:** FastAPI generates an OpenAPI schema (JSON) from your route definitions, type hints, Pydantic models, and docstrings. It then serves two interactive UIs that consume this schema:

- **Swagger UI** at `/docs` — interactive, lets you try requests directly from the browser
- **ReDoc** at `/redoc` — read-only, better for documentation browsing

```python
from fastapi import FastAPI

app = FastAPI(
    title="POS Customer Support API",
    description="API for merchant onboarding, orders, and case management",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI (default)
    redoc_url="/redoc",     # ReDoc (default)
    openapi_url="/openapi.json"  # raw OpenAPI schema
)

@app.get("/orders/{order_id}",
    summary="Get order by ID",
    description="Retrieves a single order with all line items and status history.",
    response_description="The order object",
    tags=["Orders"],
    responses={
        404: {"description": "Order not found"},
        403: {"description": "Not authorized to view this order"}
    }
)
async def get_order(order_id: int) -> OrderResponse:
    """
    Fetch a specific order by its unique identifier.

    - **order_id**: The unique order ID (auto-generated at checkout)
    """
    ...
```

Everything — path params, query params, request body schema, response model, status codes, tags, descriptions — is extracted from your Python code and type hints. No separate YAML or annotation files needed.

---

### Q5. How do Python type hints power FastAPI's validation, serialization, and documentation?

**Answer:** A single type-hinted function signature does three jobs simultaneously:

```python
from pydantic import BaseModel, Field
from typing import Optional

class OrderCreate(BaseModel):
    merchant_id: str = Field(..., min_length=3, max_length=50)
    total: float = Field(..., gt=0, description="Order total in USD")
    items: list[str] = Field(..., min_length=1)
    notes: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    merchant_id: str
    total: float
    status: str
    model_config = ConfigDict(from_attributes=True)

@app.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(
    order: OrderCreate,                    # ← REQUEST BODY validated by Pydantic
    priority: int = Query(default=1, ge=1, le=5),  # ← QUERY PARAM validated
    db: Session = Depends(get_db),         # ← DEPENDENCY injected
) -> OrderResponse:
    ...
```

**Validation:** When a request arrives, FastAPI uses Pydantic to validate the body against `OrderCreate`. If `total` is negative or `items` is empty, it returns a 422 with specific error details — automatically.

**Serialization:** The return value is filtered through `OrderResponse` — only fields defined in the response model are included. Database fields like `password_hash` are excluded automatically.

**Documentation:** The OpenAPI schema includes the full `OrderCreate` schema (with field types, constraints, descriptions), `OrderResponse` schema, query parameter `priority` with its range, and example values — all generated from the type hints.

---

### Q6. What is ASGI and how does it differ from WSGI?

**Answer:**

**WSGI (Web Server Gateway Interface)** — the traditional Python web standard (PEP 3333). It's synchronous and handles one request per thread. Flask and Django use WSGI. Each request blocks a thread until complete.

**ASGI (Asynchronous Server Gateway Interface)** — the async evolution of WSGI. It supports async/await, WebSockets, HTTP/2, long-polling, and server-sent events. A single process can handle thousands of concurrent connections using an event loop.

```
WSGI (Flask/Django):
Request 1 ──→ Thread 1 ──[blocked on DB]──────→ Response 1
Request 2 ──→ Thread 2 ──[blocked on API call]─→ Response 2
Request 3 ──→ Thread 3 ──[blocked on file I/O]─→ Response 3
(Need 1 thread per concurrent request)

ASGI (FastAPI/Starlette):
Request 1 ──→ ┐
Request 2 ──→ ├── Event Loop (single thread handles all)
Request 3 ──→ ┘
               │
               ├── await db_query()      → suspended, loop handles other requests
               ├── await api_call()      → suspended, loop handles other requests
               └── await file_read()     → suspended, loop handles other requests
(Thousands of concurrent requests on few threads)
```

FastAPI uses ASGI because it enables: non-blocking I/O (one process handles thousands of connections), WebSocket support (real-time features), background tasks, and significantly higher throughput for I/O-bound workloads. The standard ASGI server for FastAPI is **Uvicorn** (based on uvloop).

---

### Q7. What is the difference between path parameters, query parameters, and request body?

**Answer:**

```python
from fastapi import FastAPI, Query, Path, Body
from pydantic import BaseModel

class OrderUpdate(BaseModel):
    status: str
    notes: str | None = None

@app.put("/merchants/{merchant_id}/orders/{order_id}")
async def update_order(
    # PATH PARAMETERS — part of the URL path, always required
    merchant_id: str = Path(..., description="The merchant's unique ID"),
    order_id: int = Path(..., gt=0, description="The order's unique ID"),

    # QUERY PARAMETERS — after ? in URL, can be optional
    notify: bool = Query(default=False, description="Send notification email"),
    reason: str = Query(default=None, max_length=200),

    # REQUEST BODY — JSON payload, validated by Pydantic model
    order_data: OrderUpdate = Body(...),
):
    ...

# Called as:
# PUT /merchants/M-001/orders/42?notify=true&reason=customer+request
# Body: {"status": "shipped", "notes": "Expedited shipping"}
```

| Type      | Location                            | Required?                     | Use For                        |
| --------- | ----------------------------------- | ----------------------------- | ------------------------------ |
| **Path**  | In URL path `/items/{id}`           | Always required               | Resource identification        |
| **Query** | After `?` in URL `?page=2&limit=10` | Can be optional with defaults | Filtering, sorting, pagination |
| **Body**  | JSON in request body                | Depends on Pydantic model     | Creating/updating resources    |

FastAPI determines parameter type by how it's declared: if the name matches a path placeholder `{name}` → path param. If it's a simple type (str, int, float, bool) and not in path → query param. If it's a Pydantic `BaseModel` → body.

---

### Q8. How does FastAPI handle request validation errors?

**Answer:** When validation fails, FastAPI returns a **422 Unprocessable Entity** response with a detailed JSON body listing every validation error, the field location, and the error message.

```python
class OrderCreate(BaseModel):
    merchant_id: str = Field(..., min_length=3)
    total: float = Field(..., gt=0)
    items: list[str] = Field(..., min_length=1)

# If client sends: {"merchant_id": "AB", "total": -5, "items": []}
# FastAPI returns 422:
{
    "detail": [
        {
            "type": "string_too_short",
            "loc": ["body", "merchant_id"],
            "msg": "String should have at least 3 characters",
            "input": "AB",
            "ctx": {"min_length": 3}
        },
        {
            "type": "greater_than",
            "loc": ["body", "total"],
            "msg": "Input should be greater than 0",
            "input": -5,
            "ctx": {"gt": 0}
        },
        {
            "type": "too_short",
            "loc": ["body", "items"],
            "msg": "List should have at least 1 item after validation",
            "input": []
        }
    ]
}
```

You can customize validation error responses by overriding the exception handler:

```python
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def custom_validation_handler(request: Request, exc: RequestValidationError):
    errors = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])
        errors[field] = error["msg"]
    return JSONResponse(
        status_code=422,
        content={"error": "Validation failed", "fields": errors}
    )
```

---

### Q9. What is an `APIRouter` and how do you organize a large application?

**Answer:** `APIRouter` is FastAPI's way of splitting your application into modular, reusable route groups — like Flask's `Blueprint`. Each router handles a domain (orders, merchants, cases), and they're assembled in `main.py`.

```python
# app/api/v1/endpoints/orders.py
from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    dependencies=[Depends(get_current_user)],  # auth for all routes in this router
    responses={401: {"description": "Not authenticated"}},
)

@router.get("/")
async def list_orders(): ...

@router.get("/{order_id}")
async def get_order(order_id: int): ...

@router.post("/", status_code=201)
async def create_order(order: OrderCreate): ...
```

```python
# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import orders, merchants, cases, products, auth

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(orders.router)
api_router.include_router(merchants.router)
api_router.include_router(products.router)
api_router.include_router(cases.router)
```

```python
# app/main.py
from fastapi import FastAPI
from app.api.v1.router import api_router

app = FastAPI(title="POS Customer Support API")
app.include_router(api_router, prefix="/api/v1")
```

This gives you clean URLs like `/api/v1/orders`, `/api/v1/merchants`, with each module in its own file, own dependencies, and own tags in the Swagger docs.

---

### Q10. How do you handle file uploads in FastAPI?

**Answer:** FastAPI provides `File` and `UploadFile` for handling file uploads via multipart form data.

```python
from fastapi import UploadFile, File

# UploadFile — preferred for large files (spooled to disk, async read)
@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(..., description="The document to upload"),
    merchant_id: str = Form(...),
):
    contents = await file.read()  # async read
    file_size = len(contents)

    # Save to disk or cloud storage
    save_path = f"/uploads/{merchant_id}/{file.filename}"
    with open(save_path, "wb") as f:
        f.write(contents)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": file_size,
    }

# Multiple file upload
@app.post("/documents/bulk-upload")
async def bulk_upload(files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        contents = await file.read()
        results.append({"name": file.filename, "size": len(contents)})
    return {"uploaded": results}
```

**`File` vs `UploadFile`:**

| Feature           | `File(...)`           | `UploadFile`                          |
| ----------------- | --------------------- | ------------------------------------- |
| **Type received** | Raw `bytes`           | SpooledTemporaryFile object           |
| **Memory**        | Entire file in memory | Spooled to disk beyond threshold      |
| **Large files**   | Bad (memory hog)      | Good (stream from disk)               |
| **Async**         | No                    | Yes (`await file.read()`)             |
| **Metadata**      | No                    | `.filename`, `.content_type`, `.size` |

Always use `UploadFile` for production applications.

---

### Q11. How do you implement API versioning in FastAPI?

**Answer:** The most common approach is URL-prefix versioning using `APIRouter`:

```python
# app/api/v1/endpoints/orders.py
from fastapi import APIRouter
router = APIRouter(prefix="/orders", tags=["Orders v1"])

@router.get("/{order_id}")
async def get_order_v1(order_id: int):
    return {"version": "v1", "order_id": order_id, "format": "legacy"}

# app/api/v2/endpoints/orders.py
from fastapi import APIRouter
router = APIRouter(prefix="/orders", tags=["Orders v2"])

@router.get("/{order_id}")
async def get_order_v2(order_id: int):
    return {"version": "v2", "order_id": order_id, "format": "new_format", "includes_items": True}

# app/main.py
from app.api.v1.router import api_v1_router
from app.api.v2.router import api_v2_router

app = FastAPI()
app.include_router(api_v1_router, prefix="/api/v1")
app.include_router(api_v2_router, prefix="/api/v2")

# Result:
# GET /api/v1/orders/42 → v1 handler
# GET /api/v2/orders/42 → v2 handler
```

Other approaches include header-based versioning (`Accept: application/vnd.posapp.v2+json`) and query-param versioning (`/orders/42?version=2`), but URL-prefix is the industry standard because it's explicit, cacheable, and works with any HTTP client.

---

### Q12. How do you return different HTTP status codes and custom headers?

**Answer:**

```python
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse

# Method 1: Default status code on decorator
@app.post("/orders", status_code=201)
async def create_order(order: OrderCreate):
    return {"id": 1, "status": "created"}
# Returns 201 Created

# Method 2: HTTPException for error codes
@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    order = db.get(order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
            headers={"X-Error-Code": "ORDER_NOT_FOUND"}
        )
    return order

# Method 3: Response parameter for custom headers
@app.get("/orders/{order_id}")
async def get_order(order_id: int, response: Response):
    response.headers["X-Request-ID"] = "req-abc-123"
    response.headers["Cache-Control"] = "max-age=60"
    return {"order_id": order_id}

# Method 4: Return JSONResponse directly for full control
@app.post("/orders")
async def create_order(order: OrderCreate):
    new_order = save_order(order)
    return JSONResponse(
        status_code=201,
        content={"id": new_order.id, "status": "created"},
        headers={
            "Location": f"/api/v1/orders/{new_order.id}",
            "X-Order-Id": str(new_order.id)
        }
    )
```

---

### Q13. What is the difference between Pydantic `BaseModel` and SQLAlchemy ORM model?

**Answer:** They serve completely different purposes despite both being called "models."

**SQLAlchemy model** = database table definition. Maps Python classes to database rows. Handles queries, relationships, migrations.

**Pydantic model** = data shape/contract. Validates incoming data, serializes outgoing data, generates API docs.

```python
# SQLAlchemy model — defines the DATABASE TABLE
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.db.base import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, server_default=func.now())
    # This defines what's stored in PostgreSQL

# Pydantic models — define the API CONTRACT
from pydantic import BaseModel, ConfigDict

class OrderCreate(BaseModel):
    merchant_id: str
    total: float
    items: list[str]
    # This defines what the CLIENT sends (no id, no created_at)

class OrderResponse(BaseModel):
    id: int
    merchant_id: str
    total: float
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
    # This defines what the CLIENT receives (no items list)
```

You need **both** because: the client shouldn't see internal DB fields (like password hashes), the client shouldn't set server-controlled fields (like id, created_at), create and update operations need different fields, and Pydantic handles validation that doesn't belong in the database layer.

---

### Q14. How do you create separate schemas for Create, Update, and Response?

**Answer:** This pattern prevents clients from setting fields they shouldn't, and keeps response payloads clean.

```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

# Base — shared fields
class MerchantBase(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=100)
    business_type: str
    email: str
    phone: str

# Create — what the client sends to POST /merchants
class MerchantCreate(MerchantBase):
    tax_id: str = Field(..., pattern=r"^\d{2}-\d{7}$")
    # Client provides all base fields + tax_id
    # No id, no status, no created_at — server sets these

# Update — what the client sends to PATCH /merchants/{id}
class MerchantUpdate(BaseModel):
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    # ALL fields optional — partial update (PATCH semantics)
    # Can't update tax_id or id

# Response — what the client receives
class MerchantResponse(MerchantBase):
    id: int
    tax_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
    # Includes server-generated fields
    # Excludes sensitive internal fields

# Usage in endpoint:
@router.post("/", response_model=MerchantResponse, status_code=201)
async def create_merchant(merchant: MerchantCreate, db: Session = Depends(get_db)):
    db_merchant = Merchant(**merchant.model_dump())
    db.add(db_merchant)
    db.commit()
    db.refresh(db_merchant)
    return db_merchant  # Pydantic filters through MerchantResponse automatically
```

---

### Q15. How do you add custom validation logic in a Pydantic model?

**Answer:** Pydantic v2 provides `field_validator` for per-field validation and `model_validator` for cross-field validation.

```python
from pydantic import BaseModel, field_validator, model_validator
import re

class MerchantCreate(BaseModel):
    business_name: str
    email: str
    phone: str
    password: str
    password_confirm: str

    # Per-field validation
    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower().strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        cleaned = re.sub(r"[^\d+]", "", v)
        if len(cleaned) < 10:
            raise ValueError("Phone number must have at least 10 digits")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain a digit")
        return v

    # Cross-field validation (runs after all field validators)
    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self
```

You can also use `Field` with built-in constraints for simple cases:

```python
from pydantic import Field

class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0, le=99999.99)
    sku: str = Field(..., pattern=r"^[A-Z]{3}-\d{4}$")  # e.g., TRM-0001
    quantity: int = Field(default=0, ge=0)
```

---

### Q16. What is `from_attributes=True` and why is it needed?

**Answer:** By default, Pydantic models only accept dictionaries. SQLAlchemy returns ORM objects with attribute access (`order.id`, `order.total`), not dictionary access. `from_attributes=True` (called `orm_mode=True` in Pydantic v1) tells Pydantic to read data from object attributes instead of dictionary keys.

```python
# Without from_attributes — FAILS
class OrderResponse(BaseModel):
    id: int
    total: float

order = db.query(Order).first()  # SQLAlchemy object
OrderResponse.model_validate(order)
# ERROR: value is not a valid dict

# With from_attributes — WORKS
class OrderResponse(BaseModel):
    id: int
    total: float
    model_config = ConfigDict(from_attributes=True)

order = db.query(Order).first()  # SQLAlchemy object
OrderResponse.model_validate(order)
# Reads order.id, order.total via attribute access → works!

# In endpoints, FastAPI does this automatically with response_model:
@app.get("/orders/{id}", response_model=OrderResponse)
def get_order(id: int, db: Session = Depends(get_db)):
    return db.query(Order).get(id)
    # FastAPI calls OrderResponse.model_validate(orm_object) internally
```

---

### Q17. How does FastAPI handle nested Pydantic models?

**Answer:** Pydantic models can be nested arbitrarily, and FastAPI validates the entire tree recursively.

```python
class Product(BaseModel):
    id: int
    name: str
    price: float

class OrderItem(BaseModel):
    product: Product
    quantity: int = Field(..., ge=1)
    line_total: float

class ShippingAddress(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str = Field(..., pattern=r"^\d{5}(-\d{4})?$")

class OrderResponse(BaseModel):
    id: int
    merchant_id: str
    items: list[OrderItem]                 # nested list of objects
    shipping: ShippingAddress              # nested single object
    total: float
    status: str
    model_config = ConfigDict(from_attributes=True)

# FastAPI validates the entire nested structure:
# {
#   "id": 1,
#   "merchant_id": "M-001",
#   "items": [
#     {
#       "product": {"id": 1, "name": "Verifone T650", "price": 599.99},
#       "quantity": 2,
#       "line_total": 1199.98
#     }
#   ],
#   "shipping": {
#     "street": "123 Main St",
#     "city": "Charlotte",
#     "state": "NC",
#     "zip_code": "28134"
#   },
#   "total": 1199.98,
#   "status": "pending"
# }
```

For ORM relationships, ensure your SQLAlchemy models have `relationship()` defined and the Pydantic models have `from_attributes=True` at every level.

---

### Q18. Explain FastAPI's dependency injection system with `Depends()`.

**Answer:** `Depends()` declares that a parameter should be provided by calling another function. FastAPI calls the dependency function, injects its return value, handles cleanup (for `yield` dependencies), and caches results within a single request.

```python
from fastapi import Depends

# Simple dependency — reusable logic
def get_pagination(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
):
    return {"skip": (page - 1) * per_page, "limit": per_page}

@app.get("/orders")
async def list_orders(pagination: dict = Depends(get_pagination)):
    # pagination = {"skip": 0, "limit": 20}
    return db.query(Order).offset(pagination["skip"]).limit(pagination["limit"]).all()

@app.get("/merchants")
async def list_merchants(pagination: dict = Depends(get_pagination)):
    # Same pagination logic reused — DRY
    ...
```

**Why `Depends()` instead of calling the function directly:** dependency results are cached per-request (call `get_db` in 3 places, get the same session), dependencies can be overridden in tests (swap real DB for test DB), dependencies compose (a dependency can have its own dependencies), and FastAPI manages lifecycle (cleanup via `yield`).

---

### Q19. How do you create a `get_db` dependency for database sessions?

**Answer:** Use a `yield` dependency to create a session, provide it, and ensure it's closed after the request — even if an exception occurs.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "postgresql://user:pass@localhost:5432/pos_db"

engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency — yields a session, ensures cleanup
def get_db():
    db = SessionLocal()
    try:
        yield db        # session provided to endpoint
    finally:
        db.close()      # always closed, even on error

# Usage — injected automatically
@app.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
    # After this returns (or raises), finally block closes the session
```

The `yield` is key — code before `yield` runs before the endpoint, code after `yield` runs after the response is sent (cleanup). This pattern is equivalent to a context manager.

---

### Q20. How do you implement `get_current_user` authentication dependency?

**Answer:**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# Role-based dependency built on top
def require_role(required_role: str):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# Usage
@app.get("/orders")
async def list_orders(user: User = Depends(get_current_user)):
    # Any authenticated user
    return get_orders_for_user(user.id)

@app.delete("/orders/{id}")
async def delete_order(id: int, admin: User = Depends(require_role("admin"))):
    # Only admins
    ...
```

`OAuth2PasswordBearer` automatically extracts the token from the `Authorization: Bearer <token>` header. It also adds the lock icon to Swagger UI for interactive testing.

---

### Q21. What is the difference between a dependency with `yield` and a regular dependency?

**Answer:**

**Regular dependency** — runs completely before the endpoint. Returns a value. No cleanup.

**`yield` dependency** — runs setup code before `yield`, provides the value, then runs cleanup code after the response is sent.

```python
# Regular — no cleanup
def get_settings():
    return Settings()  # returns immediately, no cleanup needed

# Yield — setup + cleanup
def get_db():
    db = SessionLocal()     # SETUP: create session
    try:
        yield db            # PROVIDE: endpoint uses this
    finally:
        db.close()          # CLEANUP: runs after response sent

# Yield — with commit/rollback pattern
def get_db_transactional():
    db = SessionLocal()
    try:
        yield db
        db.commit()         # if no exception → commit
    except Exception:
        db.rollback()       # if exception → rollback
        raise
    finally:
        db.close()          # always close

# Multiple yield dependencies — cleanup in REVERSE order
@app.get("/report")
def generate_report(
    db: Session = Depends(get_db),           # opened first, closed last
    cache: Redis = Depends(get_redis),       # opened second, closed second
    file: TempFile = Depends(get_temp_file), # opened last, closed first
):
    ...
```

**Think of `yield` dependencies as context managers:** `try/yield/finally` is equivalent to `__enter__/__exit__` in a `with` block.

---

### Q22. Walk through setting up SQLAlchemy with FastAPI.

**Answer:** Four pieces: engine, session factory, base model, and dependency.

```python
# app/db/session.py — Engine and session factory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://user:pass@localhost:5432/pos_db"

engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # maintain 20 persistent connections
    max_overflow=10,       # allow 10 more under burst
    pool_recycle=3600,     # recycle connections after 1 hour
    echo=False,            # True for SQL logging in dev
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# app/db/dependency.py — Session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# app/models/order.py — ORM model
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, server_default=func.now())
    items = relationship("OrderItem", back_populates="order")
    merchant = relationship("Merchant", back_populates="orders")

# app/main.py — Create tables on startup (dev only; use Alembic in prod)
from app.db.session import engine, Base
from app.models import order, merchant  # import to register models

Base.metadata.create_all(bind=engine)

app = FastAPI()
```

---

### Q23. What is Alembic and how do you use it for migrations?

**Answer:** Alembic is the database migration tool for SQLAlchemy — the equivalent of Django's `makemigrations` / `migrate`. It tracks schema changes as versioned Python scripts and applies them to your database in order.

```bash
# Initialize Alembic in your project
alembic init alembic

# Configure alembic/env.py to use your Base and DATABASE_URL
# In env.py:
#   from app.db.session import Base
#   target_metadata = Base.metadata

# Generate a migration after changing models
alembic revision --autogenerate -m "add status column to orders"
# Alembic compares your models to the current DB schema
# Generates: alembic/versions/a1b2c3d4_add_status_column_to_orders.py

# The generated migration file:
def upgrade():
    op.add_column('orders', sa.Column('status', sa.String(), nullable=True))

def downgrade():
    op.drop_column('orders', 'status')

# Apply the migration
alembic upgrade head        # apply all pending migrations
alembic upgrade +1          # apply next one migration
alembic downgrade -1        # rollback last migration
alembic history             # show migration history
alembic current             # show current revision
```

**Critical production practice:** Never use `Base.metadata.create_all()` in production. Always use Alembic migrations — they're version-controlled, reversible, and auditable.

---

### Q24. How do you use async database access in FastAPI?

**Answer:** Replace synchronous SQLAlchemy with async equivalents:

```python
# app/db/session.py — Async engine and session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/pos_db"
#                          ^^^^^^^^ async driver

async_engine = create_async_engine(DATABASE_URL, pool_size=20)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Async dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Async endpoint
@app.get("/orders/{order_id}")
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(404, "Order not found")
    return order
```

**Async database libraries:** `asyncpg` (PostgreSQL, fastest), `aiomysql` (MySQL), `aiosqlite` (SQLite), `databases` (multi-driver wrapper). For ORM, SQLAlchemy 2.0+ has full native async support.

---

### Q25. What is middleware and how do you write a request logging example?

**Answer:** Middleware is code that runs **before every request** and **after every response**. It wraps the entire request/response cycle.

```python
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # BEFORE — runs before the endpoint
        request_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()

        # Add request ID to headers for tracing
        request.state.request_id = request_id

        # Call the actual endpoint
        response = await call_next(request)

        # AFTER — runs after the endpoint
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"→ {response.status_code} ({duration_ms:.1f}ms)"
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"
        return response

# Register middleware
app.add_middleware(RequestLoggingMiddleware)

# Log output:
# [a3f8b2c1] GET /api/v1/orders/42 → 200 (23.4ms)
# [7e2d1f9a] POST /api/v1/orders → 201 (156.7ms)
# [c4b9e3d2] GET /api/v1/orders/999 → 404 (8.2ms)
```

---

### Q26. How would you implement rate limiting?

**Answer:**

**Approach 1: In-memory with `slowapi` (simplest):**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/orders")
@limiter.limit("100/minute")
async def list_orders(request: Request):
    ...
# Returns 429 Too Many Requests after 100 calls/minute from same IP
```

**Approach 2: Redis-based (distributed, production):**

```python
import redis.asyncio as redis

redis_client = redis.from_url("redis://localhost:6379")

async def rate_limit(request: Request, limit: int = 100, window: int = 60):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}:{request.url.path}"

    current = await redis_client.incr(key)
    if current == 1:
        await redis_client.expire(key, window)

    if current > limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {window} seconds.",
            headers={"Retry-After": str(window)}
        )

# As a dependency
@app.get("/orders", dependencies=[Depends(rate_limit)])
async def list_orders():
    ...
```

**Approach 3: API Gateway level** — Kong, AWS API Gateway, or Nginx rate limiting. Best for production because it offloads work from your application.

---

### Q27. How do you secure FastAPI with OAuth2 and JWT?

**Answer:** Four components: password hashing, token creation, token verification, and the OAuth2 scheme.

```python
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# JWT token creation
SECRET_KEY = "your-256-bit-secret"
ALGORITHM = "HS256"

def create_access_token(user_id: int, expires_delta: timedelta = timedelta(hours=1)):
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + expires_delta,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@app.post("/auth/login")
async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}

# Protected endpoint
@app.get("/orders")
async def list_orders(current_user: User = Depends(get_current_user)):
    return get_user_orders(current_user.id)
```

---

### Q28. How does FastAPI handle CORS?

**Answer:** FastAPI uses Starlette's `CORSMiddleware` to handle Cross-Origin Resource Sharing:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pos-dashboard.company.com",    # production frontend
        "http://localhost:3000",                  # dev React app
    ],
    allow_credentials=True,     # allow cookies/auth headers
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID", "X-Response-Time"],
    max_age=3600,              # cache preflight response for 1 hour
)

# NEVER do this in production:
# allow_origins=["*"]  ← allows any website to call your API
```

CORS works by the browser sending a **preflight OPTIONS request** before the actual request. The middleware responds with the allowed origins, methods, and headers. If the requesting origin isn't in the allowed list, the browser blocks the request client-side.

---

### Q29. How do you write tests and override dependencies?

**Answer:** FastAPI provides `TestClient` (from Starlette) and `app.dependency_overrides` for swapping dependencies during tests.

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import Base, get_db

# Test database
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DATABASE_URL)
TestSession = sessionmaker(bind=test_engine)

# Override the get_db dependency with test database
def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Override authentication for testing
def override_get_current_user():
    return User(id=1, email="test@test.com", role="admin")

app.dependency_overrides[get_current_user] = override_get_current_user

# Fixtures
@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

client = TestClient(app)

# Tests
def test_create_order():
    response = client.post("/api/v1/orders", json={
        "merchant_id": "M-001",
        "total": 599.99,
        "items": ["Verifone T650"]
    })
    assert response.status_code == 201
    data = response.json()
    assert data["merchant_id"] == "M-001"
    assert data["status"] == "pending"
    assert "id" in data

def test_get_order_not_found():
    response = client.get("/api/v1/orders/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"

def test_create_order_validation_error():
    response = client.post("/api/v1/orders", json={
        "merchant_id": "",
        "total": -5,
        "items": []
    })
    assert response.status_code == 422
```

---

### Q30. Design a production deployment for 10K requests/second.

**Answer:**

```
                        Internet
                           │
                    ┌──────▼──────┐
                    │   CDN       │  Static assets, cached GET responses
                    │  CloudFront │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Load      │  AWS ALB / Nginx
                    │   Balancer  │  SSL termination, health checks
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐ ┌───▼───┐ ┌─────▼─────┐
        │  Pod 1    │ │ Pod 2 │ │  Pod N    │   Kubernetes pods
        │           │ │       │ │           │
        │  Gunicorn │ │  ...  │ │  Gunicorn │   Process manager
        │  4 Uvicorn│ │       │ │  4 Uvicorn│   ASGI workers
        │  workers  │ │       │ │  workers  │
        └─────┬─────┘ └───┬───┘ └─────┬─────┘
              │            │            │
              └────────────┼────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐ ┌───▼───┐ ┌─────▼─────┐
        │  Redis    │ │ Postgres│ │  S3       │
        │  Cache    │ │ Primary │ │  Files    │
        │  +Session │ │ +Replica│ │           │
        └───────────┘ └────────┘ └───────────┘
```

**Key components:**

**ASGI Server:** Uvicorn with `--workers 4` (per CPU core) behind Gunicorn as the process manager: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000`

**Horizontal Scaling:** Kubernetes with Horizontal Pod Autoscaler (HPA). Start with 10 pods × 4 workers = 40 Uvicorn workers. Auto-scale based on CPU/memory/request latency.

**Caching:** Redis for frequently read, rarely changing data (product catalog, merchant profiles). Cache headers for GET responses (`Cache-Control: max-age=60`). CDN for static assets.

**Database:** PostgreSQL with read replicas. Connection pooling via PgBouncer (hundreds of app workers sharing dozens of DB connections). Async driver (asyncpg) for non-blocking queries.

**Reverse Proxy:** Nginx or AWS ALB for SSL termination, load balancing, request buffering, gzip compression, and static file serving.

**Containerization:** Docker image with multi-stage build (slim Python base). Kubernetes for orchestration, rolling deployments, health checks.

**Monitoring:** Prometheus + Grafana for metrics. Structured JSON logging → ELK/Loki. Sentry for error tracking. OpenTelemetry for distributed tracing.

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "30", "--graceful-timeout", "10"]
```

```yaml
# kubernetes deployment
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 10
  template:
    spec:
      containers:
        - name: fastapi-app
          image: pos-api:latest
          ports:
            - containerPort: 8000
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            periodSeconds: 30
```

---

## Section 3: Implementation Tracker

| #   | Category     | Topic                                                        | Status         | Date Completed | Notes |
| --- | ------------ | ------------------------------------------------------------ | -------------- | -------------- | ----- |
| 1   | Fundamentals | Compare FastAPI vs Flask vs DRF with same endpoint           | ⬜ Not Started |                |       |
| 2   | Fundamentals | Identify Starlette and Pydantic usage in a FastAPI app       | ⬜ Not Started |                |       |
| 3   | Fundamentals | Build endpoints with def and async def, test concurrency     | ⬜ Not Started |                |       |
| 4   | Fundamentals | Customize Swagger and ReDoc documentation                    | ⬜ Not Started |                |       |
| 5   | Fundamentals | Build endpoint with full type hints, check generated schema  | ⬜ Not Started |                |       |
| 6   | Fundamentals | Run Uvicorn, inspect ASGI request/response cycle             | ⬜ Not Started |                |       |
| 7   | Routing      | Build endpoint with path, query, and body params combined    | ⬜ Not Started |                |       |
| 8   | Routing      | Trigger validation errors, customize error response format   | ⬜ Not Started |                |       |
| 9   | Routing      | Split app into 4+ routers with APIRouter and tags            | ⬜ Not Started |                |       |
| 10  | Routing      | Implement single and multi-file upload endpoints             | ⬜ Not Started |                |       |
| 11  | Routing      | Set up v1 and v2 API versions side by side                   | ⬜ Not Started |                |       |
| 12  | Routing      | Return 201, 204, 404 with custom headers                     | ⬜ Not Started |                |       |
| 13  | Pydantic     | Create SQLAlchemy model + matching Pydantic schemas          | ⬜ Not Started |                |       |
| 14  | Pydantic     | Build Create, Update, Response schemas with base inheritance | ⬜ Not Started |                |       |
| 15  | Pydantic     | Add field_validator and model_validator to a schema          | ⬜ Not Started |                |       |
| 16  | Pydantic     | Return ORM objects with from_attributes=True                 | ⬜ Not Started |                |       |
| 17  | Pydantic     | Build nested Order → OrderItems → Product response           | ⬜ Not Started |                |       |
| 18  | DI           | Create reusable pagination and filtering dependencies        | ⬜ Not Started |                |       |
| 19  | DI           | Implement get_db with yield and proper cleanup               | ⬜ Not Started |                |       |
| 20  | DI           | Build JWT auth with get_current_user + role-based access     | ⬜ Not Started |                |       |
| 21  | DI           | Compare yield vs regular dependency with logging             | ⬜ Not Started |                |       |
| 22  | Database     | Set up full SQLAlchemy integration from scratch              | ⬜ Not Started |                |       |
| 23  | Database     | Initialize Alembic, generate and apply a migration           | ⬜ Not Started |                |       |
| 24  | Database     | Convert sync endpoint to async with asyncpg                  | ⬜ Not Started |                |       |
| 25  | Middleware   | Build request logging middleware with timing                 | ⬜ Not Started |                |       |
| 26  | Middleware   | Implement Redis-based rate limiting                          | ⬜ Not Started |                |       |
| 27  | Security     | Build complete OAuth2 + JWT login flow                       | ⬜ Not Started |                |       |
| 28  | Security     | Configure CORS for specific frontend domain                  | ⬜ Not Started |                |       |
| 29  | Testing      | Write 10+ tests with TestClient and dependency overrides     | ⬜ Not Started |                |       |
| 30  | Deployment   | Create Dockerfile + docker-compose for local prod simulation | ⬜ Not Started |                |       |

### Status Legend

| Icon | Status       | Description                       |
| ---- | ------------ | --------------------------------- |
| ⬜   | Not Started  | Haven't begun implementation      |
| 🟡   | In Progress  | Currently working on it           |
| ✅   | Completed    | Implemented and tested            |
| 🔄   | Needs Review | Implemented but needs code review |
| ❌   | Blocked      | Stuck, need help                  |

---

> **Tip:** Clone this file, update the tracker as you go, and commit your implementations alongside this README in a Git repository for a complete study portfolio.
