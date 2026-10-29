import {
  Alert,
  Anchor,
  Badge,
  Center,
  Container,
  Grid,
  Group,
  List,
  Loader,
  Stack,
  Text,
  Title,
} from "@mantine/core"
import { ArrowLeft } from "lucide-react"
import { useState } from "react"
import { Link, useParams } from "react-router"
import type { IngredientCandidateDto } from "@/apis/ingredients/dtos/IngredientDtos"
import {
  DEFAULT_MATCHING_PREFERENCES,
  type MatchingPreferences,
} from "@/apis/matching/matchingPreferences"
import type { RecipeIngredientDto } from "@/apis/recipes/dtos/RecipeDtos"
import { useRecipeDetail } from "@/apis/recipes/useRecipes"
import { HttpError } from "@/shared/utils/http"
import { IngredientMatchModal } from "./recipes/IngredientMatchModal"
import { MatchingPreferencesPanel } from "./recipes/MatchingPreferencesPanel"
import { RecipeIngredientList } from "./recipes/RecipeIngredientList"

export function RecipeDetailPage() {
  const { identifiant } = useParams<{ identifiant: string }>()
  const {
    data: recipe,
    isLoading,
    isError,
    error,
  } = useRecipeDetail(identifiant)
  const [matches, setMatches] = useState<
    Record<string, IngredientCandidateDto>
  >({})
  const [selected, setSelected] = useState<RecipeIngredientDto | null>(null)
  const [preferences, setPreferences] = useState<MatchingPreferences>(
    DEFAULT_MATCHING_PREFERENCES,
  )

  const recordMatch = (
    ingredientKey: string,
    candidate: IngredientCandidateDto,
  ) => {
    setMatches((current) => ({ ...current, [ingredientKey]: candidate }))
  }

  return (
    <Container py="xl" size="lg">
      <Stack gap="lg">
        <Anchor component={Link} to="/">
          <Group gap={4}>
            <ArrowLeft size={16} />
            <Text>Retour aux recettes</Text>
          </Group>
        </Anchor>

        {isLoading && (
          <Center py="xl">
            <Loader />
          </Center>
        )}

        {isError &&
          (error instanceof HttpError && error.status === 404 ? (
            <Text c="dimmed">Cette recette est introuvable.</Text>
          ) : (
            <Alert color="red" title="Chargement de la recette impossible">
              {error instanceof Error ? error.message : "Erreur inconnue"}
            </Alert>
          ))}

        {recipe && (
          <>
            <div>
              <Title order={2}>{recipe.nom}</Title>
              {recipe.description && (
                <Text c="dimmed" mt="xs">
                  {recipe.description}
                </Text>
              )}
              <Group gap={6} mt="sm">
                {recipe.type.map((type) => (
                  <Badge key={type} size="sm" variant="light">
                    {type}
                  </Badge>
                ))}
              </Group>
            </div>

            <Grid gap="lg">
              <Grid.Col span={{ base: 12, md: 8 }}>
                <Stack gap="lg">
                  <div>
                    <Title order={4} mb="sm">
                      Ingrédients
                    </Title>
                    <RecipeIngredientList
                      ingredients={recipe.ingredients}
                      matches={matches}
                      onMatch={setSelected}
                    />
                  </div>

                  <div>
                    <Title order={4} mb="sm">
                      Préparation
                    </Title>
                    {recipe.etapes.length > 0 ? (
                      <List spacing="sm" type="ordered">
                        {recipe.etapes.map((step, index) => (
                          // Steps have no stable id; order is their identity.
                          <List.Item key={`${index}-${step.slice(0, 16)}`}>
                            {step}
                          </List.Item>
                        ))}
                      </List>
                    ) : (
                      <Text c="dimmed">Aucune instruction disponible.</Text>
                    )}
                  </div>
                </Stack>
              </Grid.Col>

              <Grid.Col span={{ base: 12, md: 4 }}>
                <MatchingPreferencesPanel
                  onChange={setPreferences}
                  preferences={preferences}
                />
              </Grid.Col>
            </Grid>
          </>
        )}
      </Stack>

      <IngredientMatchModal
        ingredient={selected}
        onClose={() => setSelected(null)}
        onMatch={recordMatch}
        preferences={preferences}
      />
    </Container>
  )
}
