from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import  Ingredient, Recipe
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()
# 挂载前端静态文件
app.mount("/frontend", StaticFiles(directory="../frontend"), name="frontend")
app.mount("/images", StaticFiles(directory="../frontend/Food Images"), name="images")

# 访问 / 时返回 index.html 页面
@app.get("/")
def read_index():
    return FileResponse(os.path.join("../frontend", "index.html"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建数据库表
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/test")
def test():
    return {"message": "Test endpoint is working"}

@app.get("/debug/ingredients")
def list_ingredients(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    total = db.query(Ingredient).count()
    ingredients = db.query(Ingredient).offset(skip).limit(limit).all()
    return {
        "total": total,
        "items": [{"id": i.id, "name": i.name} for i in ingredients]
    }

@app.get("/recipes")
def get_all_recipes(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    total = db.query(Recipe).count()
    recipes = db.query(Recipe).offset(skip).limit(limit).all()
    return {
        "total": total,
        "items": [{
            "id": recipe.id,
            "title": recipe.title,
            "ingredients": recipe.ingredients_text,
            "instructions": recipe.instructions,
            "image_name": recipe.image_name,
            "cleaned_ingredients": [ing.name for ing in recipe.ingredients]
        } for recipe in recipes]
    }

@app.get("/recipes/search")
def search_recipes(
    ingredient: str, 
    db: Session = Depends(get_db), 
    skip: int = 0, 
    limit: int = 20
):
    print(f"Search ingredients: {ingredient}")
    ingredients = [i.strip().lower() for i in ingredient.split(",") if i.strip()]
    print(f"Processed ingredient list: {ingredients}")

    if not ingredients:
        raise HTTPException(
            status_code=400, 
            detail="At least one ingredient must be provided"
        )
    
    try:
        # Base query
        query = db.query(Recipe).distinct()
        
        # For each ingredient, use OR conditions instead of AND conditions
        # Match any ingredient instead of requiring all
        if len(ingredients) == 1:
            # Single ingredient case: direct fuzzy matching
            ing = ingredients[0]
            query = query.join(Recipe.ingredients).filter(
                func.lower(Ingredient.name).like(f"%{ing}%")
            )
        else:
            # Multiple ingredients case: match any and sort by relevance
            from sqlalchemy import or_
            
            # Create a filter condition to find recipes containing any provided ingredient
            ingredient_conditions = [
                Recipe.ingredients.any(
                    func.lower(Ingredient.name).like(f"%{ing}%")
                ) for ing in ingredients
            ]
            
            query = query.filter(or_(*ingredient_conditions))
        
        # Get total count
        total = query.count()
        print(f"Total recipes found: {total}")
        
        if total == 0:
            raise HTTPException(
                status_code=404, 
                detail=f"No recipes found containing these ingredients: {ingredient}"
            )
        
        # Get results sorted by the number of matching ingredients
        recipes = query.order_by(Recipe.id).offset(skip).limit(limit).all()
        
        # Return complete recipe information
        return {
            "total": total,
            "items": [{
                "id": recipe.id,
                "title": recipe.title,                   
                "ingredients_text": recipe.ingredients_text, 
                "instructions": recipe.instructions,       
                "image_name": recipe.image_name,         
                "cleaned_ingredients": [ing.name for ing in recipe.ingredients]  
            } for recipe in recipes]
        }
    except HTTPException:
        raise
    except Exception as e:
        # Catch and log any other exceptions
        print(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing search: {str(e)}"
        )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)