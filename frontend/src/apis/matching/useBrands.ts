import { useQuery } from "@tanstack/react-query"
import { brandRequests } from "./requests/brandRequests"

const MIN_QUERY_LENGTH = 2
const SUGGESTION_LIMIT = 10

export const useBrandSuggestions = (query: string) => {
  return useQuery({
    enabled: query.trim().length >= MIN_QUERY_LENGTH,
    queryFn: () => brandRequests.suggest(query.trim(), SUGGESTION_LIMIT),
    queryKey: ["brands", query.trim()],
    select: (data) => data.marques,
  })
}
