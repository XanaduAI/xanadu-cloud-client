## Release 0.2.0 (development release)

### Improvements

* Following an update to the Xanadu Cloud 0.4.0 API, names are no longer required to submit jobs.
  [(#16)](https://github.com/XanaduAI/xanadu-cloud-client/pull/16)

## Release 0.1.1 (current release)

### New features since last release

* The Job class now has a `metadata` property which, by convention, returns
  information about job failures.
  [(#15)](https://github.com/XanaduAI/xanadu-cloud-client/pull/15)

### Improvements

* The CI workflows are now triggered when a branch is merged into `main`.
  [(#15)](https://github.com/XanaduAI/xanadu-cloud-client/pull/15)

### Bug Fixes

* On Windows, the XCC configuration file is now stored at `...\Xanadu\xanadu-cloud\.env`.
  [(#15)](https://github.com/XanaduAI/xanadu-cloud-client/pull/15)

### Documentation

* Individual modules are now listed in the *API* section of the Sphinx sidebar.
  [(#15)](https://github.com/XanaduAI/xanadu-cloud-client/pull/15)

* The `Settings` class docstring now includes an example walkthrough as well as
  the location of the XCC configuration file.
  [(#15)](https://github.com/XanaduAI/xanadu-cloud-client/pull/15)

### Contributors

This release contains contributions from (in alphabetical order):

[Mikhail Andrenkov](https://github.com/Mandrenkov).

## Release 0.1.0

### New features since last release

* This is the initial public release.

### Contributors

This release contains contributions from (in alphabetical order):

[Mikhail Andrenkov](https://github.com/Mandrenkov).