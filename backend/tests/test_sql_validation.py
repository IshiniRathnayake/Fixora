from app.agents.data_retrieval import DataRetrievalAgent


def test_rejects_non_select():
    assert DataRetrievalAgent._validate_sql("DELETE FROM orders") is not None


def test_rejects_forbidden_table():
    err = DataRetrievalAgent._validate_sql("SELECT * FROM users")
    assert err is not None


def test_accepts_valid_select():
    assert DataRetrievalAgent._validate_sql("SELECT id FROM orders LIMIT 5") is None
