import { Alert, Center, Loader, SimpleGrid, Text } from "@mantine/core"
import type { RecipeSearchRequestDto } from "@/apis/recipes/dtos/RecipeDtos"
import { useRecipeSearch } from "@/apis/recipes/useRecipes"
import { RecipeCard } from "./RecipeCard"

interface RecipeResultsProps {
  request: RecipeSearchRequestDto
}

export function RecipeResults({ request }: RecipeResultsProps) {
  const { data: recipes, isLoading, isError, error } = useRecipeSearch(request)

  if (isLoading) {
    return (
      <Center py="xl">
        <Loader />
      </Center>
    )
  }
  if (isError) {
    return (
      <Alert color="red" title="La recherche a échoué">
        {error instanceof Error ? error.message : "Erreur inconnue"}
      </Alert>
    )
  }
  if (!recipes?.length) {
    return <Text c="dimmed">Aucune recette trouvée.</Text>
  }
  return (
    <SimpleGrid cols={{ base: 1, lg: 3, sm: 2 }} spacing="md">
      {recipes.map((recipe) => (
        <RecipeCard key={recipe.identifiant} recipe={recipe} />
      ))}
    </SimpleGrid>
  )
}
