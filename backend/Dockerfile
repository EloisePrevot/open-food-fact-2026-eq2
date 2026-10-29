# syntax=docker/dockerfile:1

# --- Build stage: compile and assemble the runnable distribution ---
FROM eclipse-temurin:25-jdk AS build
WORKDIR /app

# Warm the Gradle cache with just the build scripts first for better layer caching.
COPY backend/gradlew ./
COPY backend/gradle ./gradle
COPY backend/settings.gradle backend/build.gradle backend/gradle.properties ./
# Strip any CRLF line endings (e.g. from Windows checkouts) so /bin/sh can run the script.
RUN sed -i 's/\r$//' ./gradlew && chmod +x ./gradlew && ./gradlew --no-daemon dependencies || true

# Build the application distribution.
COPY backend/config ./config
COPY backend/src ./src
RUN ./gradlew --no-daemon clean installDist

# --- Runtime stage: JRE + Python environment for the ELT pipeline ---
FROM eclipse-temurin:25-jre AS runtime
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /usr/local/bin/uv
ENV UV_PYTHON=3.13 \
    UV_PYTHON_INSTALL_DIR=/opt/python \
    UV_PROJECT_ENVIRONMENT=/app/elt/.venv \
    UV_LINK_MODE=copy

# Install the ELT dependencies from the lockfile before copying the sources.
COPY elt/pyproject.toml elt/uv.lock ./elt/
RUN uv sync --project elt --frozen --no-dev

# Shared embedding model: the Python pipeline indexes with it, the Java API vectorises queries with it.
ENV FASTEMBED_CACHE_PATH=/app/models \
    EMBEDDING_MODEL_DIRECTORY=/app/models
RUN /app/elt/.venv/bin/python -c "from fastembed import TextEmbedding; TextEmbedding('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"

# Offline English→French translation model, baked into the image so the ELT never
# calls out at runtime (no network, no API key). Download happens at build time only.
# An Argos ".argosmodel" is a zip holding a CTranslate2 model (in model/) and a
# SentencePiece tokenizer; we flatten both into one directory and drop the Stanza
# sentence splitter we do not use. See transform/translation.py.
ENV TRANSLATION_MODEL_DIRECTORY=/app/models/translation/en-fr
ADD https://argos-net.com/v1/translate-en_fr-1_9.argosmodel /tmp/en_fr.argosmodel
RUN /app/elt/.venv/bin/python - <<'PY'
import shutil, zipfile
from pathlib import Path

target = Path("/app/models/translation/en-fr")
target.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile("/tmp/en_fr.argosmodel") as archive:
    archive.extractall("/tmp/en_fr")

root = next(Path("/tmp/en_fr").iterdir())
for item in (root / "model").iterdir():
    shutil.copy2(item, target / item.name)
shutil.copy2(root / "sentencepiece.model", target / "sentencepiece.model")

required = {"model.bin", "sentencepiece.model"}
missing = required - {entry.name for entry in target.iterdir()}
if missing:
    raise SystemExit(f"Modele de traduction incomplet, manquants: {missing}")
print("Translation model ready:", sorted(entry.name for entry in target.iterdir()))
PY
RUN rm -rf /tmp/en_fr /tmp/en_fr.argosmodel

COPY elt ./elt
# The application plugin names the distribution after rootProject.name.
COPY --from=build /app/build/install/equipe2-bd/ ./

ENV ELT_PYTHON=/app/elt/.venv/bin/python \
    ELT_DIRECTORY=/app/elt

EXPOSE 8080

CMD ["./bin/equipe2-bd"]
