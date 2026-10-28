# Architecture.md

## Moteur 1 : SQLite - SQL

### 1. Type de données conservées
Les données conservées dans ce moteur sont les données brutes extraites de nos trois sources de données. Nous avons choisi de conserver les données brutes dans un moteur SQL, puisqu’elles peuvent être téléchargées au format CSV, qui peut facilement se convertir en SQL. Nous avons également choisi le moteur SQLite pour sa simplicité d’utilisation et pour sa facilité de conversion de CSV en une base de données SQLite.

### 2. Exemple réel de chaque donnée conservée
**Recettes**
| Colonne | Exemple |
|---|---|
| `recipe_title` | `Air Fryer Potato Slices with Dipping Sauce` |
| `category` | `Air Fryer Recipes` |
| `subcategory` | `Air Fryer Recipes` |
| `description` | `These air fryer potato slices, served with a beer ketchup dipping sauce, are a tasty finger food…` |
| `ingredients` | `["3/4 cup ketchup", "1/2 cup beer", … ]` |
| `directions` | `["Combine ketchup, beer, Worcestershire sauce…", …]` |
| `num_ingredients` | `9` |
| `num_steps` | `5` |
| `ingredient_text` | `ketchup beer worcestershire sauce onion powder cayenne baking potatoes …` |
| `directions_text` | `combine ketchup, beer, worcestershire sauce, onion powder, and cayenne in a small saucepan. …` |
| `combined_text` | `air fryer potato slices with dipping sauce air fryer recipes air fryer recipes 3/4 cup ketchup …` |
| `ingredients_raw` | `["3/4 cup ketchup", "1/2 cup beer", … ]` |
| `directions_raw` | `["Combine ketchup, beer, Worcestershire sauce…", …]` |
| `ingredients_canonical` | `["ketchup", "beer", "worcestershire sauce", … , "salt freshly ground black pepper"]` |
| `cuisine_list` | `["american", "american_region", "asian", "european", "greek", "korean", "mediterranean", "middle eastern region"]` |
| `course_list` | `["sauce"]` |
| `tastes` | `["spicy", "bitter", "savory"]` |
| `primary_taste` | `spicy` |
| `secondary_taste` | `savory` |
| `fast_hits` | `6` |
| `slow_hits` | `2` |
| `medium_hits` | `7` |
| `cook_speed` | `medium` |
| `est_prep_time_min` | `23` |
| `est_cook_time_min` | `74` |
| `difficulty` | `hard` |
| `is_vegan` | `True` |
| `is_vegetarian` | `True` |
| `is_halal` | `False` |
| `is_kosher` | `True` |
| `is_nut_free` | `True` |
| `is_dairy_free` | `True` |
| `is_gluten_free` | `True` |
| `dietary_profile` | `["vegan", "gluten_free", "nut_free", "kosher"]` |
| `healthiness_score` | `80` |
| `health_flags` | `["plant_based", "healthy_fats", "fried"]` |
| `main_ingredient` | `unknown` |
| `health_level` | `healthy` |

**Open Food Facts**
| Colonne | Exemple |
|---|---|
| `code` | `000000000054` |
| `url` | `http://world-en.openfoodfacts.org/product/000000000054/limonade-artisanale-a-la-rose` |
| `creator` | `kiliweb` |
| `created_t` | `1582569031` |
| `created_datetime` | `2020-02-24T18:30:31Z` |
| `last_modified_t` | `1733085204` |
| `last_modified_datetime` | `2024-12-01T20:33:24Z` |
| `last_modified_by` | — |
| `last_updated_t` | `1740205422` |
| `last_updated_datetime` | `2025-02-22T06:23:42Z` |
| `product_name` | `Limonade artisanale a la rose` |
| `abbreviated_product_name` | — |
| `generic_name` | — |
| `quantity` | — |
| `packaging` | — |
| `packaging_tags` | — |
| `packaging_en` | — |
| `packaging_text` | — |
| `brands` | — |
| `brands_tags` | — |
| `brands_en` | — |
| `categories` | — |
| `categories_tags` | — |
| `categories_en` | — |
| `origins` | — |
| `origins_tags` | — |
| `origins_en` | — |
| `manufacturing_places` | — |
| `manufacturing_places_tags` | — |
| `labels` | — |
| `labels_tags` | — |
| `labels_en` | — |
| `emb_codes` | — |
| `emb_codes_tags` | — |
| `first_packaging_code_geo` | — |
| `cities` | — |
| `cities_tags` | — |
| `purchase_places` | — |
| `stores` | — |
| `countries` | `en:fr` |
| `countries_tags` | `en:france` |
| `countries_en` | `France` |
| `ingredients_text` | — |
| `ingredients_tags` | — |
| `ingredients_analysis_tags` | — |
| `allergens` | — |
| `allergens_en` | — |
| `traces` | — |
| `traces_tags` | — |
| `traces_en` | — |
| `serving_size` | — |
| `serving_quantity` | — |
| `no_nutrition_data` | — |
| `additives_n` | — |
| `additives` | — |
| `additives_tags` | — |
| `additives_en` | — |
| `nutriscore_score` | — |
| `nutriscore_grade` | `unknown` |
| `nova_group` | — |
| `pnns_groups_1` | `unknown` |
| `pnns_groups_2` | `unknown` |
| `food_groups` | — |
| `food_groups_tags` | — |
| `food_groups_en` | — |
| `states` | `en:to-be-completed, en:nutrition-facts-to-be-completed, en:ingredients-to-be-completed, en…` |
| `states_tags` | `en:to-be-completed,en:nutrition-facts-to-be-completed,en:ingredients-to-be-completed,en:ex…` |
| `states_en` | `To be completed,Nutrition facts to be completed,Ingredients to be completed,Expiration dat…` |
| `brand_owner` | — |
| `environmental_score_score` | — |
| `environmental_score_grade` | `unknown` |
| `nutrient_levels_tags` | — |
| `product_quantity` | — |
| `owner` | — |
| `data_quality_errors_tags` | — |
| `unique_scans_n` | — |
| `popularity_tags` | — |
| `completeness` | `0.1625` |
| `last_image_t` | `1733085204` |
| `last_image_datetime` | `2024-12-01T20:33:24Z` |
| `main_category` | — |
| `main_category_en` | — |
| `image_url` | `https://images.openfoodfacts.org/images/products/invalid/front_en.6.400.jpg` |
| `image_small_url` | `https://images.openfoodfacts.org/images/products/invalid/front_en.6.200.jpg` |
| `image_ingredients_url` | — |
| `image_ingredients_small_url` | — |
| `image_nutrition_url` | — |
| `image_nutrition_small_url` | — |
| `energy-kj_100g` | — |
| `energy-kcal_100g` | — |
| `energy_100g` | — |
| `energy-from-fat_100g` | — |
| `fat_100g` | — |
| `saturated-fat_100g` | — |
| `butyric-acid_100g` | — |
| `caproic-acid_100g` | — |
| `caprylic-acid_100g` | — |
| `capric-acid_100g` | — |
| `lauric-acid_100g` | — |
| `myristic-acid_100g` | — |
| `palmitic-acid_100g` | — |
| `stearic-acid_100g` | — |
| `arachidic-acid_100g` | — |
| `behenic-acid_100g` | — |
| `lignoceric-acid_100g` | — |
| `cerotic-acid_100g` | — |
| `montanic-acid_100g` | — |
| `melissic-acid_100g` | — |
| `unsaturated-fat_100g` | — |
| `monounsaturated-fat_100g` | — |
| `omega-9-fat_100g` | — |
| `polyunsaturated-fat_100g` | — |
| `omega-3-fat_100g` | — |
| `omega-6-fat_100g` | — |
| `alpha-linolenic-acid_100g` | — |
| `eicosapentaenoic-acid_100g` | — |
| `docosahexaenoic-acid_100g` | — |
| `linoleic-acid_100g` | — |
| `arachidonic-acid_100g` | — |
| `gamma-linolenic-acid_100g` | — |
| `dihomo-gamma-linolenic-acid_100g` | — |
| `oleic-acid_100g` | — |
| `elaidic-acid_100g` | — |
| `gondoic-acid_100g` | — |
| `mead-acid_100g` | — |
| `erucic-acid_100g` | — |
| `nervonic-acid_100g` | — |
| `trans-fat_100g` | — |
| `cholesterol_100g` | — |
| `carbohydrates_100g` | — |
| `sugars_100g` | — |
| `added-sugars_100g` | — |
| `sucrose_100g` | — |
| `glucose_100g` | — |
| `fructose_100g` | — |
| `galactose_100g` | — |
| `lactose_100g` | — |
| `maltose_100g` | — |
| `maltodextrins_100g` | — |
| `psicose_100g` | — |
| `starch_100g` | — |
| `polyols_100g` | — |
| `erythritol_100g` | — |
| `isomalt_100g` | — |
| `maltitol_100g` | — |
| `sorbitol_100g` | — |
| `fiber_100g` | — |
| `soluble-fiber_100g` | — |
| `polydextrose_100g` | — |
| `insoluble-fiber_100g` | — |
| `proteins_100g` | — |
| `casein_100g` | — |
| `serum-proteins_100g` | — |
| `nucleotides_100g` | — |
| `salt_100g` | — |
| `added-salt_100g` | — |
| `sodium_100g` | — |
| `alcohol_100g` | — |
| `vitamin-a_100g` | — |
| `beta-carotene_100g` | — |
| `vitamin-d_100g` | — |
| `vitamin-e_100g` | — |
| `vitamin-k_100g` | — |
| `vitamin-c_100g` | — |
| `vitamin-b1_100g` | — |
| `vitamin-b2_100g` | — |
| `vitamin-pp_100g` | — |
| `vitamin-b6_100g` | — |
| `vitamin-b9_100g` | — |
| `folates_100g` | — |
| `vitamin-b12_100g` | — |
| `biotin_100g` | — |
| `pantothenic-acid_100g` | — |
| `silica_100g` | — |
| `bicarbonate_100g` | — |
| `potassium_100g` | — |
| `chloride_100g` | — |
| `calcium_100g` | — |
| `phosphorus_100g` | — |
| `iron_100g` | — |
| `magnesium_100g` | — |
| `zinc_100g` | — |
| `copper_100g` | — |
| `manganese_100g` | — |
| `fluoride_100g` | — |
| `selenium_100g` | — |
| `chromium_100g` | — |
| `molybdenum_100g` | — |
| `iodine_100g` | — |
| `caffeine_100g` | — |
| `taurine_100g` | — |
| `methylsulfonylmethane_100g` | — |
| `hydroxymethylbutyrate_100g` | — |
| `ph_100g` | — |
| `fruits-vegetables-legumes_100g` | — |
| `collagen-meat-protein-ratio_100g` | — |
| `cocoa_100g` | — |
| `chlorophyl_100g` | — |
| `carbon-footprint_100g` | — |
| `glycemic-index_100g` | — |
| `water-hardness_100g` | — |
| `choline_100g` | — |
| `phylloquinone_100g` | — |
| `beta-glucan_100g` | — |
| `inositol_100g` | — |
| `carnitine_100g` | — |
| `sulphate_100g` | — |
| `nitrate_100g` | — |
| `acidity_100g` | — |
| `carbohydrates-total_100g` | — |
| `water_100g` | — |


**CNF**

**Conversion Factor**
| Colonne | Exemple |
|---|---|
| `FoodID` | `2` |
| `MeasureID` | `341` |
| `ConversionFactorValue` | `0.40152` |
| `ConvFactorDateOfEntry` | `1997-05-01` |

**Food Group**
| Colonne | Exemple |
|---|---|
| `FoodGroupID` | `1` |
| `FoodGroupCode` | `1` |
| `FoodGroupName` | `Dairy and Egg Products` |
| `FoodGroupNameF` | `Produits laitiers et d'œufs` |

**Food Name**
| Colonne | Exemple |
|---|---|
| `FoodID` | `2` |
| `FoodCode` | `2` |
| `FoodGroupID` | `22` |
| `FoodSourceID` | `20` |
| `FoodDescription` | `Cheese souffle` |
| `FoodDescriptionF` | `Soufflé au fromage` |
| `FoodDateOfEntry` | `1981-01-01` |
| `FoodDateOfPublication` | — |
| `CountryCode` | — |
| `ScientificName` | — |

**Food Source**
| Colonne | Exemple |
|---|---|
| `FoodSourceID` | `0` |
| `FoodSourceCode` | `0` |
| `FoodSourceDescription` | `FOODS BASED ON DATA FROM USDA: NO CHANGES` |
| `FoodSourceDescriptionF` | `ALIMENTS BASÉS SUR LE USDA: AUCUNE MODIFICATION APPORTÉE` |

**Measure Name**
| Colonne | Exemple |
|---|---|
| `MeasureID` | `6` |
| `MeasureDescription` | `1 fish (500 g)` |
| `MeasureDescriptionF` | `1 poisson (500 g)` |

**Nutrient Amount**
| Colonne | Exemple |
|---|---|
| `FoodID` | `2` |
| `NutrientID` | `203` |
| `NutrientValue` | `9.54` |
| `StandardError` | `0` |
| `NumberofObservations` | `0` |
| `NutrientSourceID` | `102` |
| `NutrientDateOfEntry` | `2010-04-16` |

**Nutrient Name**
| Colonne | Exemple |
|---|---|
| `NutrientID` | `203` |
| `NutrientCode` | `203` |
| `NutrientSymbol` | `PROT` |
| `NutrientUnit` | `g` |
| `NutrientName` | `PROTEIN` |
| `NutrientNameF` | `PROTÉINES` |
| `Tagname` | `PROCNT` |
| `NutrientDecimals` | `2` |

**Nutrient Source**
| Colonne | Exemple |
|---|---|
| `NutrientSourceID` | `0` |
| `NutrientSourceCode` | `0` |
| `NutrientSourceDescription` | `No change from USDA` |
| `NutrientSourc DescriptionF` | `Provient intégralement de l'USDA` |

**Refuse Amount**
| Colonne | Exemple |
|---|---|
| `FoodID` | `2` |
| `RefuseID` | `750` |
| `RefuseAmount` | `0` |
| `RefuseDateOfEntry` | `1997-05-01` |

**Refuse Name**
| Colonne | Exemple |
|---|---|
| `RefuseID` | `750` |
| `RefuseDescription` | `total refuse` |
| `RefuseDescriptionF` | `portion non comestible totale` |

**Yield Amount**
| Colonne | Exemple |
|---|---|
| `FoodID` | `57` |
| `YieldID` | `985` |
| `YieldAmount` | `22` |
| `YieldDateofEntry` | `2004-08-12` |

**Yield Name**
| Colonne | Exemple |
|---|---|
| `YieldID` | `455` |
| `YieldDescription` | `amount to make 100ml` |
| `YieldDescriptionF` | `quantité requise pour préparer  100ml` |

### 3. Modèle de données envisagé
Nos trois sources de données contiennent 14 fichiers CSV. Le moteur SQLite va ainsi contenir une table par fichier, soit 14 tables. 
* La source de recettes représente une seule table.
* La source OFF contient les produits à code barre et représente une seule table.
* La source CNF contient les produits de base et représente 12 tables.

### 4. Requêtes de l'application servies
| Route | Moteur |
| --- | --- |
| GET /donnees_brutes/{identifiant} | SQLite |
| GET /extracted_data | SQLite |

### 5. Données présentes dans plus d'un moteur
Les données de ces modèles sont dans la plupart des cas utilisés dans une autre base de données. Par exemple, les produits de l'Amérique du Nord de OFF et les autres éléments des bases de données de recette et la CNF se retrouve dans la base de données Mongo. Puisque cette base de données sert seulement à chercher données sans filtres, la priorité sera toujours les données traitées, c’est à dire Mongo. 

### 6. Justification par les principes
**Fiabilité**
Cette BD doit simplement contenir les données brutes et l'importation des données peut se faire très facilement grâce à un script Python. Ce moteur peut aussi être utilisé en lecture seul, ce qui garantit l'immuabilité des données. Il est aussi possible de créer des index pour accélérer la lecture des données.

**Maintenabilité**
Il y a peu de de maintenance à faire dans cette BD, puisque c'est un seul fichier dans le projet qui nécessite aucune configuration.

**Extensibilité**
Ajouter une source ne demande aucune modification du schéma : il suffit d'une nouvelle valeur de `source`. Si une règle de transformation change, on reconstruit la BD2 et la BD3 à partir de la BD1 sans retélécharger les sources.


## Moteur 2 : MongoDB - Document

### 1. Type de données conservées
Recettes – type : recettes propres, traduite en français et un champ type

Produits : catalogues des produits nettoyés de OFF et CNF

### 2. Exemple réel de chaque donnée conservée

**Recettes**

| Colonne | Exemple |
|---|---|
| `recipe_title` | `Air Fryer Potato Slices with Dipping Sauce` |
| `category` | `Air Fryer Recipes` |
| `subcategory` | `Air Fryer Recipes` |
| `description` | `These air fryer potato slices, served with a beer ketchup dipping sauce, are a tasty finger food…` |
| `ingredients` | `["3/4 cup ketchup", "1/2 cup beer", … ]` |
| `directions` | `["Combine ketchup, beer, Worcestershire sauce…", …]` |
| `num_ingredients` | `9` |
| `num_steps` | `5` |
| `ingredient_text` | `ketchup beer worcestershire sauce onion powder cayenne baking potatoes …` |
| `directions_text` | `combine ketchup, beer, worcestershire sauce, onion powder, and cayenne in a small saucepan. …` |
| `combined_text` | `air fryer potato slices with dipping sauce air fryer recipes air fryer recipes 3/4 cup ketchup …` |
| `ingredients_raw` | `["3/4 cup ketchup", "1/2 cup beer", … ]` |
| `directions_raw` | `["Combine ketchup, beer, Worcestershire sauce…", …]` |
| `ingredients_canonical` | `["ketchup", "beer", "worcestershire sauce", … , "salt freshly ground black pepper"]` |
| `cuisine_list` | `["american", "american_region", "asian", "european", "greek", "korean", "mediterranean", "middle eastern region"]` |
| `course_list` | `["sauce"]` |
| `tastes` | `["spicy", "bitter", "savory"]` |
| `primary_taste` | `spicy` |
| `secondary_taste` | `savory` |
| `fast_hits` | `6` |
| `slow_hits` | `2` |
| `medium_hits` | `7` |
| `cook_speed` | `medium` |
| `est_prep_time_min` | `23` |
| `est_cook_time_min` | `74` |
| `difficulty` | `hard` |
| `is_vegan` | `True` |
| `is_vegetarian` | `True` |
| `is_halal` | `False` |
| `is_kosher` | `True` |
| `is_nut_free` | `True` |
| `is_dairy_free` | `True` |
| `is_gluten_free` | `True` |
| `dietary_profile` | `["vegan", "gluten_free", "nut_free", "kosher"]` |
| `healthiness_score` | `80` |
| `health_flags` | `["plant_based", "healthy_fats", "fried"]` |
| `main_ingredient` | `unknown` |
| `health_level` | `healthy` |

**Open Food Facts**
| Colonne | Exemple |
|---|---|
| `code` | `000000000054` |
| `product_name` | `Limonade artisanale a la rose` |
| `brands` | — |
| `countries_tags` | `en:france` |
| `nutriscore_grade` | `unknown` |
| `nova_group` | — |
| `countries_tags` | `en:france` |

**CNF**

**Food Name**
| Colonne | Exemple |
|---|---|
| `FoodID` | `2` |
| `FoodCode` | `2` |
| `FoodGroupID` | `22` |
| `FoodSourceID` | `20` |
| `FoodDescription` | `Cheese souffle` |
| `FoodDescriptionF` | `Soufflé au fromage` |
| `FoodDateOfEntry` | `1981-01-01` |
| `FoodDateOfPublication` | — |
| `CountryCode` | — |
| `ScientificName` | — |

**Nutrient Amount**
| Colonne | Exemple |
|---|---|
| `FoodID` | `2` |
| `NutrientID` | `203` |
| `NutrientValue` | `9.54` |
| `StandardError` | `0` |
| `NumberofObservations` | `0` |
| `NutrientSourceID` | `102` |
| `NutrientDateOfEntry` | `2010-04-16` |

**Nutrient Name**
| Colonne | Exemple |
|---|---|
| `NutrientID` | `203` |
| `NutrientCode` | `203` |
| `NutrientSymbol` | `PROT` |
| `NutrientUnit` | `g` |
| `NutrientName` | `PROTEIN` |
| `NutrientNameF` | `PROTÉINES` |
| `Tagname` | `PROCNT` |
| `NutrientDecimals` | `2` |

### 3. Modèle de données envisagé
**Recettes (collection)**

| Champ | Type | Nullable | Contraintes |
|---|---|---|---|
| `identifiant` | `string` | Non | — |
| `nom` | `string` | Non | — |
| `nomEn` | `string` | Non | — |
| `description` | `string` | Non | — |
| `descriptionEn` | `string` | Non | — |
| `type` | `string` | Non | — |
| `nbIngredients` | `int` | Non | minimum : 1 |
| `ingredients` | `array<string>` | Non | — |

**Produits (collection)**

| Champ | Type | Nullable | Contraintes |
|---|---|---|---|
| `identifiant` | `string `| Non | — |
| `codeBarres` | `string` | Oui | — |
| `nomProduit` | `string` | Non | — |
| `marque` | `string` | Oui | — |
| `source` | `enum` | Non | `"off"`, `"cnf"` |
| `produitDeBase` | `bool` | Non | — |
| `categorie` | `string` | Non | — |
| `nutriScore` | `enum` | Oui | `"a"`, `"b"`, `"c"`, `"d"`, `"e"`, `null` |
| `nova` | `int` | Oui | minimum : 1, maximum : 4 |

### 4. Requêtes de l'application servies
| Route | Moteur |
| --- | --- |
| GET /transformed_data | MongoDB |
| GET /type | MongoDB |
| POST /recette | MongoDB |
| POST /cuisiner | MongoDB |

### 5. Données présentes dans plus d'un moteur
Certaines données des ingrédients et des recettes, tels que la description et les étapes de préparation seront doublé dans Mongo et dans la base de données non filtré (BD1).  À la différence de Mongo, Qdrant  ne possède que les données nécessaires pour la création de vecteur, donc dans notre cas, la source véridique sera toujours Mongo DB. Une fois que les données de la base de données 1 soit transféré, Mongo à priorité sur les autres. 

### 6. Justification par les principes
**Fiabilité**
On peut reconstruire la BD facilement à partir de la BD1, donc si jamais une erreur survient dans la BD elle sera détruite à la reconstruction et l’erreur disparait au lieu de rester dans nos données ce qui est plus fiable.

**Maintenabilité**
Les routes sont simples à implémenter et à comprendre. Ce sont de simples find, ce qui aide à la maintenabilité du système.

**Extensibilité**
Mongo a seulement à lire un id et retrouver le bon document avec toutes l’informations. De plus, ajouter un champ ou une source ne brise pas les documents existants.


## Moteur 3 : Qdrant - Vectoriel

### 1. Type de données conservées
Dans notre base de données vectorielle, nous allons conserver les données nécessaires à la recherche des recettes. En ce référent à la base de données Extended Recipes Dataset : 64K nous allons utiliser les champs suivants : Le titre de la recette, la catégorie de la recette, la sous-catégorie de la recette, la description, les directions, les goûts, la vitesse de cuisine, l’estimation de temps de préparation et l’estimation de temps de cuisson, la difficulté, le pointage de santé et le profile diététique qui inclut la présence de noix ou si la nourriture est végan.   

Si nous décidons aussi de mettre les ingrédients dans une collection pour avoir de meilleurs résultats d’association. Les champs seront donc l’identifiant, le nom du produit, la compagnie, la catégorie.    

### 2. Exemple réel de chaque donnée conservée
| Colonne | Valeur |
|---|---|
| **recipe_title** | Air Fryer Potato Slices with Dipping Sauce |
| **category** | Air Fryer Recipes |
| **subcategory** | Air Fryer Recipes |
| **description** | These air fryer potato slices, served with a beer ketchup dipping sauce, are a tasty finger food som… |
| **directions** | “Combine ketchup, beer, Worcestershire sauce, onion powder, and cayenne in a small saucepan. Bring… |
| **tastes** | [“spicy”, “bitter”, “savory”] |
| **cook_speed** | medium |
| **est_prep_time_min** | 23 |
| **est_cook_time_min** | 74 |
| **difficulty** | hard |
| **healthiness_score** | 80 |
| **dietary_profile** | [“vegan”, “gluten_free”, “nut_free”, “kosher”] |
| **is_vegan** | True |
| **is_nut_free** | True |

Pour les ingrédients,  

| Colonne | Valeur |
|---|---|
| **code** | 0000000105 |
| **product_name** | Paleta gran reserva — Sierra nevada — |
| **brands** | AdvoCare |
| **categories_en** | Beverages and beverages preparations, Beverages |
| **ingredients_text** | Thiamin, Biotin, Chromium, Garcinia cambogia fruit extract, Taurine, Green coffee fruit extract, Caffeine, Inositol, Citric Acid, Natural, Artificial Flavors, Sucralose, Spirulina Extract, Beta Carotene |

### 3. Modèle de données envisagé
Il va y avoir la collection des recettes. Chaque recette est un vecteur qui représente le sens des informations de la recette.   

Puis dans le cas où il faut faire de la recherche vectorielle avec les ingrédients, il faut aussi une collection pour les ingrédients qui seront eux aussi représentés dans des vecteurs.  

### 4. Requêtes de l'application servies
| Route | Moteur |
| --- | --- |
| POST /apparier_ingredient | Qdrant |
| POST /recette | Qdrant |
| POST /cuisiner | Qdrant |

### 5. Données présentes dans plus d'un moteur
Les données des ingrédients seront dans plusieurs moteurs, car dans le cas plusieurs informations ne seront pas utilisées pour la recherche et qu’un autre type de base de données est plus avantageux. En cas de divergence, l’id doit rester le plus possible identique et vers le même produit. Par contre, si la description change, la priorité sera à la seconde base de données faite pour retenir les informations des produits.   

### 6. Justification par les principes
**Fiabilité**
La recherche de recette et l’association des ingrédients sont très complexes et l’utilisation d’une base de données vectorielle permet de répondre de façon plus fiable à la demande du client.

**Maintenabilité**
Pas besoin d’avoir des jointures et des recherches complexes dans la base de données pour trouver ce que le client veut. Ceci rend donc la base de données plus maintenable, car on s’évite de la complexité.

**Extensibilité**
Ajouter des recettes avec une base vectorielle sera facile, il suffit de calculer le nouveau vecteur et de l’ajouter, ce qui rend la base de données extensible.
