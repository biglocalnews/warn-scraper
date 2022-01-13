#
# Python helpers
#

PIPENV := pipenv run
PYTHON := $(PIPENV) python -W ignore

define python
    @echo "🐍🤖 $(OBJ_COLOR)Executing Python script $(1)$(NO_COLOR)\r";
    @$(PYTHON) $(1)
endef

#
# Tests
#


test: ## run all tests
	@$(PYTHON) setup.py test


format: ## automatically format Python code with black
	@$(PIPENV) black .


#
# Releases
#

check-release: ## check release for potential errors
	@$(PIPENV) twine check dist/*


test-release: clean dist ## release distros to test.pypi.org
	@$(PIPENV) twine upload -r testpypi dist/*


release: clean dist ## package and upload a release
	@$(PIPENV) twine upload -r pypi dist/*


dist: clean ## builds source and wheel package
	@$(PYTHON) setup.py sdist
	@$(PYTHON) setup.py bdist_wheel
	@ls -l dist


#
# Extras
#

help: ## Show this help. Example: make help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


# Mark all the commands that don't have a target
.PHONY: help \
        check-release \
        dist \
        format \
        release \
        test \
        test-release
