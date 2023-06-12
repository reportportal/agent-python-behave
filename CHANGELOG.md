# Changelog

## [Unreleased]

## [2.0.4]
### Changed
- Client version updated on [5.3.5](https://github.com/reportportal/client-Python/releases/tag/5.3.5), by @HardNorth
- `token` configuration parameter was renamed to `api_key` to maintain common convention, by @HardNorth

## [2.0.3]
### Added
- Stub files for `config` and `behave_agent` modules, by @HardNorth
- `log_batch_size` and `log_batch_payload_size` config parameters, by @HardNorth
### Changed
- Build script updates, by @HardNorth
### Fixed
- Launch attributes parsing, by @HardNorth

## [2.0.2]
### Changed
- Client version updated on [5.3.0](https://github.com/reportportal/client-Python/releases/tag/5.3.0), by @HardNorth
- move debug mode to RPClient init, by @nicke46
- Make agent not finish the launch if a launch_id was supplied at start, by @nicke46

## [2.0.1]
### Fixed
- Invalid rerun parameter on Launch start, by @HardNorth
- Logging part at README.rst, by @HardNorth

## [2.0.0]
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
