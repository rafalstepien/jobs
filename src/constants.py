from yarl import URL

BASE_URL = URL("https://justjoin.it/")
PYTHON_BOARD_ENDPOINT = "job-offers/all-locations/python"
BOARD_URL__PYTHON = BASE_URL / PYTHON_BOARD_ENDPOINT
BOARD_URL__PYTHON_AND_RUST = BOARD_URL__PYTHON.with_query(skills="Rust")

SINGLE_JOB_CLASS_NAME = "offer-card"
SINGLE_JOB_TAG_NAME = "a"
