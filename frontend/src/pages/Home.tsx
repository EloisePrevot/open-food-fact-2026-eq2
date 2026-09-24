import { Alert, Badge, Group, Loader, Stack, Text, Title } from "@mantine/core"
import { useHeartbeat } from "@/apis/heartbeat/useHeartbeat"

export function HomePage() {
  const { data, isLoading, isError, error } = useHeartbeat()

  return (
    <Stack p="xl" gap="md">
      <Title order={2}>Backend connectivity</Title>

      {isLoading && (
        <Group gap="xs">
          <Loader size="sm" />
          <Text>Checking the backend heartbeat...</Text>
        </Group>
      )}

      {isError && (
        <Alert color="red" title="Backend unreachable">
          {error instanceof Error ? error.message : "Unknown error"}
        </Alert>
      )}

      {data && (
        <Group gap="xs">
          <Badge color="green">Connected</Badge>
          <Text>
            Application: <strong>{data.nomApplication}</strong>
          </Text>
        </Group>
      )}
    </Stack>
  )
}
