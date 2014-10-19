from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import SQLALCHEMY_DATABASE_URI
from contextlib import contextmanager

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

@contextmanager
def session(commit=False):
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        if commit:
            session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
