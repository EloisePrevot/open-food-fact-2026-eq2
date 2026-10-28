import { AppShell, Group, Title } from "@mantine/core"
import { Route, Routes } from "react-router"
import { HeartbeatStatus } from "./components/HeartbeatStatus"
import { HomePage } from "./pages/Home"

const App = () => {
  return (
    <AppShell header={{ height: 72 }} padding={0}>
      <AppShell.Header>
        <Group h="100%" justify="space-between" px="lg">
          <Title order={3}>Open Food Facts Québec</Title>
          <HeartbeatStatus />
        </Group>
      </AppShell.Header>
      <AppShell.Main>
        <Routes>
          <Route element={<HomePage />} path="/" />
        </Routes>
      </AppShell.Main>
    </AppShell>
  )
}

export default App
