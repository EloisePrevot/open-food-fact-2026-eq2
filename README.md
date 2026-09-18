# Base de données avancée - Equipe 2

### Structure

```text
/
├── backend/              # API REST Java
└── frontend/             # SPA React
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