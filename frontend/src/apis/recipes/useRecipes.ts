import { useQuery } from "@tanstack/react-query"
import type { RecipeSearchRequestDto } from "./dtos/RecipeDtos"
import { recipeRequests } from "./requests/recipeRequests"

export const RECIPE_TYPES_QUERY_KEY = ["recipeTypes"] as const

export const useRecipeTypes = () => {
  return useQuery({
    queryFn: recipeRequests.types,
    queryKey: RECIPE_TYPES_QUERY_KEY,
    select: (data) => data.typesRecette,
  })
}

export const useRecipeSearch = (request: RecipeSearchRequestDto) => {
  return useQuery({
    queryFn: () => recipeRequests.search(request),
    queryKey: ["recipes", request],
    select: (data) => data.recettes,
  })
}
