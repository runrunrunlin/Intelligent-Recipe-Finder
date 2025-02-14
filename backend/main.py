from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import  Ingredient, Recipe
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select

app = FastAPI()

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
    limit: int = 10
):

    ingredients = [i.strip().lower() for i in ingredient.split(",") if i.strip()]
    
    # 基础查询
    query = db.query(Recipe).join(Recipe.ingredients)
    
    # 添加每个食材的过滤条件
    for ing in ingredients:
        query = query.filter(
            Recipe.ingredients.any(
                func.lower(Ingredient.name).like(f"%{ing}%")
            )
        )
    
    # 获取结果
    total = query.group_by(Recipe.id).count()
    recipes = query.group_by(Recipe.id).order_by(
        func.count(Ingredient.id).desc()
    ).offset(skip).limit(limit).all()
    
    if not recipes:
        raise HTTPException(
            status_code=404, 
            detail=f"No recipes found for ingredients: {ingredient}"
        )
    
    # 返回完整的菜谱信息
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)