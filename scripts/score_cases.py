"""Validate research assessments and calculate heuristic scores. Standard library only."""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

VERSION = "research-v1.0"
WEIGHTS = {
    "credibility": {
        "source_reliability": 15, "firsthand": 15, "domain_fit": 15,
        "verifiability": 20, "corroboration": 25, "incentive_transparency": 10,
    },
    "opportunity": {
        "novelty": 20, "expectation_gap": 25, "materiality": 25,
        "timeliness": 15, "scarcity": 15,
    },
}
GATES = {
    "fact_status", "mapping_verified", "counterevidence_checked",
    "material_contradiction_unresolved", "expectation_baseline_established",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def timestamp(value, label):
    require(nonempty(value), f"{label}: expected ISO 8601 timestamp")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label}: invalid timestamp") from exc
    require(result.tzinfo is not None, f"{label}: timezone required")
    return result


def check_refs(refs, evidence_ids, label, required=False):
    require(isinstance(refs, list), f"{label}: expected list")
    require(all(nonempty(r) for r in refs), f"{label}: expected string IDs")
    require(len(refs) == len(set(refs)), f"{label}: duplicate references")
    require(all(r in evidence_ids for r in refs), f"{label}: unknown evidence ID")
    require(not required or bool(refs), f"{label}: evidence required")


def score_case(case):
    require(isinstance(case, dict), "case must be an object")
    require(nonempty(case.get("case_id")), "case_id required")
    cutoff = timestamp(case.get("as_of"), "as_of")
    evidence = case.get("evidence")
    require(isinstance(evidence, list), "evidence must be a list")
    ids = set()
    for item in evidence:
        require(isinstance(item, dict), "evidence item must be an object")
        eid = item.get("id")
        require(nonempty(eid) and eid not in ids, "evidence ID missing or duplicated")
        require(item.get("kind") in ("source", "search_log", "analysis"), f"{eid}: invalid kind")
        require(nonempty(item.get("locator")), f"{eid}: locator required")
        require(nonempty(item.get("summary")), f"{eid}: summary required")
        require(timestamp(item.get("available_at"), f"{eid}.available_at") <= cutoff,
                f"{eid}: evidence is later than as_of")
        ids.add(eid)

    assessments = case.get("assessments")
    require(isinstance(assessments, dict) and set(assessments) == set(WEIGHTS),
            "assessments must contain exactly credibility and opportunity")
    scores = {}
    for group, weights in WEIGHTS.items():
        values = assessments[group]
        require(isinstance(values, dict) and set(values) == set(weights),
                f"{group}: missing or unexpected dimensions")
        known_weight = 0
        weighted_value = 0
        missing = []
        for dimension, weight in weights.items():
            item = values[dimension]
            label = f"{group}.{dimension}"
            require(isinstance(item, dict) and "value" in item, f"{label}: value required")
            value = item["value"]
            require(value is None or (type(value) is int and 0 <= value <= 4),
                    f"{label}: value must be null or integer 0..4")
            require(nonempty(item.get("reason")), f"{label}: reason required")
            check_refs(item.get("evidence_refs"), ids, label, required=value is not None)
            if value is None:
                missing.append(dimension)
            else:
                known_weight += weight
                weighted_value += weight * value
        priority = weighted_value / 4
        scores[group] = {
            "observed_score": round(priority * 100 / known_weight, 2) if known_weight else None,
            "coverage": known_weight / 100,
            "priority_score": priority,
            "missing_dimensions": missing,
        }

    gates = case.get("gates")
    gate_refs = case.get("gate_evidence")
    require(isinstance(gates, dict) and set(gates) == GATES, "missing or unexpected gates")
    require(isinstance(gate_refs, dict) and set(gate_refs) == GATES, "gate_evidence keys must match gates")
    require(gates["fact_status"] in ("unverified", "corroborated", "conflicted", "refuted"),
            "invalid fact_status")
    for name in GATES:
        value = gates[name]
        if name == "fact_status":
            needs_evidence = value != "unverified"
        else:
            require(value is None or type(value) is bool, f"{name}: expected boolean or null")
            needs_evidence = value is not None
        check_refs(gate_refs[name], ids, f"gate_evidence.{name}", required=needs_evidence)

    gap = assessments["opportunity"]["expectation_gap"]["value"]
    require(gap is None or gates["expectation_baseline_established"] is True,
            "expectation_gap requires an established baseline")
    require(gates["expectation_baseline_established"] is not True or gap is not None,
            "established baseline requires an assessed expectation_gap")

    reasons = []
    if gates["fact_status"] == "refuted":
        state, reasons = "rejected", ["关键事实已被反证推翻"]
    elif gates["fact_status"] == "conflicted" or gates["material_contradiction_unresolved"] is True:
        state, reasons = "conflicted", ["存在重大未解决冲突"]
    else:
        for ok, reason in (
            (gates["fact_status"] == "corroborated", "关键事实待核验"),
            (gates["mapping_verified"] is True, "公司经济关联待核验"),
            (gates["counterevidence_checked"] is True, "反证检索未完成"),
            (gates["material_contradiction_unresolved"] is False, "重大冲突情况未知"),
        ):
            if not ok:
                reasons.append(reason)
        if reasons:
            state = "needs_verification"
        else:
            if gates["expectation_baseline_established"] is not True:
                reasons.append("缺少可比较的同期预期基线")
            for group, score in scores.items():
                if score["coverage"] < .8:
                    reasons.append(f"{group}: 信息覆盖率低于 80%")
                if score["priority_score"] < 70:
                    reasons.append(f"{group}: 排序分低于 70")
            state = "watchlist" if reasons else "research_candidate"
            if not reasons:
                reasons = ["满足默认研究候选门槛；尚未验证投资收益"]
    return {
        "case_id": case["case_id"], "as_of": case["as_of"], "rule_version": VERSION,
        "scores": scores, "research_state": state, "state_reasons": reasons,
    }


def score_batch(data):
    cases = data if isinstance(data, list) else [data]
    require(bool(cases), "empty case list")
    results = [score_case(case) for case in cases]
    require(len({r["case_id"] for r in results}) == len(results), "duplicate case_id in batch")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        results = score_batch(json.loads(args.input.read_text(encoding="utf-8-sig")))
        payload = json.dumps(results, ensure_ascii=False, indent=2, allow_nan=False)
        if args.out:
            require(args.out.resolve() != args.input.resolve(), "output must not overwrite input")
            # Refuse silent replacement of a previous research snapshot.
            with args.out.open("x", encoding="utf-8") as stream:
                stream.write(payload + "\n")
        else:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
            print(payload)
    except (ValueError, TypeError, OSError) as exc:
        print(f"Invalid input or output: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
