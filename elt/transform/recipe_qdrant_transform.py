class RecipeQdrantTransform:
    @staticmethod
    def transform(recipe: dict) -> dict:
        ingredients = recipe.get("ingredients", [])

        text = " ".join([
            str(recipe.get("recipe_title", "")),
            str(recipe.get("category", "")),
            str(recipe.get("description", "")),
            str(recipe.get("directions", "")),
            str(recipe.get("difficulty", "")),
            " ".join(map(str, ingredients)),
        ])

        return {
            "text": text.strip(),
            "payload": recipe,
        }