# app/v2/main.py
from fastapi import FastAPI

# Create a separate FastAPI instance for v2.
app = FastAPI(
    title="API Version 2",
    description="This is the second, improved version of our API.",
    version="2.0.0",
    docs_url=None,  # Disable the default Swagger UI
    redoc_url="/redoc",  # Enable ReDoc at /v2/redoc
)


@app.get("/items/", tags=["Items"])
async def read_items_v2():
    """
    An updated endpoint for version 2 to retrieve items.
    """
    return {"message": "This is the shiny new response from API v2", "status": "ok"}


@app.get("/products/", tags=["Products"])
async def read_products_v2():
    """
    A new endpoint available only in version 2.
    """
    return {"products": ["product_a_v2", "product_b_v2"]}
