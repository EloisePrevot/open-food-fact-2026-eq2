# syntax=docker/dockerfile:1

# --- Build stage: compile and assemble the runnable distribution ---
FROM eclipse-temurin:25-jdk AS build
WORKDIR /app

# Warm the Gradle cache with just the build scripts first for better layer caching.
COPY gradlew ./
COPY gradle ./gradle
COPY settings.gradle build.gradle gradle.properties ./
RUN chmod +x ./gradlew && ./gradlew --no-daemon dependencies || true

# Build the application distribution.
COPY config ./config
COPY src ./src
RUN ./gradlew --no-daemon clean installDist

# --- Runtime stage: run on a lean JRE ---
FROM eclipse-temurin:25-jre AS runtime
WORKDIR /app

# The application plugin names the distribution after rootProject.name.
COPY --from=build /app/build/install/equipe2-bd/ ./

EXPOSE 8080

CMD ["./bin/equipe2-bd"]
