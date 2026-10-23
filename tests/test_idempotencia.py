
"""Pruebas de ya_existe(): el pipeline no repite descargas."""

from src import config
from src.utils import ya_existe


def test_omite_archivo_que_ya_existe(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DIR_BRONZE", tmp_path) # bronce "falso" temporal

    (tmp_path / "xm_demanda.parquet").write_bytes(b"datos") # simulamos que ya se descargo

    assert ya_existe("xm_demanda", forzar=False) is True


def test_con_forzar_vuelve_a_descargar(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DIR_BRONZE", tmp_path)

    (tmp_path / "xm_demanda.parquet").write_bytes(b"datos")

    assert ya_existe("xm_demanda", forzar=True) is False # --forzar ignora el archivo


def test_archivo_nuevo_si_se_descarga(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DIR_BRONZE", tmp_path)

    assert ya_existe("noaa_oni", forzar=False) is False # no existe -> hay que descargar
