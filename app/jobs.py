import logging
import schedule
import time
import utils
from config import Config

logging.basicConfig(
    format="%(asctime)s %(funcName)s %(levelname)s: %(message)s", level=logging.INFO
)


def write_disk_usage_job():
    try:
        logging.info("Writing disk usage")
        utils.write_disk_usage()
    except Exception as e:
        logging.error(f"Error writing disk usage: {e}")


def main():
    c = Config()

    if c.get("CREATE_FAKE_DATA"):
        utils.create_fake_data()
    if c.get("USAGE_LOOP_MODE") == "second":
        schedule.every(int(c.get("USAGE_LOOP_TIME"))).seconds.do(write_disk_usage_job)
    elif c.get("USAGE_LOOP_MODE") == "day":
        schedule.every().day.at(
            c.get("USAGE_LOOP_TIME"), c.get("USAGE_LOOP_TIMEZONE")
        ).do(write_disk_usage_job)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
