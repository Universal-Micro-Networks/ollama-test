import os
from sqlalchemy import Engine, create_engine

def get_db_connection() -> Engine:
    """create async session

    Returns:
        async_sessionmaker:async session maker object
    """
    url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://log_analysis_user:Fq3MdiTt@localhost/log_analysis_db",
    )
    engine = create_engine(
        url,
        echo=False,
    )

    return engine
