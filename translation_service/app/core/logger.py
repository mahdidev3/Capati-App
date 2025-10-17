import logging

logging.basicConfig(
    filename="error.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)