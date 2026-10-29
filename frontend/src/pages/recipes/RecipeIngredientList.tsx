import { Badge, Button, Card, Group, Stack, Text } from "@mantine/core"
import { Link2 } from "lucide-react"
import type { IngredientCandidateDto } from "@/apis/ingredients/dtos/IngredientDtos"
import type { RecipeIngredientDto } from "@/apis/recipes/dtos/RecipeDtos"

interface RecipeIngredientListProps {
  ingredients: RecipeIngredientDto[]
  matches: Record<string, IngredientCandidateDto>
  onMatch: (ingredient: RecipeIngredientDto) => void
}

export function RecipeIngredientList({
  ingredients,
  matches,
  onMatch,
}: RecipeIngredientListProps) {
  return (
    <Stack gap="sm">
      {ingredients.map((ingredient) => {
        const match = matches[ingredient.cle]
        return (
          <Card key={ingredient.cle} padding="sm" withBorder>
            <Group justify="space-between" wrap="nowrap">
              <div>
                <Text fw={500}>{ingredient.nom}</Text>
                <Text c="dimmed" size="sm">
                  {ingredient.texteOriginal}
                </Text>
                {match && (
                  <Badge color="teal" mt={6} variant="light">
                    Apparié : {match.nomProduit}
                  </Badge>
                )}
              </div>
              <Button
                leftSection={<Link2 size={16} />}
                onClick={() => onMatch(ingredient)}
                variant={match ? "light" : "filled"}
              >
                {match ? "Changer" : "Apparier l'ingrédient"}
              </Button>
            </Group>
          </Card>
        )
      })}
    </Stack>
  )
}
