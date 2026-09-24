import { API_BASE_URL } from "@/shared/config/apiConfig";
import { ensureSuccess } from "@/shared/utils/http";
import type { HeartbeatDto } from "../dtos/HeartBeatDto";

const HEARTBEAT_ENDPOINT = `${API_BASE_URL}/heartbeat`;

export const heartbeatRequests = {
	get: async (): Promise<HeartbeatDto> => {
		const response = await fetch(HEARTBEAT_ENDPOINT, {
			headers: { Accept: "application/json" },
		});

		await ensureSuccess(response);

		return (await response.json()) as HeartbeatDto;
	},
};
