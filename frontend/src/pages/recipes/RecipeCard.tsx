import { Badge, Card, Group, Text } from "@mantine/core"
import type { KeyboardEvent } from "react"
import { useNavigate } from "react-router"
import type { RecipeSummaryDto } from "@/apis/recipes/dtos/RecipeDtos"

interface RecipeCardProps {
  recipe: RecipeSummaryDto
}

export function RecipeCard({ recipe }: RecipeCardProps) {
  const navigate = useNavigate()

  const open = () =>
    navigate(`/recettes/${encodeURIComponent(recipe.identifiant)}`)

  const openOnKey = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault()
      open()
    }
  }

  return (
    <Card
      aria-label={`Voir la recette ${recipe.nom}`}
      onClick={open}
      onKeyDown={openOnKey}
      padding="md"
      role="button"
      style={{ cursor: "pointer" }}
      tabIndex={0}
      withBorder
    >
      <Text fw={600} lineClamp={2}>
        {recipe.nom}
      </Text>
      <Group gap={6} mt="xs">
        {recipe.type.map((type) => (
          <Badge key={type} size="sm" variant="light">
            {type}
          </Badge>
        ))}
      </Group>
      <Group c="dimmed" justify="space-between" mt="sm">
        <Text size="sm">{recipe.nbIngredients} ingrédients</Text>
        {recipe.score !== null && (
          <Text size="sm">Similarité {recipe.score.toFixed(2)}</Text>
        )}
      </Group>
    </Card>
  )
}
