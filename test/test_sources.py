from sources.base import Source, load_module


def test_tags_origin_by_default_column():
    src = Source("BOLSA", fetch=lambda: [{"x": 1}])
    assert src.load() == [{"x": 1, "Origen": "BOLSA"}]


def test_origin_column_is_configurable():
    src = Source("OTRO", fetch=lambda: [{"x": 1}], origin_column="Fuente")
    out = src.load()
    assert out[0]["Fuente"] == "OTRO"
    assert "Origen" not in out[0]


def test_runs_only_its_steps():
    only_positive = lambda rows: [r for r in rows if r["x"] > 0]
    src = Source("A", fetch=lambda: [{"x": 1}, {"x": -1}], steps=[only_positive])
    assert src.load() == [{"x": 1, "Origen": "A"}]


def test_load_module_concatenates_sources():
    a = Source("A", fetch=lambda: [{"x": 1}])
    b = Source("B", fetch=lambda: [{"x": 2}])
    out = load_module([a, b])
    assert [r["Origen"] for r in out] == ["A", "B"]