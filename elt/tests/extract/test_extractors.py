from __future__ import annotations

import json
from pathlib import Path

import pytest

from raw_extractors import (
    CsvRecordExtractor,
    JsonArrayRecordExtractor,
    TsvRecordExtractor,
    extractor_for,
)
from raw_models import RawArtifact

CSV_MEDIA_TYPE = "text/csv"
TSV_MEDIA_TYPE = "text/tab-separated-values"
JSON_MEDIA_TYPE = "application/json"


def _make_artifact(
    path: Path, media_type: str = CSV_MEDIA_TYPE, encoding: str = "utf-8"
) -> RawArtifact:
    return RawArtifact(
        source="test_source",
        path=path,
        relative_path=path.name,
        encoding=encoding,
        media_type=media_type,
    )


def _write_text(path: Path, content: str, encoding: str = "utf-8") -> Path:
    path.write_bytes(content.encode(encoding))
    return path


def _payloads(records: list) -> list[dict]:
    return [record.payload for record in records]


def _ordinals(records: list) -> list[int]:
    return [record.ordinal for record in records]


class TestCsvRecordExtractor:
    @pytest.fixture
    def extractor(self) -> CsvRecordExtractor:
        return CsvRecordExtractor()

    def test_maps_each_row_to_headers(
        self, extractor: CsvRecordExtractor, tmp_path: Path
    ) -> None:
        path = _write_text(tmp_path / "foods.csv", "id,name\n1,Pomme\n2,Poire\n")

        records = list(extractor.extract(_make_artifact(path)))

        assert _payloads(records) == [
            {"id": "1", "name": "Pomme"},
            {"id": "2", "name": "Poire"},
        ]
        assert _ordinals(records) == [1, 2]

    def test_returns_nothing_for_empty_file(
        self, extractor: CsvRecordExtractor, tmp_path: Path
    ) -> None:
        path = _write_text(tmp_path / "empty.csv", "")

        records = list(extractor.extract(_make_artifact(path)))

        assert records == []

    def test_returns_nothing_when_only_headers(
        self, extractor: CsvRecordExtractor, tmp_path: Path
    ) -> None:
        path = _write_text(tmp_path / "headers.csv", "id,name\n")

        records = list(extractor.extract(_make_artifact(path)))

        assert records == []

    def test_reads_quoted_multiline_field_as_single_value(
        self, extractor: CsvRecordExtractor, tmp_path: Path
    ) -> None:
        path = _write_text(tmp_path / "notes.csv", 'id,note\n1,"ligne 1\nligne 2"\n')

        records = list(extractor.extract(_make_artifact(path)))

        assert _payloads(records) == [{"id": "1", "note": "ligne 1\nligne 2"}]

    def test_skips_blank_rows_and_keeps_source_ordinal(
        self, extractor: CsvRecordExtractor, tmp_path: Path
    ) -> None:
        path = _write_text(tmp_path / "gaps.csv", "id,name\n1,Pomme\n\n,\n4,Kiwi\n")

        records = list(extractor.extract(_make_artifact(path)))

        assert _payloads(records) == [
            {"id": "1", "name": "Pomme"},
            {"id": "4", "name": "Kiwi"},
        ]
        assert _ordinals(records) == [1, 4]

    def test_raises_when_row_width_differs_from_headers(
        self, extractor: CsvRecordExtractor, tmp_path: Path
    ) -> None:
        path = _write_text(tmp_path / "broken.csv", "id,name\n1,Pomme\n2,Poire,extra\n")

        with pytest.raises(ValueError, match="broken.csv at record 2"):
            list(extractor.extract(_make_artifact(path)))

    def test_suffixes_duplicate_headers(
        self, extractor: CsvRecordExtractor, tmp_path: Path
    ) -> None:
        path = _write_text(tmp_path / "dupes.csv", "code,code,code\na,b,c\n")

        (record,) = extractor.extract(_make_artifact(path))

        assert record.payload == {"code": "a", "code_1": "b", "code_2": "c"}

    def test_names_empty_headers_by_position(
        self, extractor: CsvRecordExtractor, tmp_path: Path
    ) -> None:
        path = _write_text(tmp_path / "unnamed.csv", "id,,\n1,x,y\n")

        (record,) = extractor.extract(_make_artifact(path))

        assert record.payload == {"id": "1", "_unnamed_1": "x", "_unnamed_2": "y"}

    def test_decodes_with_artifact_encoding(
        self, extractor: CsvRecordExtractor, tmp_path: Path
    ) -> None:
        path = _write_text(tmp_path / "cp1252.csv", "nom\nCrème brûlée\n", encoding="cp1252")

        (record,) = extractor.extract(_make_artifact(path, encoding="cp1252"))

        assert record.payload == {"nom": "Crème brûlée"}


class TestTsvRecordExtractor:
    @pytest.fixture
    def extractor(self) -> TsvRecordExtractor:
        return TsvRecordExtractor()

    def test_splits_fields_on_tabs(
        self, extractor: TsvRecordExtractor, tmp_path: Path
    ) -> None:
        path = _write_text(tmp_path / "off.tsv", "code\tproduct_name\n123\tLait, entier\n")

        (record,) = extractor.extract(_make_artifact(path, TSV_MEDIA_TYPE))

        assert record.payload == {"code": "123", "product_name": "Lait, entier"}

    def test_treats_quotes_as_literal_data(
        self, extractor: TsvRecordExtractor, tmp_path: Path
    ) -> None:
        path = _write_text(
            tmp_path / "quotes.tsv",
            'code\tproduct_name\n1\t"Bio\n2\tSirop "érable"\n',
        )

        records = list(extractor.extract(_make_artifact(path, TSV_MEDIA_TYPE)))

        assert _payloads(records) == [
            {"code": "1", "product_name": '"Bio'},
            {"code": "2", "product_name": 'Sirop "érable"'},
        ]

    def test_accepts_fields_larger_than_default_csv_limit(
        self, extractor: TsvRecordExtractor, tmp_path: Path
    ) -> None:
        large_value = "x" * 500_000
        path = _write_text(tmp_path / "large.tsv", f"code\tingredients\n1\t{large_value}\n")

        (record,) = extractor.extract(_make_artifact(path, TSV_MEDIA_TYPE))

        assert record.payload["ingredients"] == large_value


class TestJsonArrayRecordExtractor:
    @pytest.fixture
    def extractor(self) -> JsonArrayRecordExtractor:
        return JsonArrayRecordExtractor()

    def test_yields_each_object_of_root_array(
        self, extractor: JsonArrayRecordExtractor, tmp_path: Path
    ) -> None:
        recipes = [{"title": "Tarte", "servings": 6}, {"title": "Soupe", "tags": ["hiver"]}]
        path = _write_text(tmp_path / "recipes.json", json.dumps(recipes))

        records = list(extractor.extract(_make_artifact(path, JSON_MEDIA_TYPE)))

        assert _payloads(records) == recipes
        assert _ordinals(records) == [1, 2]

    def test_returns_nothing_for_empty_array(
        self, extractor: JsonArrayRecordExtractor, tmp_path: Path
    ) -> None:
        path = _write_text(tmp_path / "empty.json", "[]")

        records = list(extractor.extract(_make_artifact(path, JSON_MEDIA_TYPE)))

        assert records == []

    def test_raises_when_item_is_not_an_object(
        self, extractor: JsonArrayRecordExtractor, tmp_path: Path
    ) -> None:
        path = _write_text(tmp_path / "mixed.json", json.dumps([{"title": "Tarte"}, "oops"]))

        with pytest.raises(ValueError, match="mixed.json at record 2"):
            list(extractor.extract(_make_artifact(path, JSON_MEDIA_TYPE)))


class TestExtractorFor:
    @pytest.mark.parametrize(
        ("media_type", "expected_extractor"),
        [
            (CSV_MEDIA_TYPE, CsvRecordExtractor),
            (TSV_MEDIA_TYPE, TsvRecordExtractor),
            (JSON_MEDIA_TYPE, JsonArrayRecordExtractor),
        ],
    )
    def test_selects_extractor_matching_media_type(
        self, tmp_path: Path, media_type: str, expected_extractor: type
    ) -> None:
        artifact = _make_artifact(tmp_path / "source", media_type)

        extractor = extractor_for(artifact)

        assert type(extractor) is expected_extractor

    def test_raises_for_unsupported_media_type(self, tmp_path: Path) -> None:
        artifact = _make_artifact(tmp_path / "source.xml", "application/xml")

        with pytest.raises(ValueError, match="Unsupported media type: application/xml"):
            extractor_for(artifact)