import os
import logging
import datetime
import json
import base64
import subprocess
from config import Config

logging.basicConfig(
    format="%(asctime)s %(funcName)s %(levelname)s: %(message)s", level=logging.INFO
)


def _default_data():
    return {"exports": {}}

def create_fake_data():
    """
    Create fake data in root folder
    """
    import random

    c = Config()
    for export in range(0, 4):
        for user in range(0, 4):
            dirs = os.path.join(
                c.get("ROOT_FOLDER"),
                f"export{str(export)}",
                "application",
                f"user{str(user)}",
                "folder",
            )
            os.makedirs(dirs)
            with open(os.path.join(dirs, "file"), "wb") as f:
                for _ in range(random.randint(100000, 300000)):
                    f.write(b"\0")


def traverse_level(root, level):
    """
    Traverse directories down to specific level and return the results
    """
    if level < 0:
        return []
    result = []
    for entry in os.scandir(root):
        if entry.is_dir(follow_symlinks=False):
            if level == 0:
                result.append(entry.path)
            else:
                result.extend(traverse_level(entry.path, level - 1))
    return result


def disk_usage():
    """
    Loop through folders get their disk usage grouped by export and folder as a dict
    """
    c = Config()
    usage = _default_data()
    for dir in traverse_level(c.get("ROOT_FOLDER"), c.get("FOLDER_REPORTING_DEPTH")):
        parent = dir[len(c.get("ROOT_FOLDER")) + len(os.path.sep) :].split(os.path.sep)[
            c.get("EXPORT_REPORTING_DEPTH")
        ]
        if not usage["exports"].get(parent):
            usage["exports"][parent] = {"folders": {}}
        cmd = ["pdu", "--bytes-format=plain", "--max-depth=1", dir]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        du = result.stdout.split()[0]
        folder = os.path.basename(dir)
        if not usage["exports"][parent].get(folder):
            usage["exports"][parent]["folders"][folder] = {}
        usage["exports"][parent]["folders"][folder]["bytes"] = du
    return usage


def get_kube_namespace():
    """
    Get the namespace from the pod's service account or return default
    """
    try:
        with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as f:
            namespace = f.read().strip()
        if namespace:
            return namespace
    except Exception:
        pass
    return "default"


def read_usage_from_kube_secret():
    """
    Read the disk usage from the configured kube secret
    """
    logging.info("Reading usage from kube secret")
    c = Config()
    try:
        secret = c.kube_client.read_namespaced_secret(
            namespace=get_kube_namespace(), name=c.get("KUBE_USAGE_SECRET")
        )
        if secret and secret.data:
            encoded = secret.data[c.get("KUBE_USAGE_KEY")]
            decoded = base64.b64decode(encoded).decode("utf-8")
            return json.loads(decoded)
    except Exception as e:
        logging.exception(e)
    return None


def write_disk_usage_to_kube_secret(usage):
    """
    Write the disk usage to the configured kube secret
    """
    logging.info("Writing usage to kube secret")
    c = Config()
    usage = json.dumps(usage)
    encoded = base64.b64encode(str.encode(usage)).decode("utf-8")
    c.kube_client.patch_namespaced_secret(
        namespace=get_kube_namespace(),
        name=c.get("KUBE_USAGE_SECRET"),
        body={"data": {c.get("KUBE_USAGE_KEY"): encoded}},
    )


def get_usage_from_usage_file():
    """
    Read disk usage from local file
    """
    c = Config()
    usage_file = c.get("USAGE_FILE")
    if usage_file and os.path.isfile(usage_file):
        with open(usage_file) as uf:
            return json.load(uf)
    return _default_data()


def read_usage():
    """
    Read disk usage from local file or kube state
    """
    c = Config()
    # Always use usage file if we're working in local state.
    if c.get("USE_LOCAL_STATE"):
        return get_usage_from_usage_file()
    # Use kube state if set.
    if c.get("USE_KUBE_STATE"):
        # Bypass if usage file is also set. The writing process will handle this.
        if c.get("USAGE_FILE"):
            return get_usage_from_usage_file()
        if (
            c.get("LAST_READ_TIME")
            + datetime.timedelta(seconds=c.get("CACHED_READ_THRESHOLD_SECONDS"))
            > datetime.datetime.now()
        ):
            logging.info("Using cached read")
            return c.get("CACHED_USAGE")
        usage = read_usage_from_kube_secret()
        c.set("LAST_READ_TIME", datetime.datetime.now())
        c.set("CACHED_USAGE", usage)
        return usage
    return _default_data()


def write_disk_usage():
    """
    Write disk usage to local file or kube state
    """
    c = Config()
    usage = disk_usage()
    if c.get("USE_LOCAL_STATE"):
        with open(c.get("USAGE_FILE"), "w") as json_file:
            json.dump(usage, json_file)
    elif c.get("USE_KUBE_STATE"):
        write_disk_usage_to_kube_secret(usage)
