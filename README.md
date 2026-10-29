# Base de données avancée - Equipe 2

### Structure

```text
/
├── backend/              # API REST Java
├── frontend/             # SPA React
└── elt/                  # Scripts Python d'extraction, transformation et chargement
```

### Technologies

- OpenJDK 25, Gradle 9.7, Jetty et Jersey;
- Node.js 24 LTS, pnpm 11 et TypeScript 6 & React 19;

### Prérequis : mise

Les versions de Node.js (24) et de pnpm sont gérées par [mise](https://mise.jdx.dev/)
via le fichier `mise.toml` à la racine.

Installez mise :

```sh
# Windows
winget install jdx.mise

# macOS
brew install mise
```

Activez mise dans votre shell (voir la [doc](https://mise.jdx.dev/getting-started.html)) en faisant cette commande dans PowerShell:
```
if (-not (Test-Path $PROFILE)) {
    New-Item -ItemType Directory -Force (Split-Path -Parent $PROFILE) | Out-Null
    New-Item -ItemType File -Path $PROFILE | Out-Null
}
$activation = '(&mise activate pwsh) | Out-String | Invoke-Expression'
if (-not (Select-String -Path $PROFILE -SimpleMatch $activation -Quiet)) {
    Add-Content $PROFILE $activation
}
```

Puis redémarrez votre terminal ou recharger votre profil:
```
. $PROFILE
```

Ensuite, installez les outils du projet à la racine du dépôt :

```sh
mise install
```

### Installation

À la racine du dépôt :

```sh
pnpm install
```

### Utilisation

Démarrez d'abord l'API dans un terminal :

```sh
cd backend
./gradlew run
```

Sous Windows, utilisez `gradlew.bat run` et sous Linux/MacOS `./start.sh`.
Dans un second terminal, lancez le frontend depuis la racine :
```
pnpm dev:frontend
```

### ELT

Vérifiez les connexions :

```sh
uv run --project elt python -m elt.load --check-connections
```

Chargez les données CNF :

```sh
uv run --project elt python -m elt.load --load-raw cnf
```

Chargez les recettes Kaggle :

```sh
uv run --project elt python -m elt.load --load-raw kaggle
```

Chargez toutes les sources prises en charge :

```sh
uv run --project elt python -m elt.load --load-raw all
```

#### Indexation de recherche et de produits dans Qdrant

L’ELT maintient deux collections, séparées selon leur usage :

- `recipes` : un vecteur par recette, payload `{identifiant, type}`;
- `ingredients` : aliments CNF et produits OFF, payload
  `{identifiant, produitDeBase, marques, nutriScore, nova}`.

Qdrant ne garde que l’identifiant et les champs filtrés; le document complet
vit dans MongoDB sous le même identifiant (`recipe:…`, `cnf:…`, `off:…`).
SQLite contient toutes les données brutes, sans filtre. Les règles de nettoyage
(`elt/transform/recipes.py`, `cnf_foods.py`, `off_products.py`) lisent SQLite
et produisent le document MongoDB; Qdrant en indexe une projection minimale
(`elt/transform/qdrant_points.py`). Seuls les produits OFF étiquetés Canada,
États-Unis ou Mexique sont conservés. Le fichier OFF est attendu à
`elt/raw/off.csv`; pour un autre emplacement, définissez `ELT_OFF_FILE`.

Chargez d’abord les sources brutes, puis construisez MongoDB et Qdrant à partir
de SQLite (l’ordre entre les deux n’importe pas) :

```sh
uv run --project elt python -m elt.load --load-raw all
uv run --project elt python -m elt.load --load-mongo --limit 0
uv run --project elt python -m elt.load --load-qdrant --limit 1000
```

Avec `--limit 0`, le chargement MongoDB supprime aussi les documents d’une
source qui ne sont plus produits par les règles actuelles (rejeu complet).

#### Pipeline lancé par le backend

Avec `docker compose up`, le backend exécute le pipeline **en arrière-plan** au
démarrage (extract → MongoDB → Qdrant). L’API répond pendant ce temps; chaque
ligne du pipeline apparaît dans les logs du backend préfixée par
`[ETL en arrière-plan]`, jusqu’à `Terminé` ou `Échec`. Variables du service
`backend` :

- `ELT_AU_DEMARRAGE` : `true` pour lancer le pipeline au démarrage (`false` par
  défaut hors Docker);
- `ELT_LIMITE` : documents maximum par source pour MongoDB et Qdrant (`0` =
  aucune limite). L’extraction vers SQLite est toujours complète.

Le pipeline ne refait pas un travail déjà fait :

- l’extraction ignore un fichier déjà présent dans SQLite avec le même contenu
  (hash SHA-256); seul le calcul du hash de `off.csv` prend une à deux minutes;
- MongoDB et Qdrant sont lancés avec `--skip-up-to-date` : une source est
  ignorée si elle a déjà été chargée à partir des mêmes fichiers bruts, des
  mêmes règles de transformation (`elt/transform/`) et d’une limite au moins
  aussi grande. Cet état est conservé dans la collection MongoDB
  `etat_chargements` et dans les métadonnées des collections Qdrant.

Sans `--skip-up-to-date`, une commande lancée à la main recharge toujours.
Tant que MongoDB ou Qdrant ne sont pas prêts, l’API répond `503` avec un
message plutôt qu’une erreur générique.

`--limit` s’applique séparément aux recettes, aliments CNF et produits OFF;
`--limit 0` indexe tout. Les IDs de points sont déterministes : rejouer un
chargement met à jour les mêmes points sans créer de doublons. Avec `--limit 0`,
le chargement Qdrant supprime ensuite tous les points qu’il n’a pas réécrits
(règle qui exclut désormais un document, ancien format de payload); avec une
limite, rien n’est supprimé.

Le flux de recommandation visé est : recherche de recette dans `recipes`
(filtre `type`), puis recherche vectorielle de chaque ingrédient dans
`ingredients` (filtres `produitDeBase`, `marques`, `nutriScore`, `nova`), et
lecture des documents complets dans MongoDB par identifiant. Un minimum de
Nutri-Score est ordonné de A à E; NOVA est un plafond; une marque est comparée
sans tenir compte de la casse. `produitDeBase` vaut `true` pour le CNF et
`false` pour OFF.

### Qualité (backend)

Étapes vérifiées : format (Spotless) → analyse statique (PMD, SpotBugs) → tests → build → couverture (JaCoCo).

Depuis la racine :

```sh
pnpm backend:verify   # tout : format + analyse + tests + build
pnpm backend:test     # check + tests
pnpm backend:build    # build seulement
pnpm backend:format   # corrige le formatage automatiquement
```

Si `backend:verify` échoue sur le formatage, lancez `pnpm backend:format` puis relancez.

### Docker

`docker compose` démarre toute la pile : backend (`:80`), frontend (`:8081`),
Qdrant (`:6333`), MongoDB (`:27017`) et PostgreSQL (`:5432`).

Le backend répond sur le port **80** (exigence de l'énoncé) à la requête
`GET /heartbeat`. Ce port est fixé par l'énoncé et ne doit pas être changé pour
`8080`. Le frontend, lui, est publié sur `:8081`.

```sh
docker compose up -d --build   # construit et démarre tout
docker compose down            # arrête tout
```

#### Partager MongoDB et Qdrant sans tout recharger

MongoDB et les vecteurs Qdrant sont calculés une seule fois, puis distribués
dans la Release GitHub `snapshots` du dépôt : `recipes.snapshot`,
`ingredients.snapshot` (Qdrant) et `mongo.archive.gz` (dump MongoDB).

**Pour un coéquipier : copier les sources dans `elt/raw/`, puis
`docker compose up -d --build`.** Au premier démarrage :

1. le service `snapshots` télécharge les trois fichiers;
2. Qdrant restaure les collections absentes de son volume;
3. `mongo-restore` restaure le dump si la base est vide;
4. le backend démarre; la recherche fonctionne tout de suite;
5. le pipeline en arrière-plan extrait les sources vers SQLite (environ une
   heure la première fois, à cause des 13 Go de `off.csv`), puis ignore
   MongoDB et Qdrant, déjà à jour.

Aux démarrages suivants, le pipeline ne fait que vérifier les hashes (une à
deux minutes). Si un fichier n’est pas publié, le pipeline charge lui-même la
base correspondante.

Si une source change, le pipeline la recharge; Qdrant ne revectorise alors que
ce qui a changé : chaque point garde dans son payload une `empreinte` (hash du
texte vectorisé et du modèle). Un point dont le texte est identique est
conservé tel quel; si seul son payload a changé (type, Nutri-Score…), il est
mis à jour sans recalculer le vecteur.

**Pour publier de nouvelles données** (après une modification des règles ou des
sources), depuis la racine du dépôt, la pile démarrée :

```sh
uv run --project elt python -m elt.load --load-raw all
uv run --project elt python -m elt.load --load-mongo --limit 0
uv run --project elt python -m elt.load --load-qdrant --limit 0
uv run --project elt python -m elt.load --export-qdrant-snapshots
docker compose run --rm mongo-dump
```

Les deux dernières commandes écrivent `recipes.snapshot`,
`ingredients.snapshot`, `manifest.json` (version de Qdrant, modèle, nombre de
points) et `mongo.archive.gz` dans `elt/snapshots/`, exclu de Git. Publiez-les
dans la Release `snapshots` (GitHub limite chaque fichier à 2 Go) :

```sh
gh release create snapshots elt/snapshots/* --title "Données préparées" --notes "MongoDB et Qdrant"
gh release upload snapshots elt/snapshots/* --clobber
```

La première commande crée la Release, la seconde remplace ses fichiers.

**Pour récupérer des données plus récentes**, supprimez les volumes locaux
(cela efface vos bases MongoDB et Qdrant) puis redémarrez :

```sh
docker compose down -v
docker compose up -d
```

`SNAPSHOTS_URL` permet de pointer vers un autre emplacement de téléchargement.
Les snapshots doivent provenir de la même version de Qdrant (`v1.19.1`) et du
même modèle `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
(dimension 384, cosine) que la stack.

Points d'accès une fois la stack démarrée :

| Service   | URL                              |
| --------- | -------------------------------- |
| Frontend  | http://localhost:8081            |
| Heartbeat | http://localhost/heartbeat       |

Le frontend affiche l'état de la connexion au backend sur la page d'accueil
(badge « Connected » et nom de l'application renvoyé par `/heartbeat`).

```sh
# Vérifier le heartbeat du backend
curl http://localhost/heartbeat
# -> {"nomApplication":"Open Food Facts"}
```

### Inspecter les bases de données

#### Qdrant: tableau de bord web intégré

Une fois la pile démarrée, ouvrez :

```
http://localhost:6333/dashboard
```

Vous y trouverez les collections, un explorateur de points et une console API.
L'API REST brute reste accessible sur `http://localhost:6333` (ex. `GET
http://localhost:6333/collections`).

#### MongoDB — CLI ou interface graphique

Via `mongosh` directement dans le conteneur :

```sh
docker compose exec mongodb mongosh -u root -p root --authenticationDatabase admin
```

Via une interface graphique (MongoDB Compass) depuis l'hôte, utilisez la chaîne
de connexion :

```
mongodb://root:root@localhost:27017/?authSource=admin
```

#### PostgreSQL — CLI ou interface graphique

Via `psql` directement dans le conteneur :

```sh
docker compose exec postgres psql -U postgres -d open_food_facts
# puis, dans le prompt : \dt  puis  \d raw_records
```

Via une interface graphique (DBeaver, pgAdmin) depuis l'hôte, utilisez la chaîne
de connexion :

```
postgresql://postgres:postgres@localhost:5432/open_food_facts
```
