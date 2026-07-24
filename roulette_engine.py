from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class SignalResult:
    target_sector: str
    epicenter: int
    covered_numbers: tuple[int, ...]
    score: float
    confidence_score: float
    confidence_label: str
    backtest_accuracy: float
    sample_size: int
    backtest_trials: int
    explanation: str


class EuropeanRouletteEngine:
    """Motor estatístico para roleta europeia (0–36).

    O motor não tenta afirmar que resultados aleatórios são previsíveis.
    Ele resume recência, concentração física na roda e desempenho histórico
    de uma regra determinística.
    """

    WHEEL: tuple[int, ...] = (
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
        13,
        36,
        11,
        30,
        8,
        23,
        10,
        5,
        24,
        16,
        33,
        1,
        20,
        14,
        31,
        9,
        22,
        18,
        29,
        7,
        28,
        12,
        35,
        3,
        26,
    )

    RED_NUMBERS = frozenset(
        {
            1,
            3,
            5,
            7,
            9,
            12,
            14,
            16,
            18,
            19,
            21,
            23,
            25,
            27,
            30,
            32,
            34,
            36,
        }
    )

    SECTORS: dict[str, tuple[int, ...]] = {
        "Jeu Zéro": (12, 35, 3, 26, 0, 32, 15),
        "Voisins": (22, 18, 29, 7, 28, 19, 4, 21, 2, 25),
        "Orphelins": (1, 20, 14, 31, 9, 6, 34, 17),
        "Tiers": (27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33),
    }

    def __init__(self) -> None:
        self._wheel_index = {
            number: index
            for index, number in enumerate(self.WHEEL)
        }

        self._sector_by_number = {
            number: sector
            for sector, numbers in self.SECTORS.items()
            for number in numbers
        }

    @staticmethod
    def validate_number(number: int) -> int:
        """Valida e converte um resultado para inteiro."""

        value = int(number)

        if not 0 <= value <= 36:
            raise ValueError(
                f"Número inválido: {number}. Use valores de 0 a 36."
            )

        return value

    def sanitize_history(
        self,
        history: Iterable[int],
    ) -> list[int]:
        """Remove valores inválidos do histórico."""

        valid: list[int] = []

        for number in history:
            try:
                valid.append(self.validate_number(number))
            except (TypeError, ValueError):
                continue

        return valid

    def get_color(self, number: int) -> str:
        """Retorna a cor correspondente ao número."""

        value = self.validate_number(number)

        if value == 0:
            return "Verde"

        if value in self.RED_NUMBERS:
            return "Vermelho"

        return "Preto"

    def get_sector(self, number: int) -> str:
        """Retorna o setor físico da roda."""

        value = self.validate_number(number)
        return self._sector_by_number[value]

    def get_neighbors(
        self,
        number: int,
        radius: int = 2,
    ) -> tuple[int, ...]:
        """Retorna o número central e seus vizinhos físicos."""

        value = self.validate_number(number)

        bounded_radius = max(
            0,
            min(int(radius), 18),
        )

        index = self._wheel_index[value]

        return tuple(
            self.WHEEL[
                (index + offset) % len(self.WHEEL)
            ]
            for offset in range(
                -bounded_radius,
                bounded_radius + 1,
            )
        )

    @staticmethod
    def _recency_weights(
        length: int,
        decay: float,
    ) -> list[float]:
        """Cria pesos exponenciais para os resultados."""

        if length <= 0:
            return []

        bounded_decay = min(
            max(float(decay), 0.50),
            0.999,
        )

        return [
            bounded_decay ** (length - 1 - index)
            for index in range(length)
        ]

    def _sector_scores(
        self,
        history: Sequence[int],
        decay: float,
    ) -> dict[str, float]:
        """Calcula a pontuação ponderada de cada setor."""

        weights = self._recency_weights(
            len(history),
            decay,
        )

        scores = {
            sector: 0.0
            for sector in self.SECTORS
        }

        for number, weight in zip(
            history,
            weights,
        ):
            sector = self.get_sector(number)
            scores[sector] += weight

        return scores

    def _choose_epicenter(
        self,
        history: Sequence[int],
        target_sector: str,
        decay: float,
    ) -> int:
        """Escolhe o epicentro por frequência ponderada."""

        weights = self._recency_weights(
            len(history),
            decay,
        )

        number_scores: Counter[int] = Counter()

        for number, weight in zip(
            history,
            weights,
        ):
            if self.get_sector(number) == target_sector:
                number_scores[number] += weight

        if not number_scores:
            return history[-1]

        max_score = max(number_scores.values())

        tied_numbers = {
            number
            for number, score in number_scores.items()
            if score == max_score
        }

        # Em caso de empate, vence o número mais recente.
        for number in reversed(history):
            if number in tied_numbers:
                return number

        return history[-1]

    def _raw_signal(
        self,
        history: Sequence[int],
        decay: float,
        neighbor_radius: int,
    ) -> tuple[
        str,
        int,
        tuple[int, ...],
        float,
    ]:
        """Gera o sinal sem executar o backtest."""

        scores = self._sector_scores(
            history,
            decay,
        )

        sector_order = tuple(self.SECTORS)

        target_sector = max(
            sector_order,
            key=lambda sector: (
                scores[sector],
                -sector_order.index(sector),
            ),
        )

        epicenter = self._choose_epicenter(
            history,
            target_sector,
            decay,
        )

        covered_numbers = self.get_neighbors(
            epicenter,
            neighbor_radius,
        )

        total_score = sum(scores.values())

        if total_score:
            concentration = (
                scores[target_sector]
                / total_score
                * 100
            )
        else:
            concentration = 0.0

        return (
            target_sector,
            epicenter,
            covered_numbers,
            concentration,
        )

    def backtest(
        self,
        history: Sequence[int],
        decay: float = 0.90,
        neighbor_radius: int = 2,
        minimum_training: int = 8,
    ) -> tuple[float, int]:
        """Executa um backtest walk-forward.

        Cada leitura é gerada somente com os dados que já
        estavam disponíveis antes do resultado seguinte.
        """

        clean = self.sanitize_history(history)

        hits = 0
        trials = 0

        for next_index in range(
            minimum_training,
            len(clean),
        ):
            training_history = clean[:next_index]

            (
                _,
                _,
                covered_numbers,
                _,
            ) = self._raw_signal(
                training_history,
                decay=decay,
                neighbor_radius=neighbor_radius,
            )

            next_number = clean[next_index]

            if next_number in covered_numbers:
                hits += 1

            trials += 1

        if trials == 0:
            return 0.0, 0

        accuracy = hits / trials * 100

        return accuracy, trials

    @staticmethod
    def _confidence(
        sample_size: int,
        concentration: float,
        backtest_accuracy: float,
        coverage_size: int,
        backtest_trials: int,
    ) -> tuple[float, str]:
        """Calcula um índice interno de robustez.

        Este índice não representa probabilidade de acerto.
        """

        baseline = coverage_size / 37 * 100

        sample_component = min(
            sample_size / 60,
            1.0,
        ) * 45

        concentration_component = min(
            max(concentration - 25, 0) / 35,
            1.0,
        ) * 25

        observed_lift = max(
            backtest_accuracy - baseline,
            0,
        )

        trial_reliability = min(
            backtest_trials / 40,
            1.0,
        )

        backtest_component = (
            min(observed_lift / 20, 1.0)
            * 30
            * trial_reliability
        )

        score = min(
            sample_component
            + concentration_component
            + backtest_component,
            100,
        )

        if score >= 70:
            label = "Alta"
        elif score >= 45:
            label = "Média"
        else:
            label = "Baixa"

        return score, label

    def build_signal(
        self,
        history: Sequence[int],
        decay: float = 0.90,
        neighbor_radius: int = 2,
    ) -> SignalResult | None:
        """Gera a leitura estatística completa."""

        clean = self.sanitize_history(history)

        if len(clean) < 8:
            return None

        (
            target_sector,
            epicenter,
            covered_numbers,
            concentration,
        ) = self._raw_signal(
            clean,
            decay=decay,
            neighbor_radius=neighbor_radius,
        )

        (
            backtest_accuracy,
            backtest_trials,
        ) = self.backtest(
            clean,
            decay=decay,
            neighbor_radius=neighbor_radius,
        )

        (
            confidence_score,
            confidence_label,
        ) = self._confidence(
            sample_size=len(clean),
            concentration=concentration,
            backtest_accuracy=backtest_accuracy,
            coverage_size=len(covered_numbers),
            backtest_trials=backtest_trials,
        )

        explanation = (
            f"O setor {target_sector} concentra "
            f"{concentration:.1f}% da pontuação "
            "ponderada por recência. O epicentro é "
            "escolhido por frequência ponderada, "
            "com desempate pelo resultado mais recente."
        )

        return SignalResult(
            target_sector=target_sector,
            epicenter=epicenter,
            covered_numbers=covered_numbers,
            score=concentration,
            confidence_score=confidence_score,
            confidence_label=confidence_label,
            backtest_accuracy=backtest_accuracy,
            sample_size=len(clean),
            backtest_trials=backtest_trials,
            explanation=explanation,
        )
