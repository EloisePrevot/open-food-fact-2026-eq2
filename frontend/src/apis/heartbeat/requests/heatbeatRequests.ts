import type { HeartbeatDto } from "../dtos/HeartBeatDto"

export const heartbeatRequests = {
  get: async (): Promise<HeartbeatDto> => {
    throw new Error("TODO: implement removing a call")
  },
}
