import { API_BASE_URL } from "@/shared/config/apiConfig"
import { ensureSuccess } from "@/shared/utils/http"
import type {
  RecipeDetailDto,
  RecipeSearchRequestDto,
  RecipeSearchResponseDto,
  RecipeTypesDto,
} from "../dtos/RecipeDtos"

const RECIPE_SEARCH_ENDPOINT = `${API_BASE_URL}/recette`
const RECIPE_TYPES_ENDPOINT = `${API_BASE_URL}/type`
const recipeDetailEndpoint = (identifiant: string) =>
  `${API_BASE_URL}/recette/${encodeURIComponent(identifiant)}`

export const recipeRequests = {
  detail: async (identifiant: string): Promise<RecipeDetailDto> => {
    const response = await fetch(recipeDetailEndpoint(identifiant), {
      headers: { Accept: "application/json" },
    })

    await ensureSuccess(response)

    return (await response.json()) as RecipeDetailDto
  },

  search: async (
    request: RecipeSearchRequestDto,
  ): Promise<RecipeSearchResponseDto> => {
    const response = await fetch(RECIPE_SEARCH_ENDPOINT, {
      body: JSON.stringify(request),
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      method: "POST",
    })

    await ensureSuccess(response)

    return (await response.json()) as RecipeSearchResponseDto
  },

  types: async (): Promise<RecipeTypesDto> => {
    const response = await fetch(RECIPE_TYPES_ENDPOINT, {
      headers: { Accept: "application/json" },
    })

    await ensureSuccess(response)

    return (await response.json()) as RecipeTypesDto
  },
}
