import { API_BASE_URL } from "@/shared/config/apiConfig"
import { ensureSuccess } from "@/shared/utils/http"
import type { RawDataDto } from "../dtos/RawDataDtos"

const RAW_DATA_ENDPOINT = `${API_BASE_URL}/donnees_brutes`

export const rawDataRequests = {
  byIdentifiant: async (identifiant: string): Promise<RawDataDto> => {
    const response = await fetch(
      `${RAW_DATA_ENDPOINT}/${encodeURIComponent(identifiant)}`,
      {
        headers: { Accept: "application/json" },
      },
    )

    await ensureSuccess(response)

    return (await response.json()) as RawDataDto
  },
}
