import { Button, Group, Select, TextInput } from "@mantine/core"
import { Search } from "lucide-react"
import { type FormEvent, useState } from "react"
import { useRecipeTypes } from "@/apis/recipes/useRecipes"

export interface RecipeSearchCriteria {
  description: string | null
  typeRecette: string | null
}

interface RecipeSearchFormProps {
  onSearch: (criteria: RecipeSearchCriteria) => void
}

export function RecipeSearchForm({ onSearch }: RecipeSearchFormProps) {
  const [description, setDescription] = useState("")
  const [typeRecette, setTypeRecette] = useState<string | null>(null)
  const { data: types = [] } = useRecipeTypes()

  const submit = (event: FormEvent) => {
    event.preventDefault()
    onSearch({ description: description.trim() || null, typeRecette })
  }

  return (
    <form onSubmit={submit}>
      <Group align="flex-end" gap="sm" wrap="wrap">
        <TextInput
          aria-label="Description de la recette"
          flex={1}
          leftSection={<Search size={16} />}
          miw={240}
          onChange={(event) => setDescription(event.currentTarget.value)}
          placeholder="Ex. : quelque chose de réconfortant pour un souper d'hiver"
          size="md"
          value={description}
        />
        <Select
          aria-label="Type de recette"
          clearable
          data={types}
          onChange={setTypeRecette}
          placeholder="Tous les types"
          size="md"
          value={typeRecette}
          w={180}
        />
        <Button size="md" type="submit">
          Rechercher
        </Button>
      </Group>
    </form>
  )
}
