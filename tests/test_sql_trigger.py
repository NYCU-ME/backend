
from sqlalchemy import create_engine

from models import db


def test_sql_trigger():
    sql_engine = create_engine('sqlite:///:memory:')
    db.Base.metadata.create_all(sql_engine)
