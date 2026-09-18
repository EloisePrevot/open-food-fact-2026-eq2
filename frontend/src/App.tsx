import { AppShell } from "@mantine/core"
import { Route, Routes } from "react-router"
import { HomePage } from "./pages/Home"

const App = () => {
  return (
    <AppShell header={{ height: 72 }} padding={0}>
      <AppShell.Header>Header here</AppShell.Header>
      <AppShell.Main>
        <Routes>
          <Route path="/" element={<HomePage />} />
        </Routes>
      </AppShell.Main>
    </AppShell>
  )
}

export default App
