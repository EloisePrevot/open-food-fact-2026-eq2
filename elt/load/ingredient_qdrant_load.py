from transform.ingredient_qdrant_transform import IngredientQdrantTransform
from tqdm import tqdm


class IngredientQdrantLoad:

    def __init__(self, raw_store, qdrant_store):
        self.raw_store = raw_store
        self.qdrant_store = qdrant_store

    def load(self):
        ingredients = self.raw_store.get_ingredients()

        documents = [
            IngredientQdrantTransform.transform(ingredient)
            for ingredient in tqdm(ingredients, desc="Transformation des ingrédients")
        ]

        self.qdrant_store.load_ingredients(documents)