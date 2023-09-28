import os
import string
from enum import Enum
from typing import Optional

import psycopg2

# load_dotenv: loading the key-value pairs environment variables in .env
# dotenv_values: loading environment variables as a list of tuples
from dotenv import dotenv_values, load_dotenv

# use Path and Query to add extra constraints
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware

# FastAPI relies on pydantic for validation and definitions
from pydantic import BaseModel, Field, validator

from utils import queries

# from config import config

app = FastAPI(
    title="Charlie's first FastAPI App",
    description="An barebone inventory app allows users to check, add, modify, delete items.",
    version="0.1.0",
)

# origins middleware settings permits connection from different urls and ports
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Category(Enum):
    """Category of an item"""

    TOOLS = "tools"
    CONSUMABLES = "consumables"


# Creating validation by using BaseModel from pydantic
# You can add metadata to attributes using the Field class.
# This information will also be be shown in hte auto-generated documentation.


class Item(BaseModel):
    name: str = Field(description="Name of the item.")
    price: float = Field(description="Price of the item in Euro.")
    count: int = Field(description="Amount of instances of this item in stock.")
    id: int = Field(description="Unique integer that specifies this item.")
    category: Category = Field(description="Category this item belongs to.")

    # we can add validation class method to validate field
    # It's a pydantic validator method that validate 'name' field specifically
    # Whenever we set the 'name' field, this validator method will be called
    # It's a class method, first parameter will be cls, not self
    @validator("name")
    @classmethod
    def name_valid(cls, value):
        if any(p in value for p in string.punctuation):
            raise ValueError("Username must not include punctuation.")
        else:
            return value

    # Validate if the number is positive
    @validator("price", "count")
    @classmethod
    def number_valid(cls, value):
        if value >= 0:
            return value
        else:
            raise ValueError("Numbers must be positive.")


# Usually this will go to sql database
items = {
    0: Item(name="Hammer", price=9.99, count=20, id=0, category=Category.TOOLS),
    1: Item(name="Pliers", price=5.99, count=20, id=1, category=Category.TOOLS),
    2: Item(name="Nails", price=1.99, count=100, id=2, category=Category.CONSUMABLES),
}

# load_dotenv()
# print(f"My secret key is {os.getenv('MY_SECRET_KEY')}")

# Load the environment variables from .env
env_variables = dotenv_values(".env")

# Define the keys you want to extract from the environment variables
keys_to_extract = ["host", "port", "database", "user"]

# Create a dictionary with only the required keys and their values
# Create a dict, so we can use ** later in the code
db_params = {key: env_variables[key] for key in keys_to_extract}

print(env_variables)
print(db_params)


def connect(myQuery: str) -> None:
    connection = None
    try:
        print("Connecting to PostgreSQL")
        # connect(): Create new database session, return a new instance of connection class
        # **params extracts everything in params
        connection = psycopg2.connect(**db_params)

        # cursor() method is used to create a new cursor object
        # A cursor is an essential component when working with databases
        # Cursor allows you to execute SQL queries and fetch results from the database.
        cursor = connection.cursor()
        # executing the query
        cursor.execute(myQuery)
        # commit() method is used to save changes to the database after performing INSERT, UPDATE, or DELETE operations. Doesn't need if it's a Select
        connection.commit()
        db_fetch_results = cursor.fetchall()
        print("---------- Fetching ----------")
        for row in db_fetch_results:
            print(row)
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            connection.close()
            print("Database connection terminated.")


# if __name__ == '__main__':
connect(queries.query_strings["check_version"])
# connect(queries.query_strings["create_type"])
connect(queries.query_strings["create_inventory_table"])
# connect(queries.query_strings["insert_batch"])
connect(queries.query_strings["select_items"])


# print(items[2])
# print(type(items[2]))

# FastAPI handles JSON serialization adn deserialization for us.
# We can simply use built-in python and Pydantic types, in this case dict[int, Items]


@app.get("/", response_model=dict[str, dict[int, Item]])
# limit is a query here, eg: http://127.0.0.1:8000/?limit=3
def index(limit: int = 2) -> dict[str, dict[int, Item]]:
    # return {'items': items}

    # Since key in items is serial num, we can implement limit to make the page render items within the limit
    # We can't slice dict cos dict is an unordered object
    # http://127.0.0.1:8000/?limit=3 will show 3 items
    # http://127.0.0.1:8000/?limit=1 will show 1 items
    return {"items": {key: value for key, value in items.items() if key < limit}}


# creating a router to retrieve item by id
# response_model decorator  is used to specify the model that describes the structure of the response API endpoint will return
# adding the response_model decorator can be considered good practice
# Technically we don't need response_model decorator here, cos it explicitly notes the return model inside the function


@app.get("/items/{item_id}", response_model=Item)
# FastAPI will do the type validation, send error msg if you didn't input int here
def query_item_by_id(item_id: int) -> Item:
    if item_id not in items:
        # in Python, raise an exception
        raise HTTPException(
            status_code=404, detail=f"Item with {item_id} does not exist."
        )
    # We don't worry about converting JSON, that FastAPI takes care of
    return items[item_id]


# Creating a router for query, used as for the word after question mark in URL
# For instance, when you want to search item by providing query items: /items?count=20


# dictionary containing the user's query arguments
Selection = dict[str, str | int | float | Category | None]


@app.get("/items")
def query_item_by_parameters(
    name: str | None = None,
    price: float | None = None,
    count: int | None = None,
    category: Category | None = None,
) -> dict[str, Selection | list[Item]]:
    def check_item(item: Item) -> bool:
        """Check if the item matches the query arguments from the outer scope"""
        return all(
            (
                name is None or item.name == name,
                price is None or item.price == price,
                count is None or item.count == count,
                category is None or item.category is category,
            )
        )

    selection = [item for item in items.values() if check_item(item)]
    return {
        "query": {"name": name, "price": price, "count": count, "category": category},
        "selection": selection,
    }


# This item object will be retrieved from the body of post request
# You send JSON data to this endpoint.
# FastAPI will automatically transform the JSON data into pydantic objects for you
# Never miss the key word 'raise' in front of HTTPException


@app.post("/")
def add_item(item: Item) -> dict[str, Item]:
    # Checking if item.id is one of the keys in dict items
    # it's the same as 'if item.id in items.keys()'
    print("---------------")
    print(item.id, type(item.id))
    print("---------------")
    if item.id in items:
        raise HTTPException(
            status_code=400, detail=f"Item with {item.id=} already exists."
        )
    items[item.id] = item
    return {"added": item}


# Creating router for update
# The url for update will be like: http://127.0.0.1:8000/items/1?count=9001&price=99.99
# The 'responses' keyword allows you to specify which responses a user can expect from


@app.put(
    "/items/{item_id}",
    responses={
        404: {"description": "Item not found"},
        400: {"description": "No arguments specified"},
    },
)
def update(
    # Adding extra validation flexibility
    # item_id as the url path argument should be greater and equal to 0
    item_id: int = Path(ge=0),
    name: str | None = Query(default=None, min_length=1, max_length=8),
    price: float | None = Query(default=None, gt=0.0),
    count: int | None = Query(default=None, ge=0),
) -> dict[str, Item]:
    if item_id not in items:
        raise HTTPException(
            status_code=404, detail=f"Item with {item_id=} does not exist."
        )
    if all(info is None for info in (name, price, count)):
        raise HTTPException(
            status_code=400, detail="No parameters provided for update."
        )

    item = items[item_id]
    if name is not None:
        item.name = name
    if price is not None:
        item.price = price
    if count is not None:
        item.count = count

    return {"updated": item}


# Creating router for delete


@app.delete("/items/{item_id}")
def delete_item(item_id: int) -> dict[str, Item]:
    if item_id not in items:
        raise HTTPException(
            status_code=404, detail=f"Item with {item_id=} does not exist."
        )
    item = items.pop(item_id)
    return {"deleted": item}
