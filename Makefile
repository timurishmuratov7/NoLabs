# Load environment variables from .env file
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

flower:
	celery --broker=${CELERY_BROKER_URL} flower --port=5555
install-openapi-generator:
	npm install -g openapi-typescript-codegen
generate-client:
	@openapi --input 'http://127.0.0.1:8000/openapi.json' --output frontend/src/api/client --client axios
download-diffdock-weights: