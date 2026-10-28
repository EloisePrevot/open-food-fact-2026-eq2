import { Badge, Loader } from "@mantine/core"
import { useHeartbeat } from "@/apis/heartbeat/useHeartbeat"

export function HeartbeatStatus() {
  const { data, isLoading, isError } = useHeartbeat()

  if (isLoading) {
    return <Loader size="xs" />
  }
  if (isError || !data) {
    return <Badge color="red">API hors ligne</Badge>
  }
  return <Badge color="green">{data.nomApplication}</Badge>
}
