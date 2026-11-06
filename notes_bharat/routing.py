"""BharatCode routing + budget display logic.

This is the sharpened product idea, deliberately boring in the
right way: nothing here invents an API feature.

- BharatCode is one model API in front of open-weight models. The
  model string is a plain model id (e.g. ``qwen-3.8-27b``,
  ``deepseek-v4.1-flash``) — both live on https://www.bharatcode.ai/.
  Switching models changes the string, not the code.
- Routing in this project is therefore a *visible decision*: which
  model was chosen, why, what the fallback chain is, and which routes
  were actually attempted. The UI shows that panel for every answer,
  so a judge can see the BharatCode call instead of taking it on trust.
- Fallback is local and honest: if the primary call raises, the
  fallback provider (if configured) is tried once. If both fail, the
  answer fails loudly — no fabricated answer, no silent guess.
- Budget has two layers, and the UI must never conflate them:
  (a) the local session budget in this app (calls used / remaining
  in this run, enforced in agent.py), shown as a meter;
  (b) the BharatCode-side usage in the user's BharatCode account
  (students: Qwen free up to 10M tokens a day, per bharatcode.ai),
  which this app cannot see — so the UI says "check your BharatCode
  account" instead of inventing a number.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Route:
    provider: str
    model: str
    reason: str


@dataclass
class RoutingInfo:
    """Everything the UI routing panel needs, in one serialisable shape."""

    gateway: str
    mode: str  # "mock" | "real-bharatcode"
    chosen: Route | None
    fallback_chain: list[Route] = field(default_factory=list)
    attempted: list[str] = field(default_factory=list)
    fallback_used: bool = False
    refused_before_routing: bool = False

    def to_dict(self) -> dict:
        return {
            "gateway": self.gateway,
            "mode": self.mode,
            "mode_label": "[mock] offline stand-in — no live BharatCode call"
            if self.mode == "mock"
            else "real BharatCode API",
            "chosen": (
                {"provider": self.chosen.provider, "model": self.chosen.model, "reason": self.chosen.reason}
                if self.chosen
                else None
            ),
            "fallback_chain": [
                {"provider": r.provider, "model": r.model, "reason": r.reason}
                for r in self.fallback_chain
            ],
            "attempted": list(self.attempted),
            "fallback_used": self.fallback_used,
            "refused_before_routing": self.refused_before_routing,
        }


def parse_model(model: str) -> tuple[str, str]:
    """Validate a BharatCode model id. BharatCode models are plain ids
    (``qwen-3.8-27b``), not ``provider:model`` strings. Returns
    ("bharatcode", model). Raises ValueError if malformed."""
    if not model or not model.strip():
        raise ValueError("Model id is empty; use e.g. qwen-3.8-27b")
    clean = model.strip()
    if any(ch.isspace() for ch in clean):
        raise ValueError(f"Model id must not contain spaces, got {model!r}")
    return "bharatcode", clean


def choose_route(
    model: str,
    fallback_model: str | None = None,
    user_selected: bool = False,
    gateway: str = "https://bharatcode.ai",
    mode: str = "mock",
) -> RoutingInfo:
    """Build the routing decision for one answer.

    Rules, in order (all visible in the UI, none hidden):
    1. If the user picked a model in the UI/CLI, that model is chosen
       and the reason says so.
    2. Otherwise the configured default model is chosen.
    3. A fallback model, if configured, is listed as the fallback
       chain — it is only *attempted* if the primary call raises.
    """
    provider, clean_model = parse_model(model)
    reason = (
        "User-selected model — sent to the BharatCode API unchanged"
        if user_selected
        else "Default model from configuration — sent to the BharatCode API unchanged"
    )
    chosen = Route(provider=provider, model=clean_model, reason=reason)
    chain: list[Route] = []
    if fallback_model:
        fb_provider, fb_clean = parse_model(fallback_model)
        chain.append(
            Route(
                provider=fb_provider,
                model=fb_clean,
                reason="Fallback — tried only if the primary BharatCode call fails",
            )
        )
    return RoutingInfo(gateway=gateway, mode=mode, chosen=chosen, fallback_chain=chain)


@dataclass
class BudgetTracker:
    """Local session budget. Counts provider attempts, not answers.

    A refused question (no matching notes) makes no provider call,
    so it must not consume budget — the refusal test pins this.
    """

    limit: int
    used: int = 0

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.used)

    @property
    def percent_used(self) -> int:
        if self.limit <= 0:
            return 100
        return min(100, round(100 * self.used / self.limit))

    @property
    def exhausted(self) -> bool:
        return self.used >= self.limit

    def charge(self) -> None:
        if self.exhausted:
            raise RuntimeError("LLM call budget for this run exceeded")
        self.used += 1

    def to_dict(self) -> dict:
        return {
            "used": self.used,
            "limit": self.limit,
            "remaining": self.remaining,
            "percent_used": self.percent_used,
            "exhausted": self.exhausted,
            # BharatCode-side budget is NOT this number. See module docstring.
            "gateway_budget_note": (
                "BharatCode-side usage lives in your BharatCode account "
                "(students: Qwen free up to 10M tokens a day, per bharatcode.ai) "
                "and is not visible from this app. This meter is the local session budget only."
            ),
        }
