#!make

IMAGE_NAME := acasado/aprslog
FULL_VERSION := 0.2.0
MINOR_VERSION := 0.2
MAJOR_VERSION := 0

dev:
	docker build --no-cache=false -t ${IMAGE_NAME} .

build :
	docker build --no-cache=false -t ${IMAGE_NAME}:$(FULL_VERSION)  .
	docker tag ${IMAGE_NAME}:$(FULL_VERSION) ${IMAGE_NAME}:$(MINOR_VERSION)
	docker tag ${IMAGE_NAME}:$(FULL_VERSION) ${IMAGE_NAME}:$(MAJOR_VERSION)
	docker tag ${IMAGE_NAME}:$(FULL_VERSION) ${IMAGE_NAME}
	bash ~/src/sh/docker.login
	docker push acasado/aprslog
clean:
	docker rmi ${IMAGE_NAME} 
	docker images
cleanbu:
	docker rmi ${IMAGE_NAME}:$(FULL_VERSION)  
	docker rmi ${IMAGE_NAME}:$(MINOR_VERSION)
	docker rmi ${IMAGE_NAME}:$(MAJOR_VERSION)
	docker rmi ${IMAGE_NAME} 
	docker images
