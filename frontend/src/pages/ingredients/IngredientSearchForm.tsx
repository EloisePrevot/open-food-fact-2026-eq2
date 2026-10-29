import { Button, Group, Select, TextInput } from "@mantine/core"
import { Search } from "lucide-react"
import { type FormEvent, useState } from "react"

export interface IngredientSearchCriteria {
  ingredient: string
  produitDeBase: boolean | null
}

interface IngredientSearchFormProps {
  onSearch: (criteria: IngredientSearchCriteria) => void
}

const BASIC_FOOD_OPTION = "base"
const BRANDED_OPTION = "marque"

const PRODUCT_TYPE_OPTIONS = [
  { label: "Produits de base", value: BASIC_FOOD_OPTION },
  { label: "Produits de marque", value: BRANDED_OPTION },
]

const toProduitDeBase = (value: string | null): boolean | null => {
  if (value === BASIC_FOOD_OPTION) {
    return true
  }
  if (value === BRANDED_OPTION) {
    return false
  }
  return null
}

export function IngredientSearchForm({ onSearch }: IngredientSearchFormProps) {
  const [ingredient, setIngredient] = useState("")
  const [productType, setProductType] = useState<string | null>(null)

  const submit = (event: FormEvent) => {
    event.preventDefault()
    onSearch({
      ingredient: ingredient.trim(),
      produitDeBase: toProduitDeBase(productType),
    })
  }

  return (
    <form onSubmit={submit}>
      <Group align="flex-end" gap="sm" wrap="wrap">
        <TextInput
          aria-label="Ingrédient d'une recette"
          flex={1}
          leftSection={<Search size={16} />}
          miw={240}
          onChange={(event) => setIngredient(event.currentTarget.value)}
          placeholder="Ex. : deux tasses de farine tout usage"
          size="md"
          value={ingredient}
        />
        <Select
          aria-label="Type de produit"
          clearable
          data={PRODUCT_TYPE_OPTIONS}
          onChange={setProductType}
          placeholder="Tous les produits"
          size="md"
          value={productType}
          w={200}
        />
        <Button size="md" type="submit">
          Apparier
        </Button>
      </Group>
    </form>
  )
}
