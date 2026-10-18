from pathlib import Path


def test_package_source_exists() -> None:
    assert Path("src/northgate/__init__.py").is_file()


def test_data_module_exists() -> None:
    assert Path("src/northgate/data/market_data.py").is_file()
