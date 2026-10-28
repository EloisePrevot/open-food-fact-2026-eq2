export interface RecipeSearchRequestDto {
  typeRecette: string | null
  description: string | null
  limite: number
}

export interface RecipeSummaryDto {
  identifiant: string
  nom: string
  type: string[]
  nbIngredients: number
  score: number | null
}

export interface RecipeSearchResponseDto {
  recettes: RecipeSummaryDto[]
}

export interface RecipeTypesDto {
  typesRecette: string[]
}
