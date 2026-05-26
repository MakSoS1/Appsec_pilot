"""Dramatiq-compatible worker placeholder.

The MVP API uses FastAPI BackgroundTasks for local demo scans. This module exists so Docker
Compose and future queue deployments have a stable entrypoint.
"""

import time


def main() -> None:
    print("AppSec Pilot worker ready. API-triggered scans run through the same scan service.")
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
