from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from models import db


sql_engine = create_engine('sqlite:///:memory:')

db.Base.metadata.create_all(sql_engine)

TRIGGER_SQL = """
CREATE TRIGGER before_insert_domains
BEFORE INSERT ON domains FOR EACH ROW
WHEN NEW.status = 1 AND (
    SELECT COUNT(*)
    FROM domains
    WHERE domain = NEW.domain AND status = 1
) > 0
BEGIN
    SELECT RAISE(ABORT, 'This domain has been registered');
END;
"""

# 执行 Trigger SQL 语句
with sql_engine.connect() as connection:
    connection.execute(text(TRIGGER_SQL))

# Use scoped_session for thread safety
Session = scoped_session(sessionmaker(bind=sql_engine))

def insert_domain():
    session = Session()
    now = datetime.now()
    domain = db.Domain(userId="109550028",
                        domain="test-reg.nycu-dev.me",
                        regDate=now,
                        expDate=now + timedelta(days=90),
                        status=1)
    session.add(domain)
    session.commit()
    session.close()

def test_sql_trigger():
    insert_domain()
    try:
        insert_domain()
        assert 0
    except Exception:
        assert 1
