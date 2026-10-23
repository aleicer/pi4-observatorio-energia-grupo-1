
from datetime import date

from src.utils import ventanas


def test_parte_65_dias_en_bloques_de_30():
    bloques = list(ventanas(date(2024, 1, 1), date(2024, 3, 5), 30))

    assert bloques == [
        (date(2024, 1, 1), date(2024, 1, 30)),
        (date(2024, 1, 31), date(2024, 2, 29)),
        (date(2024, 3, 1), date(2024, 3, 5)),
    ]


def test_no_deja_huecos_ni_repite_dias():
    inicio, fin = date(2024, 1, 1), date(2026, 9, 30)
    bloques = list(ventanas(inicio, fin, 30))

    assert bloques[0][0] == inicio
    assert bloques[-1][1] == fin

    for (_, fin_a), (inicio_b, _) in zip(bloques, bloques[1:]):
        assert (inicio_b - fin_a).days == 1

    for a, b in bloques:
        assert (b - a).days <= 29


def test_rango_de_un_solo_dia():
    assert list(ventanas(date(2026, 9, 30), date(2026, 9, 30), 30)) == [
        (date(2026, 9, 30), date(2026, 9, 30))
    ]
