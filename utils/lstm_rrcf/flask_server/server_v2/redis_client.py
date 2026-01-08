from redis import Redis
from redis.exceptions import RedisError
from typing import Optional, Dict
from pathlib import Path
from logger import logger
from datetime import datetime

# Global Redis connections
redis_write: Optional[Redis] = None
redis_read: Optional[Redis] = None

# Helper function to convert Redis config to connection parameters
def convert_redis_config(node: dict, readonly: bool) -> dict:
    try:
        host = node.get("host")
        port = node.get("port")

        if not host or not port:
            logger.error(f"Missing required Redis configuration keys: 'host' and/or 'port'.")
            return {}

        socket_config = {
            "host": host,
            "port": port,
            "ssl": False
        }

        if node.get("tls"):
            ca_path = node["tls"].get("ca", "")
            if ca_path:
                try:
                    ca_cert = Path(ca_path).read_text()
                    socket_config["ssl"] = True
                    socket_config["ssl_ca_certs"] = ca_path
                except Exception as e:
                    logger.warning(f"Failed to read CA certificate from '{ca_path}': {e}. Skipping TLS.")
            else:
                logger.warning("Redis TLS enabled but CA is empty. Skipping TLS.")

        redis_params = {
            **socket_config,
            "decode_responses": True
        }

        if node.get("username"):
            redis_params["username"] = node["username"]
        if node.get("password"):
            redis_params["password"] = node["password"]

        return redis_params

    except Exception as e:
        logger.error(f"Error converting Redis config: {e}")
        return {}


# Redis interface
class RedisClient:

    @staticmethod
    def is_initialized() -> bool:
        initialized = redis_write is not None and redis_read is not None
        logger.debug(f"RedisManager initialized: {initialized}")
        return initialized

    @staticmethod
    def connect():
        write_connected = False
        read_connected = False

        try:
            if not redis_write.connection or not redis_write.connection.is_connected:
                redis_write.ping()
            write_connected = True
            logger.debug("Redis write connection succeeded")
        except Exception as e:
            logger.error(f"Redis write connection failed: {e}")

        try:
            if redis_read != redis_write:
                if not redis_read.connection or not redis_read.connection.is_connected:
                    redis_read.ping()
                read_connected = True
                logger.debug("Redis read connection succeeded")
            else:
                # If redis_read is same as redis_write, reuse the write connection status
                read_connected = write_connected
        except Exception as e:
            logger.error(f"Redis read connection failed: {e}")

        return write_connected and read_connected


    @staticmethod
    def get(key: str):
        return redis_read.get(key)


    @staticmethod
    def hgetall(hash_key: str) -> Optional[dict]:
        try:
            result = redis_read.hgetall(hash_key)
            logger.debug(f"HGETALL '{hash_key}' => {result}")
            return result
        except RedisError as e:
            logger.warning(f"HGETALL error for hash '{hash_key}': {str(e)}")
            return None


    @staticmethod
    def set(key: str, val):
        return redis_write.set(key, val)


    @staticmethod
    def incr(key: str, amount: int = 1) -> Optional[int]:
        try:
            result = redis_write.incrby(key, amount)
            logger.debug(f"INCR '{key}' => {result}")
            return result
        except RedisError as e:
            logger.warning(f"INCR error for key '{key}': {str(e)}")
            return None


    @staticmethod
    def hincrby(hash_key: str, field: str, amount: int = 1) -> Optional[int]:
        try:
            result = redis_write.hincrby(hash_key, field, amount)
            logger.debug(f"HINCRBY '{hash_key}'['{field}'] by {amount} => {result}")
            return result
        except RedisError as e:
            logger.warning(f"HINCRBY error for hash '{hash_key}', field '{field}': {str(e)}")
            return None


    @staticmethod
    def quit():
        try:
            if redis_read != redis_write:
                redis_read.close()
                logger.debug("Redis read connection closed")
            redis_write.close()
            logger.debug("Redis write connection closed")
        except RedisError as e:
            logger.warning(f"Redis connection failed to close: {str(e)}")


    @staticmethod
    def exists(key: str) -> bool:
        try:
            exists = redis_read.exists(key)
            logger.debug(f"Key '{key}' exists: {bool(exists)}")
            return bool(exists)
        except RedisError as e:
            logger.warning(f"Error checking existence of key '{key}': {str(e)}")
            return False

    @staticmethod
    def read_all():
        try:
            keys = redis_read.keys("*")
            if not keys:
                logger.debug("No keys found")
                return
            logger.debug("Redis data:")
            for key in keys:
                val = redis_read.get(key)
                logger.debug(f"{key} => {val}")
        except RedisError as e:
            logger.warning(str(e))

    @staticmethod
    def delete(key: str):
        redis_read.delete(key)

    @staticmethod
    def delete_all():
        try:
            keys = redis_read.keys("*")
            if not keys:
                logger.debug("No keys found")
                return
            redis_write.delete(*keys)
        except RedisError as e:
            logger.warning(str(e))

    @staticmethod
    def flush_all():
        try:
            res = redis_write.execute_command("FLUSHALL")
            logger.info(f"FLUSHALL returns: {res}")
        except RedisError as e:
            logger.warning(str(e))



    @staticmethod
    def setTimestamp(key: str):
        try:
            timestamp = datetime.utcnow().isoformat()
            redis_write.set(key, timestamp)
            logger.debug(f"Set redis {key} => {timestamp}")
        except RedisError as e:
            logger.warning(f"Error setting redis {key}: {str(e)}")

    @staticmethod
    def getTimestamp(key: str) -> Optional[Dict[str, object]]:
        try:
            timestamp_str = redis_read.get(key)
            if not timestamp_str:
                return None

            # Parse the ISO format timestamp
            dt = datetime.fromisoformat(timestamp_str)
            formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")
            timestamp_number = int(dt.timestamp())

            logger.debug(f"Get redis {key} => {formatted_date} ({timestamp_number})")
            return {
                "formatted_date": formatted_date,
                "timestamp_number": timestamp_number
            }
        except (RedisError, ValueError) as e:
            logger.warning(f"Error getting or parsing redis {key}: {str(e)}")
            return None


def init_redisclient(config: dict):
    global redis_write, redis_read

    try:
        write_node = config["redis"]["write"][0]
        read_node = config["redis"]["read"][0] if config["redis"]["read"] else write_node

        write_key = f"{write_node.get('host', '')}:{write_node.get('port', '')}:{write_node.get('username', '')}"
        read_key = f"{read_node.get('host', '')}:{read_node.get('port', '')}:{read_node.get('username', '')}"

        write_config = convert_redis_config(write_node, readonly=False)
        read_config = convert_redis_config(read_node, readonly=True)

        if not write_config:
            logger.error("Failed to initialize Redis write client: write_config is empty or invalid.")
            redis_write = None
            redis_read = None
            return

        redis_write = Redis(**write_config)

        if not read_config:
            logger.warning("Read config is empty or invalid. Using write client for read operations.")
            redis_read = redis_write
        else:
            redis_read = redis_write if read_key == write_key else Redis(**read_config)

        logger.debug("Redis clients initialized successfully.")

    except KeyError as e:
        logger.error(f"Missing Redis config key: {e}")
        redis_write = None
        redis_read = None

    except IndexError as e:
        logger.error(f"Redis config list is empty: {e}")
        redis_write = None
        redis_read = None

    except Exception as e:
        logger.error(f"Unexpected error during Redis initialization: {e}")
        redis_write = None
        redis_read = None

redis = RedisClient()