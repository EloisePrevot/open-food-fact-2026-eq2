from __future__ import annotations

from itertools import count, islice

import pytest

from iterables import batched, capped


class TestBatched:
    def test_splits_items_into_batches_of_given_size(self) -> None:
        items = range(6)

        batches = list(batched(items, 2))

        assert batches == [[0, 1], [2, 3], [4, 5]]

    def test_last_batch_holds_remaining_items(self) -> None:
        items = range(5)

        batches = list(batched(items, 2))

        assert batches == [[0, 1], [2, 3], [4]]

    def test_returns_single_batch_when_size_exceeds_item_count(self) -> None:
        items = ["a", "b"]

        batches = list(batched(items, 10))

        assert batches == [["a", "b"]]

    def test_returns_nothing_for_empty_items(self) -> None:
        items: list[int] = []

        batches = list(batched(items, 3))

        assert batches == []

    def test_returns_nothing_when_size_is_zero(self) -> None:
        items = range(3)

        batches = list(batched(items, 0))

        assert batches == []

    def test_raises_when_size_is_negative(self) -> None:
        items = range(3)

        with pytest.raises(ValueError):
            list(batched(items, -1))

    def test_yields_batches_as_lists(self) -> None:
        items = (letter for letter in "abc")

        batches = list(batched(items, 2))

        assert all(isinstance(batch, list) for batch in batches)

    def test_consumes_items_lazily(self) -> None:
        infinite_items = count()

        first_batches = list(islice(batched(infinite_items, 3), 2))

        assert first_batches == [[0, 1, 2], [3, 4, 5]]


class TestCapped:
    def test_limits_items_to_given_count(self) -> None:
        items = range(10)

        result = list(capped(items, 3))

        assert result == [0, 1, 2]

    def test_returns_all_items_when_limit_exceeds_count(self) -> None:
        items = [1, 2]

        result = list(capped(items, 5))

        assert result == [1, 2]

    def test_returns_same_iterable_when_limit_is_none(self) -> None:
        items = [1, 2, 3]

        result = capped(items, None)

        assert result is items

    def test_returns_same_iterable_when_limit_is_zero(self) -> None:
        items = [1, 2, 3]

        result = capped(items, 0)

        assert result is items

    def test_caps_infinite_items_lazily(self) -> None:
        infinite_items = count()

        result = list(capped(infinite_items, 4))

        assert result == [0, 1, 2, 3]

    def test_raises_when_limit_is_negative(self) -> None:
        items = range(3)

        with pytest.raises(ValueError):
            capped(items, -1)