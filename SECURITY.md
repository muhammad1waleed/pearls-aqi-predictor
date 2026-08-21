# Security Notes

## Known Dependency Vulnerabilities

### protobuf 4.25.9 (PYSEC-2026-1805)

This project pins `protobuf<5.0.0` because `hopsworks==5.0.5` requires it
(see commit history around the Aug 2026 CI outage for details). A known
vulnerability exists in this version range.

**Risk assessment:** Low, for this project's usage. protobuf is used
internally by the Hopsworks SDK for gRPC communication with Hopsworks'
own infrastructure. This project never parses or constructs untrusted
protobuf messages directly, and does not expose any protobuf-handling
code to external/user input.

**Resolution plan:** Upgrade protobuf once `hopsworks` releases a version
compatible with protobuf 5.x or later. Tracked as a known limitation,
not an active fix, as of this writing.

## Secrets Management

- All API keys (OpenWeather, Hopsworks) are stored via `.env` locally
  (excluded via `.gitignore`) and GitHub Actions Secrets in CI.
- Full Git history has been audited to confirm no secret values were
  ever committed (see project development log).