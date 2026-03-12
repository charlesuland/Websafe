# this is the start of the backend API for FastAPI
#
#
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import users
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base

# necessary for the app to build the models
import app.models


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
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# need to include the different routes
app.include_router(users.router)
