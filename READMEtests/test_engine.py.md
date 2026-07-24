import unittest

from roulette_engine import (
    EuropeanRouletteEngine,
)


class EuropeanRouletteEngineTests(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.engine = (
            EuropeanRouletteEngine()
        )

    def test_wheel_contains_all_numbers(
        self,
    ) -> None:
        self.assertEqual(
            len(self.engine.WHEEL),
            37,
        )

        self.assertEqual(
            set(self.engine.WHEEL),
            set(range(37)),
        )

    def test_colors(self) -> None:
        self.assertEqual(
            self.engine.get_color(0),
            "Verde",
        )

        self.assertEqual(
            self.engine.get_color(1),
            "Vermelho",
        )

        self.assertEqual(
            self.engine.get_color(2),
            "Preto",
        )

    def test_sectors_cover_all_numbers_once(
        self,
    ) -> None:
        numbers = [
            number
            for sector_numbers
            in self.engine.SECTORS.values()
            for number in sector_numbers
        ]

        self.assertEqual(
            len(numbers),
            37,
        )

        self.assertEqual(
            set(numbers),
            set(range(37)),
        )

    def test_neighbors_wrap_around(
        self,
    ) -> None:
        neighbors = (
            self.engine.get_neighbors(
                0,
                2,
            )
        )

        self.assertEqual(
            neighbors,
            (
                3,
                26,
                0,
                32,
                15,
            ),
        )

    def test_invalid_number(self) -> None:
        with self.assertRaises(ValueError):
            self.engine.validate_number(37)

    def test_signal_requires_minimum_sample(
        self,
    ) -> None:
        signal = self.engine.build_signal(
            [1, 2, 3]
        )

        self.assertIsNone(signal)

    def test_signal_is_deterministic(
        self,
    ) -> None:
        history = [
            0,
            32,
            15,
            19,
            4,
            21,
            2,
            25,
            17,
            34,
            6,
            27,
        ]

        first_signal = (
            self.engine.build_signal(history)
        )

        second_signal = (
            self.engine.build_signal(history)
        )

        self.assertEqual(
            first_signal,
            second_signal,
        )

    def test_backtest_trials(self) -> None:
        history = list(range(20))

        _, trials = self.engine.backtest(
            history
        )

        self.assertEqual(
            trials,
            12,
        )


if __name__ == "__main__":
    unittest.main()
