from fashion_trends.settings import Settings
from fashion_trends.db import connect


def test_demo_outputs_exist_if_db_present():
    s = Settings()
    if not s.db_path.exists():
        return
    con = connect(s.db_path)
    tables = {t[0] for t in con.execute("SHOW TABLES FROM mart").fetchall()}
    assert "mart_brand_weekly_performance" in tables
    assert "mart_style_weekly" in tables
