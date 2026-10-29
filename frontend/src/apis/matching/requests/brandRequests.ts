import { API_BASE_URL } from "@/shared/config/apiConfig"
import { ensureSuccess } from "@/shared/utils/http"
import type { BrandSuggestionResponseDto } from "../dtos/BrandDtos"

const brandEndpoint = (query: string, limit: number) =>
  `${API_BASE_URL}/marques?q=${encodeURIComponent(query)}&limite=${limit}`

export const brandRequests = {
  suggest: async (
    query: string,
    limit: number,
  ): Promise<BrandSuggestionResponseDto> => {
    const response = await fetch(brandEndpoint(query, limit), {
      headers: { Accept: "application/json" },
    })

    await ensureSuccess(response)

    return (await response.json()) as BrandSuggestionResponseDto
  },
}
