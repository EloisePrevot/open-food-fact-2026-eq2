import { Autocomplete, Card, Select, Stack, Text } from "@mantine/core"
import { useDebouncedValue } from "@mantine/hooks"
import { useState } from "react"
import type { MatchingPreferences } from "@/apis/matching/matchingPreferences"
import { useBrandSuggestions } from "@/apis/matching/useBrands"

interface MatchingPreferencesPanelProps {
  preferences: MatchingPreferences
  onChange: (preferences: MatchingPreferences) => void
}

const NUTRI_SCORE_OPTIONS = [
  { label: "A", value: "a" },
  { label: "B", value: "b" },
  { label: "C", value: "c" },
  { label: "D", value: "d" },
  { label: "E", value: "e" },
]

const NOVA_OPTIONS = [
  { label: "1 - Non transformé", value: "1" },
  { label: "2 - Ingrédient culinaire", value: "2" },
  { label: "3 - Transformé", value: "3" },
  { label: "4 - Ultra-transformé", value: "4" },
]

const BASE_PRODUCT_OPTIONS = [
  { label: "Produits de base", value: "base" },
  { label: "Produits de marque", value: "marque" },
]

function toBaseProduct(value: string | null): boolean | null {
  if (value === "base") {
    return true
  }
  if (value === "marque") {
    return false
  }
  return null
}

function fromBaseProduct(value: boolean | null): string | null {
  if (value === true) {
    return "base"
  }
  if (value === false) {
    return "marque"
  }
  return null
}

const BRAND_DEBOUNCE_MS = 250

export function MatchingPreferencesPanel({
  preferences,
  onChange,
}: MatchingPreferencesPanelProps) {
  const update = (patch: Partial<MatchingPreferences>) =>
    onChange({ ...preferences, ...patch })

  const [brandQuery, setBrandQuery] = useState(preferences.marque ?? "")
  const [debouncedBrandQuery] = useDebouncedValue(brandQuery, BRAND_DEBOUNCE_MS)
  const { data: brandSuggestions = [] } =
    useBrandSuggestions(debouncedBrandQuery)

  const changeBrand = (value: string) => {
    setBrandQuery(value)
    update({ marque: value.trim() || null })
  }

  return (
    <Card padding="md" withBorder>
      <Text fw={600} mb="sm">
        Préférences d'appariement
      </Text>
      <Stack gap="sm">
        <Autocomplete
          data={brandSuggestions}
          label="Préférence de marque"
          onChange={changeBrand}
          placeholder="Toutes les marques"
          value={brandQuery}
        />
        <Select
          clearable
          data={NUTRI_SCORE_OPTIONS}
          label="Qualité nutritionnelle (Nutri-Score minimal)"
          onChange={(value) => update({ nutriScoreMin: value })}
          placeholder="Toutes les qualités"
          value={preferences.nutriScoreMin}
        />
        <Select
          clearable
          data={NOVA_OPTIONS}
          label="Degré de transformation (Nova maximal)"
          onChange={(value) =>
            update({ novaMax: value === null ? null : Number(value) })
          }
          placeholder="Tous les degrés"
          value={
            preferences.novaMax === null ? null : String(preferences.novaMax)
          }
        />
        <Select
          clearable
          data={BASE_PRODUCT_OPTIONS}
          label="Type de produit"
          onChange={(value) =>
            update({ preferenceProduitDeBase: toBaseProduct(value) })
          }
          placeholder="Tous les produits"
          value={fromBaseProduct(preferences.preferenceProduitDeBase)}
        />
      </Stack>
    </Card>
  )
}
