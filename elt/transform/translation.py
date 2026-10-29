"""Traduction anglais→français hors ligne, exécutée par lots pendant le TRANSFORM.

La traduction est appliquée une seule fois, au chargement vers MongoDB, et le
résultat est versionné comme une donnée (champs ``nom``/``nomEn`` etc.). Aucun
appel réseau ni clé d'API : le modèle est embarqué dans l'image Docker.
Voir §2.1.4 de l'énoncé : un texte généré au moment de la requête rend les
résultats non reproductibles ; on le produit donc en amont et on le conserve.

On s'appuie directement sur CTranslate2 et SentencePiece, les deux composants
légers (CPU) qu'utilise Argos Translate. On évite ainsi la dépendance à
``stanza``/``torch`` (plusieurs Go de bibliothèques GPU) qu'Argos tire pour un
découpage en phrases dont nous n'avons pas besoin : les noms de produits et les
courtes descriptions se traduisent d'un seul tenant.
"""

from __future__ import annotations

from functools import lru_cache
from os import getenv
from pathlib import Path
from typing import Protocol

_MODEL_DIRECTORY_ENV = "TRANSLATION_MODEL_DIRECTORY"
_DEFAULT_MODEL_DIRECTORY = "/app/models/translation/en-fr"
_SENTENCEPIECE_FILENAME = "sentencepiece.model"


class _Encoder(Protocol):
    def encode(self, text: str, out_type: type) -> list[str]: ...


def translate_to_french(texts: list[str]) -> list[str]:
    """Traduit une liste de chaînes anglaises en français.

    Les chaînes vides ou composées uniquement d'espaces sont retournées telles
    quelles, sans solliciter le modèle.
    """
    pending = [(index, text) for index, text in enumerate(texts) if text and text.strip()]
    results = list(texts)
    if not pending:
        return results
    for (index, _), translated in zip(pending, _translate_batch([text for _, text in pending])):
        results[index] = translated
    return results


_WHITESPACE_MARKER = "\u2581"  # ▁ : marqueur d'espace de SentencePiece.

# Taille de tranche envoyée au modèle en une fois. Le lot Mongo peut contenir des
# milliers de chaînes ; les traduire toutes d'un coup ferait grimper la mémoire
# (faisceaux de recherche + tampons internes). On traduit par petites tranches.
_TRANSLATION_CHUNK = 64


def _translate_batch(texts: list[str]) -> list[str]:
    translator, tokenizer = _model()
    results: list[str] = []
    for start in range(0, len(texts), _TRANSLATION_CHUNK):
        chunk = texts[start : start + _TRANSLATION_CHUNK]
        tokenized = [tokenizer.encode(text, out_type=str) for text in chunk]
        outputs = translator.translate_batch(tokenized, max_batch_size=_TRANSLATION_CHUNK)
        results.extend(_detokenize(output.hypotheses[0]) for output in outputs)
    return results


def _detokenize(pieces: list[str]) -> str:
    """Reconstruit le texte à partir des sous-mots SentencePiece.

    Les sous-mots sont recollés puis le marqueur d'espace ``▁`` est rétabli en
    espace. On n'utilise pas ``decode``/``decode_pieces`` du tokeniseur : sur ce
    modèle, ces méthodes laissent passer une partie des marqueurs.
    """
    return "".join(pieces).replace(_WHITESPACE_MARKER, " ").strip()


@lru_cache(maxsize=1)
def _model() -> tuple[object, _Encoder]:
    """Charge une seule fois le modèle CTranslate2 et son tokeniseur.

    Le chargement est paresseux : les étapes du pipeline qui ne traduisent pas
    (extraction, indexation Qdrant) ne paient pas ce coût.
    """
    import ctranslate2
    import sentencepiece

    directory = _model_directory()
    tokenizer_path = directory / _SENTENCEPIECE_FILENAME
    if not directory.is_dir() or not tokenizer_path.is_file():
        raise RuntimeError(
            f"Modèle de traduction en→fr introuvable sous {directory}. "
            "Il doit être embarqué dans l'image (voir backend/Dockerfile)."
        )
    # L'ELT partage son conteneur avec la JVM et un modèle d'embeddings déjà
    # résident : on contraint CTranslate2 à un seul fil et on décharge le modèle
    # de la mémoire entre les tranches pour éviter un dépassement (OOM, code 137).
    translator = ctranslate2.Translator(
        str(directory), device="cpu", inter_threads=1, intra_threads=1
    )
    tokenizer = sentencepiece.SentencePieceProcessor(model_file=str(tokenizer_path))
    return translator, tokenizer


def _model_directory() -> Path:
    return Path(getenv(_MODEL_DIRECTORY_ENV, _DEFAULT_MODEL_DIRECTORY))
