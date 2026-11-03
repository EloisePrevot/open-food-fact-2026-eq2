## Lancer le projet

- Prérequis : Docker
- Données : téléchargées depuis la Release GitHub `snapshots`, (`elt/raw/` inutile sauf pour commencé de 0)
- Premier lancement : ~2-5 min (build des images + restauration PostgreSQL, MongoDB, Qdrant)
- Prêt quand `/heartbeat` répond 200
- API : `http://localhost` (port 80) · Frontend : `http://localhost:8081`

```sh
docker compose up -d --build
curl http://localhost/heartbeat
docker compose down        # arrêter
docker compose down -v     # effacer les données, puis relancer up -d --build
```

---

## Routes

### `GET /heartbeat`

- Paquet : aucun

```json
{"nomApplication": "Open Food Facts"}
```

### `GET /extracted_data`

- Paquet : aucun
- Format : nombre d'enregistrements bruts stockés, par source

```json
{"nbProduitsAlimentairesScannes": 51429, "nbProduitsAlimentairesDeBase": 5690, "nbRecettesCuisine": 10000}
```

### `GET /transformed_data`

- Paquet : aucun
- Format : `indicateursDeQualite` = nb de produits ayant chaque indicateur ; `categoriesProduitAlimentaire` = nb de produits par catégorie

```json
{
  "indicateursDeQualite": {"NutriScore": 42256, "Nova": 35259, "EcoScore": 16547},
  "categoriesProduitAlimentaire": {
    "Légumes et produits végétaux": 785,
    "Produits de boulangerie": 441,
    "Produits de volaille": 418,
    "...": "..."
  }
}
```

### `GET /donnees_brutes/{identifiant}`

- Paquet : aucun
- Identifiants : `off:<code-barres>` · `cnf:<FoodID>` · `recipe:<hash>`
- Format : `chargeUtile` = enregistrement tel qu'acquis (noms, langues, valeurs vides d'origine)
- Identifiant inexistant : 404

```json
{
  "identifiant": "off:00000028",
  "source": "open_food_facts",
  "dateIngestion": "2026-11-03T03:25:47Z",
  "chargeUtile": {
    "url": "http://world-en.openfoodfacts.org/product/00000028/hershey-s-syrup",
    "code": "00000028",
    "owner": "",
    "brands": "Hershey’s",
    "...": "..."
  }
}
```

Autres sources :

| Identifiant | `source` | Début de `chargeUtile` |
| --- | --- | --- |
| `cnf:2` | `canadian_nutrient_file` | `{"FoodID": "2", "FoodCode": "2", "CountryCode": "", ...}` |
| `recipe:d05b7086851f9c45d10cb57e437ea1988e9c21897a26aabffabd4684a1946f07` | `extended_recipes_dataset` | `{"tastes": ["spicy", "bitter", "savory"], "category": "Air Fryer Recipes", ...}` |

```json
{"message": "Aucun enregistrement pour l'identifiant off:inexistant"}
```

### `GET /readme`

- Paquet : aucun
- Format : texte, contenu de `README.md`

### `GET /type`

- Paquet : aucun

```json
{
  "typesRecette": ["Accompagnement", "Boisson", "Collation", "Dessert", "Déjeuner",
                   "Entrée", "Pain", "Plat principal", "Sauce", "Soupe"]
}
```

### `POST /apparier_ingredient`

- Paquet :

```json
{"ingredient": "500 ml de lait 2 %", "produitDeBase": null, "limite": 2}
```

- Format : candidats triés par score décroissant ; `produitDeBase` null = aucun filtre
- Notre réponse ajoute `nutriScore`, `nova`, `marques` à chaque candidat

```json
{
  "ingredient": "500 ml de lait 2 %",
  "candidats": [
    {
      "identifiant": "off:0055872025187",
      "nomProduit": "Lait 2%",
      "score": 0.7905,
      "produitDeBase": false,
      "nutriScore": "b",
      "nova": 1,
      "marques": ["Québon"]
    },
    {
      "identifiant": "off:0041220667895",
      "nomProduit": "Reduced fat milk 2%",
      "score": 0.7729,
      "produitDeBase": false,
      "nutriScore": "b",
      "nova": null,
      "marques": ["2%"]
    }
  ]
}
```

### `POST /recette`

- Paquet : `{"typeRecette": str | null, "description": str | null, "limite": int}`
- Format : `typeRecette` filtre, `description` classe ; `description` null = `score` null, sans ordre imposé

Avec description :

```json
{"typeRecette": null, "description": "un plat léger à préparer en vingt minutes", "limite": 2}
```

```json
{
  "recettes": [
    {
      "identifiant": "recipe:7fef2c8a2ec6976017aa76d35d4a3fa70a67343a8ce414dd5a62566d6dc2823c",
      "nom": "Croustillant Tex-Mex Casserole avec rainure de ranch épicé",
      "type": ["Déjeuner", "Plat principal", "Accompagnement", "Soupe", "Collation", "Pain"],
      "nbIngredients": 11,
      "score": 0.6392
    },
    {
      "identifiant": "recipe:620b37473b0d0b74f1686fd33525e70b7bbbdd2ad410d43d18ac333abe1d9ee2",
      "nom": "Parmesan Polenta crémeux",
      "type": ["Soupe"],
      "nbIngredients": 5,
      "score": 0.6344
    }
  ]
}
```

Type seul:

```json
{"typeRecette": "Dessert", "description": null, "limite": 2}
```

```json
{
  "recettes": [
    {
      "identifiant": "recipe:5f6570e515de374e8c05bbdc55351c3212286114f27c7a5b53f9ca8e49397de1",
      "nom": "Air Fryer S'Mores",
      "type": ["Dessert"],
      "nbIngredients": 3,
      "score": null
    },
    {
      "identifiant": "recipe:c2a47795ad9b3e1408e3f1837d91c8bb3e66a4774d4b1188d75b2c1b43429adb",
      "nom": "Mini gâteau au chocolat noir avec gel de beurre brun",
      "type": ["Dessert"],
      "nbIngredients": 13,
      "score": null
    }
  ]
}
```

### `POST /cuisiner`

- Paquet :

```json
{
  "identifiantRecette": "recipe:d05b7086851f9c45d10cb57e437ea1988e9c21897a26aabffabd4684a1946f07",
  "marque": null,
  "nutriScoreMin": null,
  "novaMax": null,
  "preferenceProduitDeBase": null,
  "limiteParIngredient": 1
}
```

- Format : produits recommandés par ingrédient ; `ingredientsSansCorrespondance` = ingrédients sans produit qui respecte les filtres

```json
{
  "identifiantRecette": "recipe:d05b7086851f9c45d10cb57e437ea1988e9c21897a26aabffabd4684a1946f07",
  "nomRecette": "Tranches de pommes de terre de friteuse d'air avec sauce à tremper",
  "ingredients": [
    {
      "ingredientTexte": "3/4 cup ketchup",
      "produits": [
        {
          "identifiant": "off:0020502161511",
          "nomProduit": "Spicy jerk ketchup",
          "marque": null,
          "nutriScore": "d",
          "nova": null,
          "produitDeBase": false,
          "score": 0.7757
        }
      ]
    },
    {
      "ingredientTexte": "1/2 cup beer",
      "produits": [
        {
          "identifiant": "off:9507200193873",
          "nomProduit": "cerveza",
          "marque": "cerveza",
          "nutriScore": null,
          "nova": null,
          "produitDeBase": false,
          "score": 0.8169
        }
      ]
    },
    "..."
  ],
  "ingredientsSansCorrespondance": []
}
```

---

## Échelle des scores de similarité

- Score = similarité cosinus renvoyée par Qdrant, non transformée par le backend
- Modèle : `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions, cosinus)
- Bornes : -1 à 1 ; plus haut = plus similaire ; listes triées par score décroissant
- Même échelle pour `/apparier_ingredient`, `/recette` et `/cuisiner`
- `/recette` : `score` null quand `description` est null

### Mesures 

`/apparier_ingredient`, 10 cas publiés, `limite` 5:

*Note: pour chaque ingrédient, on met le score du meilleur candidat (1er) et du dernier des 5 (5e), soit la plage de scores d'une réponse réelle. Les ingrédients sont les 10 cas publiés du jeu de test sur Brio*

| Ingrédient | 1er | 5e |
| --- | --- | --- |
| 2 tasses de farine tout usage | 0.701 | 0.672 |
| beurre d'arachide crémeux | 0.874 | 0.855 |
| 500 ml de lait 2 % | 0.791 | 0.734 |
| 1 gousse d'ail (`produitDeBase` true) | 0.590 | 0.566 |
| 1 boîte de tomates italiennes en dés | 0.829 | 0.771 |
| 1/2 tasse d'huile d'olive extra vierge | 0.778 | 0.706 |
| 1 c. à thé d'extrait de vanille | 0.779 | 0.736 |
| 500 ml de bouillon de légumes | 0.694 | 0.673 |
| 1/2 tasse de chapelure | 0.695 | 0.648 |
| 1 pincée de sel | 0.842 | 0.736 |

`/recette`, `limite` 5 :

| Description | 1er | 5e |
| --- | --- | --- |
| quelque chose de réconfortant pour un souper d'hiver | 0.623 | 0.605 |
| un plat léger à préparer en vingt minutes | 0.639 | 0.624 |
| de quoi recevoir sans passer la journée en cuisine | 0.551 | 0.523 |
| un dessert au chocolat pour un anniversaire | 0.758 | 0.737 |

Requêtes sans rapport de sens (1er résultat) :

| Route | Requête | 1er |
| --- | --- | --- |
| `/apparier_ingredient` | pneu de voiture | 0.382 |
| `/apparier_ingredient` | ordinateur portable | 0.476 |
| `/apparier_ingredient` | billet d'avion | 0.452 |
| `/apparier_ingredient` | crayon à mine | 0.699 |
| `/recette` | réparer un pneu de voiture | 0.286 |
| `/recette` | installer un logiciel sur un ordinateur | 0.229 |

### Interpretation des scores

Nous observons les plages suivantes : 
- ingrédient 0.57-0.87, 
- recette 0.52-0.76, 
- sans rapport < 0.48 (ingrédient, sauf  "crayon à mine" 0.70) et < 0.29 (recette)
- Écart faible entre le 1er et le 5e (souvent < 0.05)

Puisque les recherches sans rapport sont beaucoup plus failble que celle avec du sens et que l'écart entre le 1er et le 5e est failbe, notre encodage semble bien fonctionner pour retourner les bon items sémantiquement.
