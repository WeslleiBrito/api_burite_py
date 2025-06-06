from sqlalchemy import create_engine

DATABASE_URL = "mysql+mysqlconnector://burite:burite123@192.168.0.112:3307/clarionerp"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800
)
