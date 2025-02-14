import csv
from database import SessionLocal, engine, Base
from models import Recipe, Ingredient
from sqlalchemy import text
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import re

import re

def clean_ingredient_name(ingredient):
    
    ingredient = ingredient.strip()
    if not ingredient:
        return None
    ingredient = ingredient.lower()
    ingredient = re.sub(r'\(.*?\)', '', ingredient)
    ingredient = re.sub(r'\b(freshly|fresh|ground|chopped|grated|minced|sliced|diced|crumbled|packed|coarsely|finely|thinly|thickly|roughly|coarse|fine)\b', '', ingredient)
    ingredient = re.sub(r'\b\d+\s*/\s*\d*\s*(cups?|tablespoon|teaspoon|pound|ounce|gram|ml|liter|inch|cm|mm)?\b', '', ingredient)
    ingredient = re.sub(r'\b\d+\s*/\s*\d*\s*(cups?|tablespoons?|teaspoons?|pounds?|ounces?|grams?|ml|liters?|inches?|cm|mm)?\b', '', ingredient)
    ingredient = re.sub(r'[^a-z0-9\s]', '', ingredient)
    ingredient = ingredient.strip()
    if not ingredient:
        return None
    
    return ingredient

def fast_import_recipes(file_path):

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        print("Reading CSV file...")
        with open(file_path, 'r', encoding='utf-8') as f:
            recipes_data = list(csv.DictReader(f))
        
        print("Collecting ingredients...")
        unique_ingredients = set()
        for recipe in recipes_data:
            ingredients = [
                i.strip() 
                for i in recipe['Cleaned_Ingredients'].split(',') 
                if i.strip()
            ]
            unique_ingredients.update(ingredients)
        
        # 批量插入食材
        print("Inserting ingredients...")
        existing_ingredients = {ing.name for ing in db.query(Ingredient).all()}
        for ing in unique_ingredients:
            cleaned_name = clean_ingredient_name(ing)
            if cleaned_name is None:
                continue
            if cleaned_name not in existing_ingredients:
                new_ingredient = Ingredient(name=cleaned_name)
                db.add(new_ingredient)
                existing_ingredients.add(cleaned_name)

        db.commit()
        
        # 重新获取食材映射
        ingredient_map = {
            ing.name: ing 
            for ing in db.query(Ingredient).all()
        }
        
        # 批量插入食谱
        print("Inserting recipes...")
        batch_size = 1000
        current_batch = []
        
        for recipe in tqdm(recipes_data):
            # 创建食谱
            new_recipe = Recipe(
                title=recipe['Title'],                 
                ingredients_text=recipe['Ingredients'], 
                instructions=recipe['Instructions'],    
                image_name=recipe['Image_Name'],        
                cleaned_ingredients=recipe['Cleaned_Ingredients'] 
            )
            
            # 关联食材
            cleaned_ingredients = [
                clean_ingredient_name(i.strip()) 
                for i in recipe['Cleaned_Ingredients'].split(',') 
                if i.strip()
            ]
            
            # 添加食材关联
            new_recipe.ingredients = [
                ingredient_map[ing_name]
                for ing_name in cleaned_ingredients
                if ing_name in ingredient_map
            ]
            
            current_batch.append(new_recipe)
            
            # 每 batch_size 条记录提交一次
            if len(current_batch) >= batch_size:
                db.add_all(current_batch)
                db.commit()
                current_batch = []
        
        # 提交剩余的记录
        if current_batch:
            db.add_all(current_batch)
            db.commit()
            
        print("Import completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error occurred: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    csv_file_path = "recipes.csv"  
    fast_import_recipes(csv_file_path)