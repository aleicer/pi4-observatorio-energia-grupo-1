import pytest

from src import config
from src.silver.nasa_power import main

def test_main_indica_como_generar_bronce_si_no_existe(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DIR_BRONZE", tmp_path)

    with pytest.raises(FileNotFoundError) as error:
        main()

    assert "python -m src.extract.nasa_power" in str(error.value)