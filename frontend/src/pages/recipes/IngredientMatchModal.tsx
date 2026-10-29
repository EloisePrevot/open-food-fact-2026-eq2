import {
  Alert,
  Center,
  Loader,
  Modal,
  SimpleGrid,
  Stack,
  Text,
} from "@mantine/core"
import { useMemo } from "react"
import type {
  IngredientCandidateDto,
  IngredientMatchRequestDto,
} from "@/apis/ingredients/dtos/IngredientDtos"
import { useIngredientMatch } from "@/apis/ingredients/useIngredients"
import type { MatchingPreferences } from "@/apis/matching/matchingPreferences"
import type { RecipeIngredientDto } from "@/apis/recipes/dtos/RecipeDtos"
import { IngredientCard } from "@/pages/ingredients/IngredientCard"

const CANDIDATE_LIMIT = 9

interface IngredientMatchModalProps {
  ingredient: RecipeIngredientDto | null
  preferences: MatchingPreferences
  onClose: () => void
  onMatch: (ingredientKey: string, candidate: IngredientCandidateDto) => void
}

export function IngredientMatchModal({
  ingredient,
  preferences,
  onClose,
  onMatch,
}: IngredientMatchModalProps) {
  const request = useMemo<IngredientMatchRequestDto>(
    () => ({
      ingredient: ingredient?.nom ?? "",
      limite: CANDIDATE_LIMIT,
      marque: preferences.marque,
      novaMax: preferences.novaMax,
      nutriScoreMin: preferences.nutriScoreMin,
      produitDeBase: preferences.preferenceProduitDeBase,
    }),
    [ingredient, preferences],
  )
  const {
    data: candidates,
    isLoading,
    isError,
    error,
  } = useIngredientMatch(request)

  const select = (candidate: IngredientCandidateDto) => {
    if (ingredient !== null) {
      onMatch(ingredient.cle, candidate)
      onClose()
    }
  }

  return (
    <Modal
      onClose={onClose}
      opened={ingredient !== null}
      size="xl"
      title={ingredient !== null ? `Apparier « ${ingredient.nom} »` : undefined}
    >
      <Stack gap="md">
        {ingredient !== null && (
          <Text c="dimmed" size="sm">
            {ingredient.texteOriginal}
          </Text>
        )}
        {isLoading && (
          <Center py="xl">
            <Loader />
          </Center>
        )}
        {isError && (
          <Alert color="red" title="L'appariement a échoué">
            {error instanceof Error ? error.message : "Erreur inconnue"}
          </Alert>
        )}
        {!isLoading && !isError && !candidates?.length && (
          <Text c="dimmed">Aucun produit correspondant.</Text>
        )}
        {candidates && candidates.length > 0 && (
          <SimpleGrid cols={{ base: 1, lg: 3, sm: 2 }} spacing="md">
            {candidates.map((candidate) => (
              <IngredientCard
                candidate={candidate}
                key={candidate.identifiant}
                onSelect={select}
              />
            ))}
          </SimpleGrid>
        )}
      </Stack>
    </Modal>
  )
}
