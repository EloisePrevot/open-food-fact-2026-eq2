import { API_BASE_URL } from "@/shared/config/apiConfig"
import { ensureSuccess } from "@/shared/utils/http"
import type {
  IngredientMatchRequestDto,
  IngredientMatchResponseDto,
} from "../dtos/IngredientDtos"

const INGREDIENT_MATCH_ENDPOINT = `${API_BASE_URL}/apparier_ingredient`

export const ingredientRequests = {
  match: async (
    request: IngredientMatchRequestDto,
  ): Promise<IngredientMatchResponseDto> => {
    const response = await fetch(INGREDIENT_MATCH_ENDPOINT, {
      body: JSON.stringify(request),
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      method: "POST",
    })

    await ensureSuccess(response)

    return (await response.json()) as IngredientMatchResponseDto
  },
}
