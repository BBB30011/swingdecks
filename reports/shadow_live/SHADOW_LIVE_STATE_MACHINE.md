# SHADOW LIVE STATE MACHINE

1. `WAITING_FOR_DATA`: Polling loop active, no new dates.
2. `PROCESSING`: New dates detected, pushing through the agent pipeline.
3. Errors fallback to fail-closed sleep logic.
