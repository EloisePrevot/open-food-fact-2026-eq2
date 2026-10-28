import { Badge, Card, Group, Text } from "@mantine/core"
import type { RecipeSummaryDto } from "@/apis/recipes/dtos/RecipeDtos"

interface RecipeCardProps {
  recipe: RecipeSummaryDto
}

export function RecipeCard({ recipe }: RecipeCardProps) {
  return (
    <Card padding="md" withBorder>
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
