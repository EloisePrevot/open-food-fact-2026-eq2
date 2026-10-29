export interface IngredientMatchRequestDto {
  ingredient: string
  produitDeBase: boolean | null
  marque: string | null
  nutriScoreMin: string | null
  novaMax: number | null
  limite: number
}

export interface IngredientCandidateDto {
  identifiant: string
  nomProduit: string
  score: number
  produitDeBase: boolean
  nutriScore: string | null
  nova: number | null
  marques: string[]
}

export interface IngredientMatchResponseDto {
  ingredient: string
  candidats: IngredientCandidateDto[]
}
