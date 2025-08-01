def test_version_import():
    from llmbrick import version
    assert hasattr(version, "__version__")
    assert isinstance(version.__version__, str)
    assert version.__version__ == "0.2.0"