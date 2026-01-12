# Manual Verification Scripts

This directory contains scripts for verifying feature logic without running the full GUI application. These are useful for quick iteration on core logic like health insights, nudges, and database operations.

## Scripts

### 1. `verify_insights_expanded.py`

**Purpose**: Verifies the "Expanded Health Insights" (PR 1.6) logic.
**Checks**:

- Positive reinforcement (Great Sleep, High Energy).
- Neutral/Stable metrics ("Balanced sleep").
- Warnings (Sleep Dept, Low Energy).
- Comprehensive Work/Energy balance checks.

### 2. `verify_quality_logic.py`

**Purpose**: Verifies the Sleep Quality specific logic (PR 1.6 Update).
**Checks**:

- Distinction between "High Duration + High Quality" (Restorative) vs "High Duration + Low Quality" (Restless).
- Database persistence of `sleep_quality` column.

### 3. `verify_integrated_nudges.py` / `_simple.py`

**Purpose**: Verifies the Nudge Logic (PR 1.5).
**Checks**:

- Basic Sleep Debt calculation.
- Burnout warning triggers (consecutive low energy).
- Checks that nudges appear (or return text) under correct conditions.

## Usage

Run any script with python:

```bash
python tests/manual/verify_insights_expanded.py
```

Note: These scripts connect to the development database defined in `app.config`. They clean up their test data but be aware they write to the DB.
