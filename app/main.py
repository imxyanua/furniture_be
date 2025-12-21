from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import (
    auth, users, products, categories, banners, cart, favorites, orders, 
    countries, filters, reviews, inventory, suppliers, reports, notifications
)

app = FastAPI(
    title="Furniture Store API",
    description="Backend API for Furniture E-commerce Application",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(banners.router, prefix="/api")
app.include_router(cart.router, prefix="/api")
app.include_router(favorites.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(countries.router, prefix="/api")
app.include_router(filters.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")
app.include_router(suppliers.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Furniture Store API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
