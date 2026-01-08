from dataclasses import dataclass
from typing import List, Optional, Literal

@dataclass
class TLSCertificate:
    ca: str

@dataclass
class RedisConfig:
    port: int
    host: str
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: Optional[str] = None
    tls: Optional[TLSCertificate] = None

@dataclass
class Redis:
    write: List[RedisConfig]
    read: List[RedisConfig]

@dataclass
class GlobalConfig:
    logLevel: Optional[Literal['error', 'warn', 'info', 'debug', 'silly']]
    environment: Literal['dev', 'staging', 'production']
    enableServicabilityMetrics: Literal['True', 'False']
    redis: Redis