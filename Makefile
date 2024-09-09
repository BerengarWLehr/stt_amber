.DEFAULT_GOAL := help
KUBECTL = "kubectl"
NAME = "nextcloud2amberscript"
SERVER_NAME = "git.uni-jena.de:5050/rz/mmz/${NAME}"
VERSION = "0.1.0"
NAMESPACE = "default"

.PHONY: help
help:
	@echo "Welcome to Transcription. Please use \`make <target>\` where <target> is one of"
	@echo " "
	@echo "  Next commands are only for dev environment with nextcloud-docker-dev!"
	@echo "  They should run from the host you are developing on(with activated venv) and not in the container with Nextcloud!"
	@echo "  "
	@echo "  build-push        build image and upload to git.uni-jena.de"
	@echo "  "
	@echo "  deploy            deploy Transcription to registered 'docker_dev' for Nextcloud Last"
	@echo "  "
	@echo "  run               install Transcription for Nextcloud Last"
	@echo "  "
	@echo "  For development of this example use PyCharm run configurations. Development is always set for last Nextcloud."
	@echo "  First run 'Transcription' and then 'make registerXX', after that you can use/debug/develop it and easy test."
	@echo "  "
	@echo "  register          perform registration of running Transcription into the 'manual_install' deploy daemon."

.PHONY: build
build:
	buildah login ${SERVER_NAME}
	buildah build --tag "${SERVER_NAME}:${VERSION}" .
	buildah tag  "${SERVER_NAME}:${VERSION}" "${SERVER_NAME}:latest"
	buildah push "${SERVER_NAME}:latest"
	buildah push "${SERVER_NAME}:${VERSION}"

.PHONY: restart
restart:
	${KUBECTL} -n ${NAMESPACE} rollout restart deploy ${NAME}

.PHONY: start
start:
	${KUBECTL} -n ${NAMESPACE} delete deployment/${NAME} || echo "No deployments"
	${KUBECTL} -n ${NAMESPACE} apply -f K8s/deploy.yaml
	${KUBECTL} -n ${NAMESPACE} apply -f K8s/service.yaml
	${KUBECTL} -n ${NAMESPACE} apply -f K8s/ingress.yaml

.PHONY: log
log:
	${KUBECTL} -n ${NAMESPACE} logs -f deployment/${NAME}
