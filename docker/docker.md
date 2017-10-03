# Docker deployment and tests

## Create images

### Ubuntu 16.04
Build the image for Ubuntu 16.04. By default, the master branch of the odie project will be cloned.
```
docker build --force-rm=true -t odie-ubuntu1604 -f docker/ubuntu_16_04.dockerfile .
```

To build with TRAVIS env we need to send global variables
```
docker build \
--force-rm=true \
--build-arg TRAVIS_BRANCH=${TRAVIS_BRANCH} \
--build-arg TRAVIS_EVENT_TYPE=${TRAVIS_EVENT_TYPE} \
--build-arg TRAVIS_PULL_REQUEST_SLUG=${TRAVIS_PULL_REQUEST_SLUG} \
--build-arg TRAVIS_PULL_REQUEST_BRANCH=${TRAVIS_PULL_REQUEST_BRANCH} \
-t odie-ubuntu1604 \
-f docker/ubuntu_16_04.dockerfile .
```

### Debian stretch
Build the image for Debian 9. By default, the master branch of the odie project will be cloned.
```
docker build --force-rm=true -t odie-debian8 -f docker/debian8.dockerfile .
```

To build with TRAVIS env we need to send global variables
```
docker build \
--force-rm=true \
--build-arg TRAVIS_BRANCH=${TRAVIS_BRANCH} \
--build-arg TRAVIS_EVENT_TYPE=${TRAVIS_EVENT_TYPE} \
--build-arg TRAVIS_PULL_REQUEST_SLUG=${TRAVIS_PULL_REQUEST_SLUG} \
--build-arg TRAVIS_PULL_REQUEST_BRANCH=${TRAVIS_PULL_REQUEST_BRANCH} \
-t odie-debian9 \
-f docker/debian9.dockerfile .
```

## Run the test

Ubuntu image
```
docker run -it --rm odie-ubuntu1604
```

Debian image
```
docker run -it --rm odie-debian9
```
