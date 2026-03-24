import logging
import redis
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
migrate = Migrate()

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self):
        self.client = None

    def init_app(self, app):
        try:
            redis_url = app.config.get("REDIS_URL")
            if redis_url:
                self.client = redis.from_url(redis_url, decode_responses=True)
                self.client.ping()
                logger.info("Redis connected successfully")
            else:
                logger.warning("Redis URL not configured")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.client = None

    def get(self, key):
        return self.client.get(key) if self.client else None

    def set(self, key, value, ex=None):
        return self.client.set(key, value, ex=ex) if self.client else False

    def delete(self, key):
        return self.client.delete(key) if self.client else 0


redis_client = RedisClient()
