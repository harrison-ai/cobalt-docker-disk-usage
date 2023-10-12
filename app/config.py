import logging
import os
import datetime
from kubernetes import client as kube_client, config as kube_config
from dotenv import load_dotenv

logging.basicConfig(
    format="%(asctime)s %(funcName)s %(levelname)s: %(message)s", level=logging.INFO
)


class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            load_dotenv()
            self._config = {
                "USAGE_LOOP_MODE": os.getenv("USAGE_LOOP_MODE", "day"),
                "USAGE_LOOP_TIME": os.getenv("USAGE_LOOP_TIME", "16:00"),
                "USAGE_LOOP_TIMEZONE": os.getenv("USAGE_LOOP_TIMEZONE", "UTC"),
                "ROOT_FOLDER": os.getenv("ROOT_FOLDER", "mnt"),
                "EXPORT_REPORTING_DEPTH": int(os.getenv("EXPORT_REPORTING_DEPTH", "0")),
                "FOLDER_REPORTING_DEPTH": int(os.getenv("FOLDER_REPORTING_DEPTH", "2")),
                "USE_LOCAL_STATE": eval(os.getenv("USE_LOCAL_STATE", "False")),
                "USE_KUBE_STATE": eval(os.getenv("USE_KUBE_STATE", "True")),
                "KUBE_USAGE_KEY": os.getenv("KUBE_USAGE_KEY", "usage.json"),
                "USE_KUBE_CONFIG": eval(os.getenv("USE_KUBE_CONFIG", "False")),
                "KUBE_USAGE_SECRET": os.getenv(
                    "KUBE_USAGE_SECRET", "folder-disk-usage"
                ),
                "USAGE_FILE": os.getenv("USAGE_FILE", None),
                "CACHED_READ_THRESHOLD_SECONDS": int(
                    os.getenv("CACHED_READ_THRESHOLD_SECONDS", "300")
                ),
                "CACHED_USAGE": {},
                "API_WORKERS": int(os.getenv("API_WORKERS", "2")),
                "API_PORT": int(os.getenv("API_PORT", "8000")),
                "API_HOST": os.getenv("API_HOST", "0.0.0.0"),
                "CREATE_FAKE_DATA": eval(os.getenv("CREATE_FAKE_DATA", "False")),
            }
            self.set(
                "LAST_READ_TIME",
                datetime.datetime.now()
                - datetime.timedelta(seconds=self.get("CACHED_READ_THRESHOLD_SECONDS")),
            )
            if self.get("USE_KUBE_STATE"):
                if self.get("USE_KUBE_CONFIG"):
                    kube_config.load_kube_config()
                else:
                    kube_config.load_incluster_config()
                self._kube_client = kube_client.CoreV1Api()
                self.initialized = True

    def get(self, key, default=None):
        return self._config.get(key, default)

    def set(self, key, value):
        self._config[key] = value

    @property
    def kube_client(self):
        return self._kube_client
