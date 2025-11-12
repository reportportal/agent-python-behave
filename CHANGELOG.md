# Changelog

## [Unreleased]
### Changed
- Client version updated to [5.6.7](https://github.com/reportportal/client-Python/releases/tag/5.6.7), by @HardNorth

## [5.0.1]
### Added
- OAuth 2.0 Password Grant authentication, by @HardNorth
### Changed
- Client version updated to [5.6.6](https://github.com/reportportal/client-Python/releases/tag/5.6.6), by @HardNorth
### Fixed
- Some configuration parameter names, which are different in the client, by @HardNorth
### Removed
- `token` param support, as it was deprecated pretty while ago, by @HardNorth

## [5.0.0]
### Added
- Support for `Python 3.13`, by @HardNorth
### Changed
- Client version updated to [5.6.5](https://github.com/reportportal/client-Python/releases/tag/5.6.5), by @HardNorth
- Behave version updated to [1.3.3](https://github.com/behave/behave/releases/tag/v1.3.3), by @HardNorth
### Removed
- `Python 3.7` support, by @HardNorth

## [4.0.3]
### Added
- Python 12 support, by @HardNorth

## [4.0.2]
### Changed
- Improve Scenario Outline parameters reporting, by @nicke46
- Client version updated on [5.5.4](https://github.com/reportportal/client-Python/releases/tag/5.5.4), by @HardNorth

## [4.0.1]
### Added
- Scenario Outline scenarios will add markdown table with active params to scenario description, by @nicke46

## [4.0.0]
### Added
- `rp_client_type` configuration variable, by @HardNorth
- `rp_connect_timeout` and `rp_read_timeout` configuration variables, by @HardNorth
### Changed
- Client version updated on [5.5.3](https://github.com/reportportal/client-Python/releases/tag/5.5.3), by @HardNorth
- Unified ReportPortal product spelling, by @HardNorth

## [3.0.0]
### Added
- `launch_uuid_print` and `launch_uuid_print_output` configuration parameters, by @HardNorth
### Changed
- Client version updated on [5.4.0](https://github.com/reportportal/client-Python/releases/tag/5.4.0), by @HardNorth
### Removed
- Python 3.6 support, by @HardNorth

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
- RPHandler support for all ReportPortal log levels, by @nicke46
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
