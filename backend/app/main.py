# this is the start of the backend API for FastAPI
#
#
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import users, projects, subscriptions
from app import auth
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers.users import create_test_user
from app.routers.products import products_router
from app.routers.orders import order_router
from app.routers.vendors import vendor_router
from app.routers.checkout import checkout_router
from app.routers.webhooks import router as webhooks_router
from app.routers.stripe_router import router as stripe_router
from dotenv import load_dotenv

# necessary for the app to build the models
import app.models
load_dotenv('../.env')

# this function happens on startup. Before the yield happens before the app runs
# after the yield happens after the app shuts down
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    create_test_user()

    print("APP STARTING...\nCREATING TABLES")
    yield
    print("APP SHUTTING DOWN")


# instantiates FastAPI object application
app = FastAPI(lifespan=lifespan)

# allows methods to be called from the frontend application
# When the application is expanded, the list of hosts (origins) may need to increase
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# need to include the different routes
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(projects.projects_router, prefix="/api")
app.include_router(projects.public_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(subscriptions.router, prefix="/api")
app.include_router(order_router, prefix="/api")
app.include_router(vendor_router, prefix="/api")
app.include_router(checkout_router, prefix="/api")
app.include_router(webhooks_router, prefix="/api")
app.include_router(stripe_router, prefix="/api")
