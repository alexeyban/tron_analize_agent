## Step 1 – Ingestion Agent
- Responsibilities  
  This agent is responsible for extracting forward USDT transfers from the Tron blockchain via TronScan API. It must implement a depth-limited breadth-first traversal of transactions starting from a seed wallet or transaction ID, collecting all forward USDT transfer events up to the defined depth limit. The agent should clean and normalize incoming data for compatibility with downstream processes, and prepare them for storage in Delta Lake on Databricks. It must ensure no data duplication and handle API rate limiting and error retries gracefully. All data transformations and preparation logic must be optimized for pushdown execution on Databricks.

- Inputs  
  - Seed wallet addresses or transaction hashes for traversal start  
  - Depth limit integer defining how far the traversal should go  
  - TronScan API credentials and endpoint configurations  
  - Configuration file describing USDT token contract address on Tron and relevant transfer event signatures

- Outputs  
  - Cleaned, normalized transaction dataset containing forward USDT transfers up to the specified depth  
  - Metadata about traversal completeness and depth reached  
  - JSON or Parquet stage files ready for ingestion into Delta Lake (expected output format: parquet or delta-compatible format)

- Acceptance Criteria  
  - Retrieved transactions include only forward USDT transfers and respect the defined traversal depth limit  
  - Data contains no duplicates and is properly normalized (e.g., consistent timestamp format, wallet address casing)  
  - Handles API errors with retries without halting the pipeline  
  - Output files or datasets conform to schema defined by downstream agents  
  - The ingestion logic is encapsulated as reusable Databricks notebooks or Python modules designed for execution on Databricks clusters  
  - Demonstrated ingestion of a sample seed input producing a dataset matching schema with expected size and traversal depth metadata

- Repository Path  
  `/src/ingestion/tronscan_forward_usdt/`  
  Contains:  
  - `ingest_forward_usdt.py` (main extraction and transformation code)  
  - `configs/` for API and token configurations  
  - Databricks notebook `.ipynb` for orchestrated runs and testing


## Step 2 – Reverse Flow Agent
- Responsibilities  
  This agent conducts reverse flow analysis to trace the origin of USDT funds by following the transactional chain backward on the Tron blockchain starting from suspicious or target transactions/wallets identified in Step 1. It must dereference each transaction source backward until either a stopping condition (e.g., external wallet, origin depth reached, or an address from a whitelist) or no further source transaction is found. This agent must prepare its outputs to integrate seamlessly with Delta Lake storage and support wallet aggregation.

- Inputs  
  - USDT forward transfer dataset from Step 1 (stored in Delta Lake)  
  - Configurations defining maximum reverse traversal depth, stop criteria (e.g., whitelist, external chains)  
  - List of wallets or transactions of interest within the forward dataset for reverse tracing  
  - Access credentials for querying TronScan or other chain explorers if needed (read-only)

- Outputs  
  - Dataset of backward (source) transaction chains forming reverse flow paths, including wallet links and timestamps  
  - Summary statistics on reverse traversal depth and coverage per starting wallet/transaction  
  - Reports of unreachable or external origin points

- Acceptance Criteria  
  - Reverse flow traversal respects depth and stop conditions strictly  
  - Output dataset schema validated and compatible with Delta Lake and ingestion for analytics  
  - No incomplete or partial reverse chains included unconditionally; incomplete chains must be flagged explicitly  
  - Computation performed exclusively on Databricks to ensure scalability  
  - Validation on sample datasets showing full round trip coverage of funds from source to forward transfer destination wallets

- Repository Path  
  `/src/reverse_flow/`  
  Contains:  
  - `reverse_trace.py` (core reverse traversal logic implemented as Spark jobs or Databricks notebooks)  
  - Helper modules for address whitelisting and stopping conditions  
  - Sample configuration files defining reverse flow parameters


## Step 3 – Delta Lake Storage Agent
- Responsibilities  
  This agent is responsible for designing, implementing, and managing Delta Lake storage schema to store forward USDT transfers, reverse flow chains, and aggregated wallet data. It ensures data is safely ingested from upstream agents, optimized for query and downstream analysis, implements partitioning strategies, and manages schema evolution. It must also implement data quality checks during ingestion such as schema validation, duplicates, completeness, and transactional consistency guarantees.

- Inputs  
  - Normalized forward transfer data (output of Step 1)  
  - Reverse flow analysis data (output of Step 2)  
  - Wallet aggregation results (from Step 4, incremental ingestion)  
  - Data quality metrics configurations and schema definitions for all tables involved

- Outputs  
  - Delta Lake tables and views accessible on Databricks containing:  
    - `forward_usdt_transfers`  
    - `reverse_flow_chains`  
    - `wallet_aggregation`  
  - Data quality reports after each ingestion or update operation  
  - Documentation of storage schema and partitioning strategies

- Acceptance Criteria  
  - Delta tables follow agreed schema definitions and partition strategies for performance  
  - All writes are atomic and idempotent to allow safe re-execution  
  - Data quality checks pass consistently and are automated in the ingestion pipeline  
  - Documentation is complete and stored in repository for maintainability  
  - Tables are optimized for query performance on Databricks (e.g., Z-order, compaction)

- Repository Path  
  `/src/delta_lake_storage/`  
  Contains:  
  - `delta_ingest.py` and/or Databricks notebooks for ingestion pipelines  
  - Schema definition files (JSON/Avro/Delta schema)  
  - Data quality checks scripts and configurations  
  - Documentation Markdown files describing table design


## Step 4 – Wallet Aggregation and Suspicious Pattern Detection Agent
- Responsibilities  
  This agent aggregates wallet transaction activity combining forward and reverse flows, building enriched wallet profiles including transaction volume, counterparties, temporal activity patterns, and consolidated holdings. It implements a configurable rule-based and heuristic suspicious pattern detection module that identifies money laundering indicators, rapid fund cycling, unusual concentration of transactions, or known blacklisted wallet interactions. The agent outputs flagged wallet lists and pattern reports ready for analyst review or automated alerting.

- Inputs  
  - Forward transaction Delta Lake table from Step 3  
  - Reverse flow chains Delta Lake table from Step 3  
  - Configuration files defining suspicious patterns, heuristics thresholds, and blacklist sources  
  - Wallet metadata if available (optional)

- Outputs  
  - Aggregated wallet analytics dataset with enriched attributes  
  - Suspicious wallet flags with supporting evidence and pattern classification  
  - Summary reports and alerts in standardized formats (e.g., JSON, CSV)  
  - Dashboards or notebooks demonstrating pattern detection results and statistics (optional)

- Acceptance Criteria  
  - Aggregation logic is fully implemented with comprehensive attributes reflecting transactional behavior  
  - Suspicious pattern detection rules are configurable, documented, and tested on synthetic/sample data  
  - Output flagged data matches expected schema and includes confidence or rule metadata  
  - No heavy compute runs outside Databricks environment  
  - Results reproducible and verifiable via automated test cases and sample runs  
  - Clear documentation of detection methods, limitations, and configuration parameters

- Repository Path  
  `/src/wallet_aggregation_detection/`  
  Contains:  
  - `aggregation.py` for wallet activity summarization  
  - `pattern_detection.py` for suspicious pattern heuristics  
  - Configuration files for rules and blacklists  
  - Testing data and notebooks for demonstration and validation