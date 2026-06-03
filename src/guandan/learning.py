"""Public learning architecture sketches for Guandan AI.

The open-source package does not ship trained weights. This module publishes
the model shapes, record schemas, and milestone metadata used by the research
track so they can be inspected and tested without requiring PyTorch.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ModelArchitecture:
    """Inspectable neural architecture metadata."""

    name: str
    visibility: str
    state_view: str
    state_features: str
    action_features: str
    trunk: str
    heads: tuple[str, ...]
    training_signal: str
    release_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TrainingMilestone:
    """A compact public record of a training route decision."""

    date: str
    route: str
    artifact_type: str
    signal: str
    outcome: str
    lesson: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


PUBLIC_POLICY_VALUE = ModelArchitecture(
    name="public_policy_value_candidate_scorer",
    visibility="public information plus known team hands",
    state_view="current player, partnership, played cards, public history, known team cards",
    state_features="public-state vector optionally extended with behavior/pass-history features",
    action_features="candidate-action vector for one legal action",
    trunk="state MLP embedding plus per-candidate state-action MLP",
    heads=(
        "policy score for each legal candidate action",
        "team win-probability value",
        "single-game utility value",
    ),
    training_signal=(
        "search-labeled candidate scores, behavior/self-play labels, and whole-game value targets"
    ),
    release_boundary="must pass paired swapped-seat gates and old-pool regression before use",
)

FULL_INFO_TEACHER = ModelArchitecture(
    name="full_info_outcome_oracle_teacher",
    visibility="full information, offline only",
    state_view="all four hands, full public history, current trick, finish order",
    state_features="full-state vector for offline teacher and sparring models",
    action_features="all legal root actions, not limited to an older model's candidate pool",
    trunk="full-state action scorer combined with bounded complete-continuation search",
    heads=(
        "full-information action prior",
        "offline outcome estimate",
    ),
    training_signal="paired game outcomes and forced-root counterfactuals",
    release_boundary="teacher data only; not fair public-information runtime play",
)

POLICY_ONLY_STUDENT = ModelArchitecture(
    name="policy_only_outcome_oracle_student",
    visibility="full information, offline distillation artifact",
    state_view="full-state teacher-record rows",
    state_features="frozen teacher state encoder",
    action_features="candidate-action vectors for all exported legal actions",
    trunk="frozen state/value components with trainable action and policy heads",
    heads=("policy distribution over teacher-selected legal actions",),
    training_signal="policy-only teacher rows with value_target_weight = 0",
    release_boundary=(
        "valid only after fresh gameplay gates; better teacher-label fit is not release evidence"
    ),
)

ARCHITECTURES: tuple[ModelArchitecture, ...] = (
    PUBLIC_POLICY_VALUE,
    FULL_INFO_TEACHER,
    POLICY_ONLY_STUDENT,
)

TRAINING_MILESTONES: tuple[TrainingMilestone, ...] = (
    TrainingMilestone(
        "2026-04-28",
        "v7 public policy",
        "policy checkpoint",
        "paired direct gates versus older policies",
        "retained as early public-policy baseline",
        "seat-swapped gates became mandatory after earlier seat-bias failures",
    ),
    TrainingMilestone(
        "2026-04-29",
        "v8-v11 public policy/value",
        "joint policy-value route",
        "search labels, guard alignment, and whole-game value calibration",
        "v11 guard-aligned branch retained; two offline-strong v11 attempts rejected",
        "offline top1 is weaker evidence than paired gameplay",
    ),
    TrainingMilestone(
        "2026-05-03",
        "portfolio and loss distillation",
        "multi-model candidate pool",
        "old-pool loss records and strong-search labels",
        "mixed results; kept research-only",
        "portfolio coverage can help one opponent style while regressing another",
    ),
    TrainingMilestone(
        "2026-05-05",
        "full-state exact-race distillation",
        "full-information policy scorer",
        "short-race exact labels and human-loss states",
        "useful teacher/sparring model, not fair public play",
        "some tactical knowledge depends on hidden cards and cannot be public-policy distilled directly",
    ),
    TrainingMilestone(
        "2026-05-06",
        "human-hard public repair",
        "public policy checkpoint route",
        "90 human hard labels plus old-pool retention records",
        "offline hard-label agreement improved, but old-pool gates blocked promotion",
        "human-loss repairs need explicit older-style negative examples",
    ),
    TrainingMilestone(
        "2026-05-07",
        "risk and pass-specialist heads",
        "auxiliary diagnostic heads",
        "trajectory-risk labels and pass-with-response hard states",
        "useful diagnostics, but broad runtime overrides stayed research-only",
        "risk heads should advise candidate generation before becoming action gates",
    ),
    TrainingMilestone(
        "2026-05-09",
        "Team-Q role/risk route",
        "teamplay auxiliary route",
        "role labels, risk labels, and rejection-safety sweeps",
        "diagnostic value retained; hard pass gates rejected",
        "teamplay features need counterfactual evidence before runtime use",
    ),
    TrainingMilestone(
        "2026-05-17",
        "V42 belief-PUCT and public-payload CF",
        "belief-search trace route",
        "distributed traces, hard-example mining, and replay counterfactual labels",
        "strength failed, but direct public-payload CF became usable",
        "failed H2H runs can still create valuable supervised hard examples",
    ),
    TrainingMilestone(
        "2026-05-29",
        "V43/V44 full-info search diagnostics",
        "offline full-information search route",
        "return-only RL, all-legal priors, and root-action repair",
        "direct all-legal argmax route rejected",
        "all-legal search needs gameplay gates even when prior validation looks strong",
    ),
    TrainingMilestone(
        "2026-06-02",
        "V45 outcome-oracle teacher",
        "offline full-information teacher",
        "166/192 paired swapped-seat wins across retained old-pool opponents",
        "cleared research target for policy-only student data preparation",
        "teacher promotion requires opponent-by-opponent gates, not aggregate strength alone",
    ),
    TrainingMilestone(
        "2026-06-03",
        "V45 policy-only student",
        "offline student checkpoint",
        "1,041 teacher rows; frozen state/value components; improved teacher-label fit",
        "not retained as direct checkpoint or oracle baseline",
        "student distillation can improve label fit while shifting gameplay trajectories",
    ),
    TrainingMilestone(
        "2026-06-03",
        "V46 public belief distillation",
        "public-information student route",
        "hidden-hand samples scored by V45 teacher plus v18 anchor labels",
        "viable but not release/default; anchor labels required",
        "pure full-info teacher labels drift without public-policy retention anchors",
    ),
)


def describe_architectures() -> list[dict[str, Any]]:
    """Return public architecture metadata as plain dictionaries."""

    return [architecture.to_dict() for architecture in ARCHITECTURES]


def describe_training_milestones() -> list[dict[str, str]]:
    """Return compact public training history metadata."""

    return [milestone.to_dict() for milestone in TRAINING_MILESTONES]


def validate_policy_value_record(record: dict[str, Any]) -> list[str]:
    """Validate the public JSONL schema for policy/value training examples.

    The schema is intentionally lightweight. It checks structural consistency
    without assuming that private model features or raw training data are
    present in the open-source repository.
    """

    errors: list[str] = []
    if not isinstance(record.get("state"), dict):
        errors.append("state must be an object")
    actions = record.get("legal_actions")
    if not isinstance(actions, list) or len(actions) < 2:
        errors.append("legal_actions must contain at least two candidate actions")
        actions = []
    scores = record.get("candidate_scores")
    if not isinstance(scores, list):
        errors.append("candidate_scores must be a list")
        scores = []
    if actions and scores and len(actions) != len(scores):
        errors.append("candidate_scores length must match legal_actions length")
    if "selected_index" in record:
        selected = record["selected_index"]
        if not isinstance(selected, int) or selected < 0 or selected >= len(actions):
            errors.append("selected_index must point to a legal action")
    for field in ("target_win", "target_utility"):
        if field in record and not isinstance(record[field], (int, float)):
            errors.append(f"{field} must be numeric when present")
    return errors


def build_optional_torch_public_policy_value_net(
    state_input_size: int,
    action_input_size: int,
    hidden_size: int = 384,
    dropout: float = 0.08,
) -> Any:
    """Build a PyTorch policy-value network when torch is installed.

    PyTorch is optional for the public package. Importing :mod:`guandan.learning`
    never requires torch; this factory raises a clear error only when the caller
    asks for the neural module without installing torch.
    """

    try:
        import torch
        from torch import nn
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise RuntimeError("Install torch to build the optional neural network") from exc

    class PublicPolicyValueNet(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            state_layers: list[nn.Module] = [
                nn.Linear(state_input_size, hidden_size),
                nn.ReLU(),
            ]
            if dropout > 0:
                state_layers.append(nn.Dropout(dropout))
            state_layers.extend([nn.Linear(hidden_size, hidden_size), nn.ReLU()])
            self.state_net = nn.Sequential(*state_layers)
            self.policy_net = nn.Sequential(
                nn.Linear(state_input_size + action_input_size, hidden_size),
                nn.ReLU(),
                nn.Dropout(dropout) if dropout > 0 else nn.Identity(),
                nn.Linear(hidden_size, hidden_size),
                nn.ReLU(),
                nn.Linear(hidden_size, hidden_size // 2),
                nn.ReLU(),
                nn.Linear(hidden_size // 2, 1),
            )
            self.win_head = nn.Sequential(
                nn.Linear(hidden_size, hidden_size // 2),
                nn.ReLU(),
                nn.Linear(hidden_size // 2, 1),
                nn.Tanh(),
            )
            self.utility_head = nn.Sequential(
                nn.Linear(hidden_size, hidden_size // 2),
                nn.ReLU(),
                nn.Linear(hidden_size // 2, 1),
                nn.Tanh(),
            )

        def forward(self, state_x: Any, action_x: Any) -> tuple[Any, Any, Any]:
            state_embed = self.state_net(state_x)
            if action_x.dim() == 2:
                policy_input = torch.cat([state_x, action_x], dim=-1)
                policy = self.policy_net(policy_input).squeeze(-1)
                return (
                    policy,
                    self.win_head(state_embed).squeeze(-1),
                    self.utility_head(state_embed).squeeze(-1),
                )
            batch, candidates, features = action_x.shape
            expanded_state = state_x.unsqueeze(1).expand(-1, candidates, -1)
            policy_input = torch.cat([expanded_state, action_x], dim=-1)
            policy = self.policy_net(
                policy_input.reshape(batch * candidates, state_x.shape[-1] + features)
            ).reshape(batch, candidates)
            return (
                policy,
                self.win_head(state_embed).squeeze(-1),
                self.utility_head(state_embed).squeeze(-1),
            )

    return PublicPolicyValueNet()
