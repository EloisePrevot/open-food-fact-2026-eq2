import { Container, Stack, Text, Title } from "@mantine/core"
import { useState } from "react"
import type { RecipeSearchRequestDto } from "@/apis/recipes/dtos/RecipeDtos"
import { RecipeResults } from "./recipes/RecipeResults"
import {
  type RecipeSearchCriteria,
  RecipeSearchForm,
} from "./recipes/RecipeSearchForm"

const RESULT_LIMIT = 12

const INITIAL_REQUEST: RecipeSearchRequestDto = {
  description: null,
  limite: RESULT_LIMIT,
  typeRecette: null,
}

export function HomePage() {
  const [request, setRequest] = useState(INITIAL_REQUEST)

  const search = (criteria: RecipeSearchCriteria) => {
    setRequest({ ...criteria, limite: RESULT_LIMIT })
  }

  return (
    <Container py="xl" size="lg">
      <Stack gap="lg">
        <div>
          <Title order={2}>Trouver une recette</Title>
          <Text c="dimmed">
            Décrivez ce que vous avez envie de manger, en vos propres mots.
          </Text>
        </div>
        <RecipeSearchForm onSearch={search} />
        <RecipeResults request={request} />
      </Stack>
    </Container>
  )
}
