import { Badge, Card, Group, Text } from "@mantine/core"
import type { KeyboardEvent } from "react"
import type { IngredientCandidateDto } from "@/apis/ingredients/dtos/IngredientDtos"

interface IngredientCardProps {
  candidate: IngredientCandidateDto
  onSelect: (candidate: IngredientCandidateDto) => void
}

const NUTRI_SCORE_COLORS: Record<string, string> = {
  a: "green",
  b: "lime",
  c: "yellow",
  d: "orange",
  e: "red",
}

function nutriScoreColor(grade: string): string {
  return NUTRI_SCORE_COLORS[grade.toLowerCase()] ?? "gray"
}

export function IngredientCard({ candidate, onSelect }: IngredientCardProps) {
  const select = () => onSelect(candidate)

  const selectOnKey = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault()
      select()
    }
  }

  const brands = candidate.marques.slice(0, 2)

  return (
    <Card
      aria-label={`Voir les détails de ${candidate.nomProduit}`}
      onClick={select}
      onKeyDown={selectOnKey}
      padding="md"
      role="button"
      style={{ cursor: "pointer" }}
      tabIndex={0}
      withBorder
    >
      <Text fw={600} lineClamp={2}>
        {candidate.nomProduit}
      </Text>
      <Text c="dimmed" mt={2} size="sm">
        {brands.length > 0 ? brands.join(", ") : "Marque inconnue"}
      </Text>
      <Group gap={6} mt="xs">
        <Badge
          color={candidate.produitDeBase ? "teal" : "blue"}
          size="sm"
          variant="light"
        >
          {candidate.produitDeBase ? "Produit de base" : "Produit de marque"}
        </Badge>
      </Group>
      <Group gap={6} mt="xs">
        {candidate.nutriScore ? (
          <Badge
            color={nutriScoreColor(candidate.nutriScore)}
            size="sm"
            variant="filled"
          >
            Nutri-Score {candidate.nutriScore.toUpperCase()}
          </Badge>
        ) : (
          <Badge color="gray" size="sm" variant="light">
            Nutri-Score inconnu
          </Badge>
        )}
        {candidate.nova !== null ? (
          <Badge color="grape" size="sm" variant="light">
            NOVA {candidate.nova}
          </Badge>
        ) : (
          <Badge color="gray" size="sm" variant="light">
            NOVA inconnu
          </Badge>
        )}
      </Group>
      <Group c="dimmed" justify="flex-end" mt="sm">
        <Text size="sm">Similarité {candidate.score.toFixed(2)}</Text>
      </Group>
    </Card>
  )
}
