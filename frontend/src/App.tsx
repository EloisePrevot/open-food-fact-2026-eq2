import { Anchor, AppShell, Group, Title } from "@mantine/core"
import { Link, Route, Routes } from "react-router"
import { HeartbeatStatus } from "./components/HeartbeatStatus"
import { HomePage } from "./pages/Home"
import { IngredientsPage } from "./pages/Ingredients"
import { RecipeDetailPage } from "./pages/RecipeDetail"

const App = () => {
  return (
    <AppShell header={{ height: 72 }} padding={0}>
      <AppShell.Header>
        <Group h="100%" justify="space-between" px="lg">
          <Group gap="xl">
            <Title order={3}>Open Food Facts Québec</Title>
            <Group gap="md">
              <Anchor component={Link} to="/">
                Recettes
              </Anchor>
              <Anchor component={Link} to="/ingredients">
                Ingrédients
              </Anchor>
            </Group>
          </Group>
          <HeartbeatStatus />
        </Group>
      </AppShell.Header>
      <AppShell.Main>
        <Routes>
          <Route element={<HomePage />} path="/" />
          <Route element={<RecipeDetailPage />} path="/recettes/:identifiant" />
          <Route element={<IngredientsPage />} path="/ingredients" />
        </Routes>
      </AppShell.Main>
    </AppShell>
  )
}

export default App
