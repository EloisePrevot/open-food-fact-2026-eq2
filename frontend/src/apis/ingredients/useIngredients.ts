import { useQuery } from "@tanstack/react-query"
import type { IngredientMatchRequestDto } from "./dtos/IngredientDtos"
import { ingredientRequests } from "./requests/ingredientRequests"

export const useIngredientMatch = (request: IngredientMatchRequestDto) => {
  return useQuery({
    enabled: request.ingredient.trim().length > 0,
    queryFn: () => ingredientRequests.match(request),
    queryKey: ["ingredientMatch", request],
    select: (data) => data.candidats,
  })
}
