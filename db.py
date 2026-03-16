from dotenv import load_dotenv
import os
from psycopg2.pool import SimpleConnectionPool

load_dotenv()

pool = SimpleConnectionPool(
    1,   # min connections
    10,  # max connections
    os.environ["NEON_URI"]
)