clean:
	@find . -name *.pyc -delete
	@find . -name __pycache__ -delete

${VIRTUAL_ENV}/bin/pip-sync:
	pip install pip-tools

pip-tools: ${VIRTUAL_ENV}/bin/pip-sync

lock:
	pip-compile --generate-hashes --output-file requirements.txt requirements/base.in

lock-dev:
	pip-compile --generate-hashes --output-file requirements-dev.txt requirements/dev.in

install: pip-tools
	pip-sync requirements.txt

install-dev: pip-tools
	pip-sync requirements-dev.txt
