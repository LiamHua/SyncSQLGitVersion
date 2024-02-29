# Description: This file is the main file for the project. It will be used to run the project.

import datetime
import re
from sched import scheduler
import sys
from Sync.syncSqVersion import SyncSqlVersion


if __name__ == "__main__":
    str = "2024-01-24 21:25:56.83"
    date_str = str.strftime("%Y-%m-%d %H:%M:%S")
    # create_date_formatted = datetime.datetime.strptime(
    #     "2024-01-24 21:25:56.83", "%Y-%m-%d %H:%M:%S.%f"
    # ).strftime("%Y-%m-%d %H:%M:%S")

    print(date_str)
