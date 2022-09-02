import os
import time
import random
from prometheus_client import start_http_server, Histogram, Counter, REGISTRY
from configuration import Configuration

# Create Prometheus metrics
histogram = Histogram(
    name="http_request_duration_seconds",
    documentation="HTTP request duration in seconds",
    labelnames=["method", "status", "endpoint", "path"]
)

counter = Counter(
    name="http_request_total",
    documentation="Total number of HTTP requests",
    labelnames=["method", "status", "endpoint", "path"]
)


def is_under_percent(percentage):
    """
    Generates a random number between 0 and 100 and then tests it against the specified percentage. The purpose
    of this function is to easily determine if a request should be handled as an error or a spike. For example, if the
    percentage is 5 and the random number is 3, then it returns True, but if the random number is 15 then it won't.
    :param percentage: the percentage to test against
    :return: True if the percentage is under the random number, else False
    """
    value = random.randint(0, 100)
    if percentage >= value:
        return True
    return False


def generate_response_time(path):
    """
    Generates the response time for the specified path. This function uses the percent_spike to determine if the
    response time should be a spike or a normal response time. Then it calculates the response time based on the
    average and delta values in the configuration file.
    :param path: the path for which to generate the response time
    :return: the response time for the request
    """
    if is_under_percent(path['percent_spike']):
        # Calculate the response time from the spike configuration
        average = path['spike']['average']
        delta = path['spike']['delta']
    else:
        # Calculate the response time from the normal configuration
        average = path['response_time']['average']
        delta = path['response_time']['delta']

    # Calculate the lower and upper bounds
    lower_bound = average - delta
    upper_bound = average + delta

    # Generate a random number in the range of upper - lower, and add it to the lower
    return lower_bound + (random.random() * (upper_bound - lower_bound))


def get_error_code(path):
    """
    Randomly picks an error code from the list of error codes defined for this path.
    :param path: the path object from which to pick an error code
    :return: a randomly chosen error code
    """
    error_codes = path['error_codes']
    return error_codes[random.randint(0, len(error_codes) - 1)]


def update_metrics():
    endpoint = configuration.get_endpoint()
    paths = configuration.get_paths()
    for path in paths:
        p = path['path']
        for i in range(p['requests_per_second']):
            # Calculate the response time
            response_time = generate_response_time(p)

            # Load our request information
            verb = p['verb']

            # See if this is an error or success
            if not is_under_percent(p['percent_error']):
                # Handle normal condition
                histogram.labels(p['verb'], p['response_code'], endpoint, p['uri']).observe(response_time)
                counter.labels(p['verb'], p['response_code'], endpoint, p['uri']).inc()
            else:
                # Handle error condition
                error_code = get_error_code(p)
                histogram.labels(p['verb'], error_code, endpoint, p['uri']).observe(response_time)
                counter.labels(p['verb'], error_code, endpoint, p['uri']).inc()


# Start the Prometheus client library HTTP server
start_http_server(8000)

# Load our YAML configuration
configuration = Configuration()

# Start executing simulated metrics in an infinite loop with a 1 second sleep time
while True:
    update_metrics()
    time.sleep(1)

