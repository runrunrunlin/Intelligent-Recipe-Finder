from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from database import Base

# 中间表：关联食谱和食材（多对多关系）
recipe_ingredient_association = Table(
    "recipe_ingredient_association",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id")),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id"))
)

# 食材表
class Ingredient(Base):
    __tablename__ = 'ingredients'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)  # 清理后的食材名称
    recipes = relationship(
        "Recipe",
        secondary=recipe_ingredient_association,
        back_populates="ingredients"
    )

# 食谱表
class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)                # 菜名 (对应 CSV 的 Title)
    ingredients_text = Column(Text)                   # 原始食材文本 (对应 CSV 的 Ingredients)
    instructions = Column(Text)                       # 烹饪步骤 (对应 CSV 的 Instructions)
    image_name = Column(String)                       # 图片名称 (对应 CSV 的 Image_Name)
    cleaned_ingredients = Column(Text)                # 清理后的食材列表 (对应 CSV 的 Cleaned_Ingredients)

    # 定义食谱和食材的多对多关系
    ingredients = relationship(
        "Ingredient",
        secondary=recipe_ingredient_association,
        back_populates="recipes"
    )

