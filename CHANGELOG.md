# Changelog

All notable changes to TealFlowMCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-02-27

### Added
- Branching workflow documentation (CONTRIBUTING.md)
- Changelog file
- Comprehensive unit tests for R Date/POSIXct type inference with Series.attrs
- Comprehensive documentation for `teal.transform` helper functions (`variable_choices()`, `value_choices()`, `choices_selected()`) in agent guidance

### Changed
- Replaced `pyreadr` (AGPL-3.0) with `rdata` (MIT) for reading RDS files
- Updated Python version requirement from >=3.10 to >=3.11 (required by rdata)
- Updated CI workflow to test on Python 3.11, 3.12, 3.13 (dropped 3.10)
- R Date/POSIXct constructors now store original R class in Series.attrs for accurate type inference
- `_infer_datetime_type` now checks Series.attrs first before falling back to heuristics

### Fixed
- Fixed RuntimeWarning in pandas when converting R Date/POSIXct values with NaN
- Fixed misclassification of POSIXct columns with all midnight timestamps as Date columns

## [0.1.4] - 2026-02-17

### Changed
- Changed license from MIT to AGPL-3.0 ([#54](https://github.com/Appsilon/TealFlowMCP/pull/54))

### Fixed
- Synced version numbers across `pyproject.toml` and `tealflow_mcp/__init__.py` ([#55](https://github.com/Appsilon/TealFlowMCP/pull/55))

## [0.1.3.post2] - 2026-02-13

### Fixed
- Fixed README links ([#53](https://github.com/Appsilon/TealFlowMCP/pull/53))

## [0.1.3.post1] - 2026-02-13

### Added
- First public release to PyPI

[Unreleased]: https://github.com/Appsilon/TealFlowMCP/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/Appsilon/TealFlowMCP/compare/v0.1.4...v0.2.0
[0.1.4]: https://github.com/Appsilon/TealFlowMCP/compare/v0.1.3.post2...v0.1.4
[0.1.3.post2]: https://github.com/Appsilon/TealFlowMCP/compare/v0.1.3.post1...v0.1.3.post2
[0.1.3.post1]: https://github.com/Appsilon/TealFlowMCP/releases/tag/v0.1.3.post1
