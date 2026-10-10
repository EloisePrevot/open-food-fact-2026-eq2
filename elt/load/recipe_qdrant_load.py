from transform.recipe_qdrant_transform import RecipeQdrantTransform
from tqdm import tqdm


class RecipeQdrantLoad:

    def __init__(self, raw_store, qdrant_store):
        self.raw_store = raw_store
        self.qdrant_store = qdrant_store

    def load(self):
        recipes = self.raw_store.get_recipes()

        documents = [
            RecipeQdrantTransform.transform(recipe)
            for recipe in tqdm(recipes, desc="Transformation des recettes")
        ]

        self.qdrant_store.load_recipes(documents)