import json

from bloom_filter2 import BloomFilter


def create_predicate_bloom(predicates):
    bloom = BloomFilter(max_elements=100, error_rate=0.001)
    for section in ("where", "joins", "having"):
        for pred in predicates[section]:
            bloom.add(json.dumps(pred, sort_keys=True))
    return bloom
