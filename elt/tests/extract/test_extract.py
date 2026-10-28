from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

import extract
from extract import (
    CNF_SOURCE,
    KAGGLE_SOURCE,
    OFF_SOURCE,
    get_raw_artifacts,
)

CNF_DIRECTORY_NAME = "cnf-fcen-csv"
KAGGLE_RELATIVE_PATH = Path("kaggle-recipes") / "recipes_extended.json"
OFF_FILENAME = "openfoodfacts.tsv"


# --------------------------------------------------------------------------- #
# Doublures et fixtures
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class FakeSettings:
    raw_directory: Path
    off_file: Path


@pytest.fixture
def raw_directory(tmp_path: Path) -> Path:
    directory = tmp_path / "raw"
    directory.mkdir()
    return directory


@pytest.fixture
def cnf_directory(raw_directory: Path) -> Path:
    directory = raw_directory / CNF_DIRECTORY_NAME
    directory.mkdir()
    return directory


@pytest.fixture
def off_file(raw_directory: Path) -> Path:
    return _create_file(raw_directory / OFF_FILENAME)


@pytest.fixture
def settings(raw_directory: Path, off_file: Path) -> FakeSettings:
    return FakeSettings(raw_directory=raw_directory, off_file=off_file)


def _create_file(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    return path


def _extract(source_names: list[str], settings: FakeSettings) -> list:
    return list(get_raw_artifacts(source_names, settings))


class TestCnfArtifacts:
    def test_returns_one_artifact_per_csv_sorted_by_name(
        self, settings: FakeSettings, cnf_directory: Path
    ) -> None:
        for filename in ("FOOD NAME.csv", "CONVERSION FACTOR.csv", "NUTRIENT NAME.csv"):
            _create_file(cnf_directory / filename)

        artifacts = _extract(["cnf"], settings)

        assert [artifact.path.name for artifact in artifacts] == [
            "CONVERSION FACTOR.csv",
            "FOOD NAME.csv",
            "NUTRIENT NAME.csv",
        ]

    def test_ignores_files_that_are_not_csv(
        self, settings: FakeSettings, cnf_directory: Path
    ) -> None:
        _create_file(cnf_directory / "FOOD NAME.csv")
        _create_file(cnf_directory / "README.txt")

        artifacts = _extract(["cnf"], settings)

        assert [artifact.path.name for artifact in artifacts] == ["FOOD NAME.csv"]

    def test_returns_nothing_when_directory_has_no_csv(
        self, settings: FakeSettings, cnf_directory: Path
    ) -> None:
        artifacts = _extract(["cnf"], settings)

        assert artifacts == []

    def test_describes_artifact_with_cnf_metadata(
        self, settings: FakeSettings, cnf_directory: Path, raw_directory: Path
    ) -> None:
        csv_path = _create_file(cnf_directory / "FOOD NAME.csv")

        (artifact,) = _extract(["cnf"], settings)

        assert artifact.source == CNF_SOURCE
        assert artifact.path == csv_path
        assert artifact.relative_path == str(Path(CNF_DIRECTORY_NAME) / "FOOD NAME.csv")
        assert artifact.media_type == "text/csv"

    @pytest.mark.parametrize(
        "filename",
        [
            "CONVERSION FACTOR.csv",
            "NUTRIENT AMOUNT.csv",
            "REFUSE AMOUNT.csv",
            "YIELD AMOUNT.csv",
        ],
    )
    def test_uses_utf8_for_known_utf8_files(
        self, settings: FakeSettings, cnf_directory: Path, filename: str
    ) -> None:
        _create_file(cnf_directory / filename)

        (artifact,) = _extract(["cnf"], settings)

        assert artifact.encoding == "utf-8"

    @pytest.mark.parametrize("filename", ["FOOD NAME.csv", "NUTRIENT NAME.csv"])
    def test_uses_cp1252_for_other_files(
        self, settings: FakeSettings, cnf_directory: Path, filename: str
    ) -> None:
        _create_file(cnf_directory / filename)

        (artifact,) = _extract(["cnf"], settings)

        assert artifact.encoding == "cp1252"

class TestKaggleArtifact:
    def test_describes_recipes_json_artifact(
        self, settings: FakeSettings, raw_directory: Path
    ) -> None:
        expected_path = raw_directory / KAGGLE_RELATIVE_PATH

        (artifact,) = _extract(["kaggle"], settings)

        assert artifact.source == KAGGLE_SOURCE
        assert artifact.path == expected_path
        assert artifact.relative_path == str(KAGGLE_RELATIVE_PATH)
        assert artifact.encoding == "utf-8"
        assert artifact.media_type == "application/json"

class TestOffArtifact:
    def test_describes_tsv_artifact(self, settings: FakeSettings, off_file: Path) -> None:
        (artifact,) = _extract(["off"], settings)

        assert artifact.source == OFF_SOURCE
        assert artifact.path == off_file
        assert artifact.encoding == "utf-8-sig"
        assert artifact.media_type == "text/tab-separated-values"

    def test_uses_path_relative_to_raw_directory_when_inside_it(
        self, raw_directory: Path
    ) -> None:
        nested_off_file = _create_file(raw_directory / "off" / OFF_FILENAME)
        settings = FakeSettings(raw_directory=raw_directory, off_file=nested_off_file)

        (artifact,) = _extract(["off"], settings)

        assert artifact.relative_path == str(Path("off") / OFF_FILENAME)

    def test_uses_filename_when_file_is_outside_raw_directory(
        self, raw_directory: Path, tmp_path: Path
    ) -> None:
        external_off_file = _create_file(tmp_path / "downloads" / OFF_FILENAME)
        settings = FakeSettings(raw_directory=raw_directory, off_file=external_off_file)

        (artifact,) = _extract(["off"], settings)

        assert artifact.relative_path == OFF_FILENAME

    def test_raises_when_file_is_missing(self, raw_directory: Path) -> None:
        missing_off_file = raw_directory / "missing.tsv"
        settings = FakeSettings(raw_directory=raw_directory, off_file=missing_off_file)

        with pytest.raises(FileNotFoundError, match="ELT_OFF_FILE"):
            _extract(["off"], settings)

    def test_raises_when_path_is_a_directory(self, raw_directory: Path) -> None:
        settings = FakeSettings(raw_directory=raw_directory, off_file=raw_directory)

        with pytest.raises(FileNotFoundError):
            _extract(["off"], settings)

class TestGetRawArtifacts:
    def test_yields_artifacts_in_requested_source_order(
        self, settings: FakeSettings, cnf_directory: Path
    ) -> None:
        _create_file(cnf_directory / "FOOD NAME.csv")

        artifacts = _extract(["off", "kaggle", "cnf"], settings)

        assert [artifact.source for artifact in artifacts] == [
            OFF_SOURCE,
            KAGGLE_SOURCE,
            CNF_SOURCE,
        ]

    def test_returns_nothing_when_no_source_is_requested(
        self, settings: FakeSettings
    ) -> None:

        artifacts = _extract([], settings)

        assert artifacts == []

    def test_raises_for_unsupported_source(self, settings: FakeSettings) -> None:
        unsupported_source = "usda"

        with pytest.raises(ValueError, match=f"Unsupported source: {unsupported_source}"):
            _extract([unsupported_source], settings)

    def test_is_lazy_until_iterated(self, settings: FakeSettings) -> None:
        unsupported_source = "usda"

        artifacts = get_raw_artifacts([unsupported_source], settings)

        with pytest.raises(ValueError):
            next(artifacts)

    def test_loads_settings_from_environment_when_none_given(
        self, monkeypatch: pytest.MonkeyPatch, settings: FakeSettings
    ) -> None:
        class EnvironmentSettings:
            @staticmethod
            def from_environment() -> FakeSettings:
                return settings

        monkeypatch.setattr(extract, "Settings", EnvironmentSettings)

        (artifact,) = list(get_raw_artifacts(["kaggle"]))

        assert artifact.path == settings.raw_directory / KAGGLE_RELATIVE_PATH