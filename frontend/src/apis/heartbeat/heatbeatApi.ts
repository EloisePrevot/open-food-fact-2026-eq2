import type { HeartbeatDto } from "./dtos/HeartBeatDto"
import { heartbeatRequests } from "./requests/heatbeatRequests"

export const HeartbeatApi = {
  check: async (): Promise<HeartbeatDto> => {
    return await heartbeatRequests.get()
  },
}
