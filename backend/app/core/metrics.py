"""Prometheus metric definitions. Kept as a single module so every metric
name is defined exactly once and discoverable in one place — no scattering
`Counter(...)` calls across endpoint files, where two people could
accidentally register the same metric name twice (Prometheus client raises
on that, but only at whatever time that second module happens to import).

`record_request` is called once per request by RequestContextMiddleware;
nothing else in the app needs to touch these directly unless a specific
endpoint wants a custom business metric later (e.g. meals analyzed count),
which should be added here too, not ad-hoc in that endpoint's module.
"""

from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests processed",
    ["method", "path", "status_code"],
)

REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)


def record_request(*, method: str, path: str, status_code: int, duration_seconds: float) -> None:
    REQUEST_COUNT.labels(method=method, path=path, status_code=str(status_code)).inc()
    REQUEST_DURATION_SECONDS.labels(method=method, path=path).observe(duration_seconds)
