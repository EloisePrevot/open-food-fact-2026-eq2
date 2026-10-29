import { Alert, Center, Loader, SimpleGrid, Text } from "@mantine/core"
import { useState } from "react"
import type {
  IngredientCandidateDto,
  IngredientMatchRequestDto,
} from "@/apis/ingredients/dtos/IngredientDtos"
import { useIngredientMatch } from "@/apis/ingredients/useIngredients"
import { IngredientCard } from "./IngredientCard"
import { IngredientDetailModal } from "./IngredientDetailModal"

interface IngredientResultsProps {
  request: IngredientMatchRequestDto
}

export function IngredientResults({ request }: IngredientResultsProps) {
  const [selected, setSelected] = useState<IngredientCandidateDto | null>(null)
  const {
    data: candidates,
    isLoading,
    isError,
    error,
  } = useIngredientMatch(request)

  if (request.ingredient.trim().length === 0) {
    return (
      <Text c="dimmed">
        Entrez un ingrédient pour voir les produits correspondants.
      </Text>
    )
  }
  if (isLoading) {
    return (
      <Center py="xl">
        <Loader />
      </Center>
    )
  }
  if (isError) {
    return (
      <Alert color="red" title="L'appariement a échoué">
        {error instanceof Error ? error.message : "Erreur inconnue"}
      </Alert>
    )
  }
  if (!candidates?.length) {
    return <Text c="dimmed">Aucun produit correspondant.</Text>
  }
  return (
    <>
      <SimpleGrid cols={{ base: 1, lg: 3, sm: 2 }} spacing="md">
        {candidates.map((candidate) => (
          <IngredientCard
            candidate={candidate}
            key={candidate.identifiant}
            onSelect={setSelected}
          />
        ))}
      </SimpleGrid>
      <IngredientDetailModal
        candidate={selected}
        onClose={() => setSelected(null)}
      />
    </>
  )
}
