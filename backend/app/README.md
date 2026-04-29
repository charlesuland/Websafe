# Backend

FastAPI backend for WebSafe.

- Serves API routes for users, auth, projects, products, orders, vendors, checkout, and subscriptions
- Uses SQLModel / SQLAlchemy for database models
- Creates tables on startup
- Uses JWT auth and CORS for frontend integration

Run from the backend folder with `uvicorn app.main:app --reload`.

Stripe change notes.
Changing the schema to fit the new stripe models.
Subscriptions will made and handled through stripe