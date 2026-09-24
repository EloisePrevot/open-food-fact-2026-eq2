# Base de données avancée - Equipe 2

### Structure

```text
/
├── backend/              # API REST Java
├── frontend/             # SPA React
└── etl/                  # Scripts Python d'extraction, transformation et chargement
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
Qdrant (`:6333`) et MongoDB (`:27017`). SQLite reste un fichier local (`etl/data/`).

Le backend répond sur le port **80** (exigence de l'énoncé) à la requête
`GET /heartbeat`. Ce port est fixé par l'énoncé et ne doit pas être changé pour
`8080`. Le frontend, lui, est publié sur `:8081`.

```sh
docker compose up -d --build   # construit et démarre tout
docker compose down            # arrête tout
```

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
