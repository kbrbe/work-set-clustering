# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2024-06-28

### Added

- Documentation about integration tests in `test/README.md` and `test/resources/README.md`

### Changed

- When updating clusters, descriptive keys of the initial clusters are now an optional parameter. This allows the reuse of existing clusters, even when they contain overlapping elements ([9](https://github.com/kbrbe/work-set-clustering/issues/9))
- Integration tests are restructured: instead of a single TestClustering class with test functions, we have now different "sets" of test functions (test functions grouped in a class). Actual test cases can inherit the test function classes that are appropriate for the given context

## [0.3.0] - 2024-02-21

Breaking changes for use as a programming library, because the parameter for the input file expects now a list.

### Added

- Functionality to add multiple descriptive key input files ([7](https://github.com/kbrbe/work-set-clustering/issues/7))

### Changed

- Instead of a single integration test class `TestClustering`, that class now only contains the test functions and they are called for different implementations in subclasses of `TestClustering`.

## [0.2.1] - 2023-12-15

### Fixed

- Switched logic: When using the commandline with existing clusters as input, clustering from scratch was involved and vice versa

## [0.2.0] - 2023-11-23

### Added

- Functionality to reuse previously computed cluster assignments ([1](https://github.com/kbrbe/work-set-clustering/issues/1))
- More unit tests as well as integration tests for the whole script ([2](https://github.com/kbrbe/work-set-clustering/issues/2))

### Changed

- Updated the documentation to provide an example of the input data ([3](https://github.com/kbrbe/work-set-clustering/issues/3))

## [0.1.0] - 2023-10-16

### Added

- Initial version of the script copied from the tool.csv folder of https://github.com/kbrbe/beltrans-data-integration/

[0.1.0]: https://github.com/kbrbe/work-set-clustering/releases/tag/v0.1.0
[0.2.0]: https://github.com/kbrbe/work-set-clustering/compare/v0.1.0...v0.2.0
[0.2.1]: https://github.com/kbrbe/work-set-clustering/compare/v0.2.0...v0.2.1
[0.3.0]: https://github.com/kbrbe/work-set-clustering/compare/v0.2.1...v0.3.0
