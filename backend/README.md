### Technologies

- OpenJDK 25
- Gradle 9.7 avec Gradle Wrapper
- Jersey 4
- Jetty 12
- JUnit 6, Mockito, AssertJ et REST Assured

<p align="right">(<a href="#readme-top">retour en haut</a>)</p>

## Démarrage

### Prérequis

- Une distribution OpenJDK 25 installée et active.

Le gestionnaire de versions Java reste au choix. La *toolchain* Gradle impose seulement la version 25. Le Gradle
Wrapper fournit Gradle 9.7, donc aucune installation globale de Gradle n'est nécessaire.

### Installation

Depuis le répertoire `backend` :

```sh
java -version
./gradlew build
```

Sous Windows, remplacez `./gradlew` par `gradlew.bat`.

<p align="right">(<a href="#readme-top">retour en haut</a>)</p>

## Utilisation

### Lancer l'API

```sh
./gradlew run
```

Vous pouvez aussi exécuter `start.sh` sous Linux/macOS, `start.bat` sous Windows, ou lancer la classe
`ProjectMain` depuis votre IDE.

L'API écoute sur `http://localhost:8080` :

- Heartbeat : [http://localhost:8080/api/heartbeat](http://localhost:8080/api/heartbeat)

### Tester et construire

```sh
./gradlew test             # tests unitaires
./gradlew integrationTest  # tests d'intégration
./gradlew build            # toutes les vérifications et la distribution
```

Les tests se trouvent dans `src/test`. Les classes dont le nom se termine par `IT` sont exécutées par la tâche
`integrationTest`; les autres le sont par `test`. Gradle affiche le résultat de chaque test et génère des rapports
HTML et JUnit XML dans `build/reports/tests/` et `build/test-results/`.

Lorsqu'aucun intrant d'un test n'a changé, Gradle indique `UP-TO-DATE` et réutilise le résultat existant. Ce
comportement est normal. Pour forcer une nouvelle exécution pendant un diagnostic, ajoutez `--rerun-tasks` à la
commande.

Les archives exécutables sont produites dans `build/distributions/`.

<p align="right">(<a href="#readme-top">retour en haut</a>)</p>

## Feuille de route

- [x] Route heartbeat pour vérifier l'état de l'API.
- [x] Build Gradle sous OpenJDK 25.
- [x] Tests unitaires et d'intégration séparés.

<p align="right">(<a href="#readme-top">retour en haut</a>)</p>

## Contribution

Respectez les consignes du projet de session. Avant de partager un changement au backend, exécutez `./gradlew build`.

<p align="right">(<a href="#readme-top">retour en haut</a>)</p>

## Licence

Aucune licence n'est actuellement fournie avec ce projet de départ. Consultez les consignes du cours avant de
redistribuer son contenu.

<p align="right">(<a href="#readme-top">retour en haut</a>)</p>

## Contact

Pour toute question, utilisez les canaux de communication officiels du cours GLO-4003.

<p align="right">(<a href="#readme-top">retour en haut</a>)</p>

## Remerciements

- [Best README Template](https://github.com/othneildrew/Best-README-Template) pour la structure de cette documentation.

<p align="right">(<a href="#readme-top">retour en haut</a>)</p>
