# Contributing

Go [here](https://github.com/corteva/djangorestframework-mvt/issues) to create a new issue or view issues.

## Types of Contributions

- Bug Fixes
    * Follow the [pull request requirements](#pull-request-requirements)
- Feature Implementations
    * Follow the [pull request requirements](#pull-request-requirements)
- Documentation
    * Sphinx compatibility required
- Bug Reports:
    * Report [here](https://github.com/corteva/djangorestframework-mvt/issues)
    * Operating system name and version required
    * Database name and version required
    * Python version required
    * Steps to reproduce if possible

## Pull Request Requirements

Pull requests should at least include:
* Tests
* Documentation
* Python 3 compatible

## Development Workflow

Please use a fork and feature branch workflow when submitting merge requests to the project on GitHub.

## Development Setup

* Install From Source:
  - `virtualenv venv -p python3`
  - `source venv/bin/activate`
  - `pip install -e .[dev]`
* Code Quality Checks:
  - `pytest test/`
  - `black --exclude venv .`
  - `pylint rest_framework_mvt/`
* View Documentation Locally:
  - `make html`
  - `open docs/index.html`

## Releases

Releases will be managed by the core developers.  Releases are NOT guaranteed to occur at regular intervals.  All 
releases will follow [semantic versioning](https://semver.org).  Releases will push the newest version of the project
to PyPi.

## Misc

djangorestframework-mvt does not guarantee Python 2 functionality.  The developers do not support Python 2.
