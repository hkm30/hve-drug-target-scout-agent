#!/usr/bin/env python3
"""
Drug Target Scout - demo claim verification

Verifies the two factual claims the demo depends on:

  MOMENT A  PubMed EFetch tolerates malformed IDs and returns a real article,
            so it must not be used to verify citation existence.
  MOMENT B  NCT06275724 is a PCSK9-directed therapy trial whose registry
            record never contains the string "PCSK9".

Usage:  python verify_demo_claims.py
Needs:  requests   (pip install requests)

Rate limits: NCBI allows 3 req/s without an API key. This script sleeps
between calls. Do not remove the delays.
"""

import json
import sys
import time

import requests

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CTGOV = "https://clinicaltrials.gov/api/v2"
UA = {"User-Agent": "drug-target-scout-verification/1.0"}
NCBI_DELAY = 0.4

G, R, Y, B, D, X = "\033[32m", "\033[31m", "\033[33m", "\033[34m", "\033[90m", "\033[0m"


def head(text):
    print(f"\n{B}{'=' * 72}\n{text}\n{'=' * 72}{X}")


def naive_pmid_check(pmid):
    """WRONG. EFetch parses leniently: 'ABC123' is read as PMID 123."""
    time.sleep(NCBI_DELAY)
    r = requests.get(
        f"{EUTILS}/efetch.fcgi",
        params={"db": "pubmed", "id": pmid, "retmode": "xml"},
        headers=UA,
        timeout=30,
    )
    body = r.text
    returned = None
    if "<PMID" in body:
        seg = body.split("<PMID", 1)[1]
        returned = seg.split(">", 1)[1].split("<", 1)[0]
    return "<PubmedArticle>" in body, returned


def correct_pmid_check(pmid):
    """RIGHT. ESummary requires an exact UID object with no nested error.

    Returns EXISTS / NOT_EXISTS / UNVERIFIED. Transient failures must never
    be reported as NOT_EXISTS.
    """
    time.sleep(NCBI_DELAY)
    try:
        r = requests.get(
            f"{EUTILS}/esummary.fcgi",
            params={"db": "pubmed", "id": pmid, "retmode": "json"},
            headers=UA,
            timeout=30,
        )
    except requests.RequestException:
        return "UNVERIFIED"
    if r.status_code == 429 or r.status_code >= 500:
        return "UNVERIFIED"
    if r.status_code != 200:
        return "UNVERIFIED"
    try:
        result = r.json().get("result", {})
    except ValueError:
        return "UNVERIFIED"
    entry = result.get(str(pmid))
    if entry is None:
        return "NOT_EXISTS"
    if "error" in entry:
        return "NOT_EXISTS"
    return "EXISTS"


def moment_a():
    head("MOMENT A  Why EFetch must not verify a citation")
    samples = ["ABC123", "99999999999", "42-hallucinated", "31518657"]
    print(f"{'input':<20} {'EFetch (wrong)':<28} {'ESummary (correct)'}")
    print(f"{D}{'-' * 72}{X}")
    trap_fired = False
    for s in samples:
        ok, returned = naive_pmid_check(s)
        verdict = correct_pmid_check(s)
        if ok and returned and returned != s:
            note = f"{R}PASS -> returned PMID {returned}{X}"
            trap_fired = True
        elif ok:
            note = f"{G}pass{X}"
        else:
            note = f"{D}reject{X}"
        color = G if verdict == "EXISTS" else (Y if verdict == "UNVERIFIED" else D)
        print(f"{s:<20} {note:<40} {color}{verdict}{X}")
    print()
    if trap_fired:
        print(f"{R}CONFIRMED{X}  EFetch accepted a malformed id and returned a real article.")
        print("          A verifier built on EFetch would stamp hallucinated")
        print("          citations as verified. Moment A holds.")
    else:
        print(f"{Y}NOT REPRODUCED{X}  EFetch rejected the malformed ids in this run.")
        print("          NCBI behaviour may have changed. Moment A needs rework.")
    return trap_fired


def moment_b(nct="NCT06275724", symbol="PCSK9"):
    head(f"MOMENT B  {nct} is {symbol}-directed but never names {symbol}")
    try:
        r = requests.get(f"{CTGOV}/studies/{nct}", headers=UA, timeout=30)
    except requests.RequestException as exc:
        print(f"{Y}UNVERIFIED{X}  network error: {exc}")
        return None
    if r.status_code != 200:
        print(f"{Y}UNVERIFIED{X}  HTTP {r.status_code}")
        return None

    study = r.json()
    proto = study.get("protocolSection", {})
    ident = proto.get("identificationModule", {})
    design = proto.get("designModule", {})
    status = proto.get("statusModule", {})
    arms = proto.get("armsInterventionsModule", {})

    print(f"  NCT ID        {ident.get('nctId')}")
    print(f"  Title         {ident.get('briefTitle', '')[:60]}")
    print(f"  Sponsor       {proto.get('sponsorCollaboratorsModule', {}).get('leadSponsor', {}).get('name')}")
    ivs = [i.get("name") for i in arms.get("interventions", [])]
    print(f"  {Y}Intervention  {', '.join(filter(None, ivs))}{X}")
    print(f"  Conditions    {', '.join(proto.get('conditionsModule', {}).get('conditions', []))}")
    print(f"  Phase         {', '.join(design.get('phases', [])) or 'n/a (observational)'}")
    print(f"  Status        {status.get('overallStatus')}")

    blob = json.dumps(study, ensure_ascii=False)
    hits = blob.upper().count(symbol.upper())
    print()
    color = G if hits else R
    print(f'  >> occurrences of "{symbol}" in the full record JSON: {color}{hits}{X}')
    print()
    if hits == 0:
        print(f"{R}CONFIRMED{X}  Retrieval by target symbol cannot reach this trial.")
        print("          Moment B holds.")
    else:
        print(f"{Y}NOT REPRODUCED{X}  The record now contains the symbol.")
        print("          Registry content changed. Moment B needs a new example.")
    return hits


def moment_b_search(nct="NCT06275724", symbol="PCSK9"):
    """Cross-check: does a target-symbol query return this trial?"""
    print(f"\n{D}  cross-check: query.term={symbol} filtered to {nct}{X}")
    try:
        r = requests.get(
            f"{CTGOV}/studies",
            params={"query.term": symbol, "filter.ids": nct, "countTotal": "true"},
            headers=UA,
            timeout=30,
        )
        n = r.json().get("totalCount", "?")
        print(f"  matches: {R if n == 0 else G}{n}{X}")
    except (requests.RequestException, ValueError) as exc:
        print(f"  {Y}cross-check unavailable: {exc}{X}")


if __name__ == "__main__":
    print(f"{B}Drug Target Scout - demo claim verification{X}")
    print(f"{D}run this before the demo; both moments must be CONFIRMED{X}")
    a = moment_a()
    b = moment_b()
    moment_b_search()
    head("SUMMARY")
    print(f"  Moment A (EFetch trap)      {G + 'CONFIRMED' + X if a else R + 'FAILED' + X}")
    print(f"  Moment B (NCT06275724)      {G + 'CONFIRMED' + X if b == 0 else R + 'FAILED' + X}")
    print()
    sys.exit(0 if (a and b == 0) else 1)
