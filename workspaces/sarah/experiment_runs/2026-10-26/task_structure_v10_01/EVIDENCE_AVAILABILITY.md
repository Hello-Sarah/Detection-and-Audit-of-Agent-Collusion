# Evidence availability

The full local run bundle includes the raw trajectory, request and locked-file snapshots, terminal record, and SQLite journals. These artifacts are retained in this run directory and their hashes are recorded in `evidence_hashes.json`.

The public GitHub record contains the execution summaries, labels file, transport metadata, and this report, but not the raw SQLite journal or row-level file snapshots. The GitHub automatic review rejected uploading the raw SQLite journal because it could contain sensitive trajectory or data records. No claim of missing or altered local evidence is intended; this is a publication boundary for the synthetic run artifacts.
