import { Container, Stack, Text, Title } from "@mantine/core"
import { useState } from "react"
import type { IngredientMatchRequestDto } from "@/apis/ingredients/dtos/IngredientDtos"
import { IngredientResults } from "./ingredients/IngredientResults"
import {
  type IngredientSearchCriteria,
  IngredientSearchForm,
} from "./ingredients/IngredientSearchForm"

const RESULT_LIMIT = 12

const INITIAL_REQUEST: IngredientMatchRequestDto = {
  ingredient: "",
  limite: RESULT_LIMIT,
  marque: null,
  novaMax: null,
  nutriScoreMin: null,
  produitDeBase: null,
}

export function IngredientsPage() {
  const [request, setRequest] = useState(INITIAL_REQUEST)

  const search = (criteria: IngredientSearchCriteria) => {
    setRequest({
      ...INITIAL_REQUEST,
      ...criteria,
      limite: RESULT_LIMIT,
    })
  }

  return (
    <Container py="xl" size="lg">
      <Stack gap="lg">
        <div>
          <Title order={2}>Apparier un ingrédient</Title>
          <Text c="dimmed">
            Entrez un ingrédient de recette pour trouver les produits à acheter.
          </Text>
        </div>
        <IngredientSearchForm onSearch={search} />
        <IngredientResults request={request} />
      </Stack>
    </Container>
  )
}
