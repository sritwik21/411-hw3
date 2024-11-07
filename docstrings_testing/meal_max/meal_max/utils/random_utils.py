import logging
import requests

from meal_max.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


def get_random() -> float:
    """
    Fetches a random decimal number from random.org.

    Makes a GET request to random.org to retrieve a random decimal fraction.
    Logs the request and handles any errors during the request process.

    Returns:
        float: A random decimal number from random.org.

    Raises:
        ValueError: If the response from random.org cannot be converted to a float.
        RuntimeError: If the request to random.org fails or times out.

    Logs:
        Info log before making the request to random.org.
        Info log with the received random number.
        Error log if the request times out or fails.
    """
    url = "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new"

    try:
        # Log the request to random.org
        logger.info("Fetching random number from %s", url)

        response = requests.get(url, timeout=5)

        # Check if the request was successful
        response.raise_for_status()

        random_number_str = response.text.strip()

        try:
            random_number = float(random_number_str)
        except ValueError:
            raise ValueError("Invalid response from random.org: %s" % random_number_str)

        logger.info("Received random number: %.3f", random_number)
        return random_number

    except requests.exceptions.Timeout:
        logger.error("Request to random.org timed out.")
        raise RuntimeError("Request to random.org timed out.")

    except requests.exceptions.RequestException as e:
        logger.error("Request to random.org failed: %s", e)
        raise RuntimeError("Request to random.org failed: %s" % e)
