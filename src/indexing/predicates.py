import json
import hashlib


def create_predicate_index(predicates):
    def normalize_section(section):
        return sorted(
            [json.dumps(predicate, sort_keys=True) for predicate in section],
            key=lambda x: x
        )

    normalized = {
        "where": normalize_section(predicates["where"]),
        "joins": normalize_section(predicates["joins"]),
        "having": normalize_section(predicates["having"])
    }

    serialized = json.dumps(normalized, sort_keys=True).encode("utf-8")

    return hashlib.sha1(serialized).hexdigest()
