# Changelog

## [Unreleased]
### Changed
- `step_based` config parameter deprecated in favor of `log_layout` parameter, by @nicke46
- The Agent now uses `RPClient` class instead of `ReportPortalService`, by @HardNorth
### Added
- RPHandler support for all Report Portal log levels, by @nicke46
- Logged exceptions now include traceback, by @nicke46
- Skipped steps after failures will be logged for `STEP` and `NESTED` log_layout, by @nicke46
### Removed
- `logger.py` module in favor to `reportportal_client.logs`, by @HardNorth

## [1.0.2]
### Added
- `debug_mode` config parameter support, by @nicke46

## [1.0.1]
### Fixed
- Issue [#21](https://github.com/reportportal/agent-python-behave/issues/21): HOOK-ERROR in after_step, by @netolyrg

## [1.0.0]
### Changed
- Initial release, by @amartiushkov-ms
