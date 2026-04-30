# this is the start of the backend API for FastAPI
#
#
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import users, projects, subscriptions, products, orders, vendors, checkout, security, webhooks, stripe_router
from app import auth
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base

from dotenv import load_dotenv

# necessary for the app to build the models
import app.models
load_dotenv()   # Docker sets env vars directly; this is fine as a fallback

# this function happens on startup. Before the yield happens before the app runs
# after the yield happens after the app shuts down
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    print("APP STARTING...\nCREATING TABLES")
    yield
    print("APP SHUTTING DOWN")


# instantiates FastAPI object application
app = FastAPI(lifespan=lifespan)

# allows methods to be called from the frontend application
# When the application is expanded, the list of hosts (origins) may need to increase
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",   # local dev (Vite)
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176",
    "http://localhost",        # Docker frontend (port 80)
    "http://localhost:5173",   # Docker frontend mapped to 5173
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# need to include the different routes
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(projects.projects_router, prefix="/api")
app.include_router(projects.public_router, prefix="/api")
app.include_router(products.products_router, prefix="/api")
app.include_router(subscriptions.router, prefix="/api")
app.include_router(orders.orders_router, prefix="/api")
app.include_router(vendors.vendors_router, prefix="/api")
app.include_router(checkout.checkout_router, prefix="/api")
app.include_router(webhooks.webhooks_router, prefix="/api")
app.include_router(security.router, prefix="/api")
app.include_router(stripe_router.router, prefix="/api")
