from fastapi import FastAPI, Query, HTTPException
from models import MenuItem, MenuResponse
from data import menu_items

# Initialise the api server and customise its params
app = FastAPI(
    title="Basic Cafe menu API",
    description="Read only API for Kiosk displays and for mobile app"
)

# Initialise the routes here
@app.get('/')
def home():
    return {"message": "Welcome to the Cafe menu API"}


# /menu -> path (endpoint)
# /menu?category=Beverages -> query param

@app.get("/menu", response_model=MenuResponse)
def get_menu(category: str | None = Query(None, description="Filter the menu items by categories (Beverages, Quick Bites, Snacks, Desserts)")):
    if category:
        filtered = [item for item in menu_items if item["category"] == category.title()]
        if not filtered:
            raise HTTPException(status_code=404, detail=f"No item found in category: {category}")
        return MenuResponse(count=len(filtered), items=filtered)

    return MenuResponse(count=len(menu_items), items=menu_items)


@app.get("/menu/{item_id}", response_model=MenuItem)
def get_item(item_id: int):
    for item in menu_items:
        if item["id"] == item_id:
            return item

    raise HTTPException(status_code=404, detail=f"No menu item found with id: {item_id}")