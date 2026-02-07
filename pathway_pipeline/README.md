# Member 1 – Pathway & ETA Pipeline

## Responsibilities
- GPS data ingestion from simulator
- Data cleaning and validation
- ETA computation logic
- Distance and speed calculations

## Timeline
- Days 1-2: Learn Pathway basics, finalize GPS schema
- Days 3-4: Ingest GPS stream, clean invalid data
- Days 5-6: Compute distance, speed, ETA
- Days 7-8: Stabilize pipeline, handle missing data
- Days 9-10: Support demo, fix issues

## Key Files
- `pipeline.py` - Main Pathway pipeline
- `eta_logic.py` - ETA calculation functions
- `schemas.py` - Data schemas
- `config.py` - Pipeline configuration

## Output
Pipeline should output processed data that backend can consume via API or shared data store.
