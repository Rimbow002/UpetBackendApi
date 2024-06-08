from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

MYSQL_USER = 'root'
MYSQL_PASSWORD = 'KLyzHquSzomBjVXrgjMjutjJqLKqQvgw'
MYSQL_HOST = 'viaduct.proxy.rlwy.net'
MYSQL_PORT = '29253'
MYSQL_DATABASE = 'railway'
#mysql://root:wUtLBypWHLWWnRUmdFtmdWszWZYYKoaL@viaduct.proxy.rlwy.net:36102/railway
#mysql://root:MmeGvXZLtObSxyOWGpsIpnMioRtpOJMl@viaduct.proxy.rlwy.net:37129/railway
#mysql://root:fvYQogwpIoplNmoKtNhgxvbhlHHQVvaS@viaduct.proxy.rlwy.net:58668/railway
#mysql://root:FfgUEZJRiDPRjPsYHlTaokDXYDAhjuHY@viaduct.proxy.rlwy.net:58091/railway
#URL_DATABASE = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
#URL_DATABASE = 'mysql+pymysql://root:12345@localhost:3306/veterinarys'

URL_DATABASE = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



def get_db() :
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
