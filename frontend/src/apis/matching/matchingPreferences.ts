export interface MatchingPreferences {
  marque: string | null
  nutriScoreMin: string | null
  novaMax: number | null
  preferenceProduitDeBase: boolean | null
}

export const DEFAULT_MATCHING_PREFERENCES: MatchingPreferences = {
  marque: null,
  novaMax: null,
  nutriScoreMin: null,
  preferenceProduitDeBase: null,
}
