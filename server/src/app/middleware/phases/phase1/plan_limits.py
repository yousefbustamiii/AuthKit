from dataclasses import dataclass

@dataclass(frozen=True)
class PlanLimits:
    rps: int | None = None       # requests per second  (window = 1s)
    rpm: int | None = None       # requests per minute  (window = 60s)
    rpd: int | None = None       # requests per day     (window = 86400s)
    rpw: int | None = None       # requests per week    (window = 604800s)
    rpmonth: int | None = None   # requests per month   (window = 2592000s)

    def __post_init__(self) -> None:
        if all(v is None for v in (self.rps, self.rpm, self.rpd, self.rpw, self.rpmonth)):
            raise ValueError("PlanLimits must define at least one rate limit window")
