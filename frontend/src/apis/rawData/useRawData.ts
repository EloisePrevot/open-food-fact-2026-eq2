import { useQuery } from "@tanstack/react-query"
import { rawDataRequests } from "./requests/rawDataRequests"

export const useRawData = (identifiant: string | null) => {
  return useQuery({
    enabled: identifiant !== null,
    queryFn: () => rawDataRequests.byIdentifiant(identifiant as string),
    queryKey: ["rawData", identifiant],
    retry: false,
  })
}
