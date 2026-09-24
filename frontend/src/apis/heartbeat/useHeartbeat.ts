import { useQuery } from "@tanstack/react-query"
import { HeartbeatApi } from "./heatbeatApi"

export const HEARTBEAT_QUERY_KEY = ["heartbeat"] as const

export const useHeartbeat = () => {
  return useQuery({
    queryKey: HEARTBEAT_QUERY_KEY,
    queryFn: HeartbeatApi.check,
  })
}
