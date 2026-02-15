# Governance Summary

Sentinel Signal provides calibrated scoring for automated decision workflows with governance controls designed for production use.

## What Is Governed

- Model versioning: every scored response includes a `model_version`.
- Calibration integrity: scoring outputs are calibration-aware and monitored for reliability.
- Threshold profiles: operating profiles are controlled and versioned.
- Drift handling: segment-level drift diagnostics can downgrade confidence when distribution shift is detected.

## Validation Focus

The platform validates models across multiple seeds and segments, with emphasis on:
- Discrimination (e.g., AUC)
- Calibration quality (e.g., ECE)
- Concentration and lift metrics in high-risk buckets
- Segment stability by payer and workflow context

## Decision-Support Scope

Sentinel Signal outputs are decision-support signals for workflow orchestration. They are not medical, legal, or payment determinations.

## Governance Intent

The objective is practical production safety:
- deterministic scoring behavior for pinned versions
- transparent model metadata in responses
- controlled degradation under drift conditions
- documented operating profiles for consistent deployment
