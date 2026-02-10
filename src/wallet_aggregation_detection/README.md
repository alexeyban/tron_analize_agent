# Wallet Aggregation & Suspicious Pattern Detection

## Purpose
Aggregate wallet-level behavior and detect explainable suspicious patterns
in USDT TRC20 flows on Tron.

## Implemented Patterns
- High total outflow volume
- Many distinct receivers (fan-out)
- Rapid activity in short time window
- High fan-out ratio

## Output
Delta table: wallet_aggregation

Columns include:
- wallet
- total_out_amount
- out_tx_count
- unique_receivers
- funding_events
- flags per rule
- is_suspicious (boolean)

## Notes
- Fully explainable rules
- No ML
- Ready for compliance / investigations
