ARG BASE=python:3.10-slim
ARG USERNAME=yaw
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG ENV_DIR=/venv
ARG CLI_DIR=/yaw


# build image: build and install the package
FROM jlvdb/yet_another_wizz:latest AS build
ARG ENV_DIR
ARG CLI_DIR
# setup the source directory
USER root
ENV PATH=${ENV_DIR}/bin:$PATH
WORKDIR ${CLI_DIR}
# copy required files for build
COPY . .
RUN pip install .


# release image: pull together all data
FROM ${BASE} as release
ARG USERNAME
ARG USER_UID
ARG USER_GID
ARG ENV_DIR
# install missing object and clean up
USER root
RUN set -eux; \
    apt-get update; \
    apt-get install libgomp1; \
    apt-get autoremove -y; \
    apt-get clean -y; \
    rm -rf /var/lib/apt/lists/*
# copy the virtual environment
COPY --from=build ${ENV_DIR} ${ENV_DIR}
ENV PATH=${ENV_DIR}/bin:$PATH
# create a non-root user and add a working directory
RUN set -eux; \
    groupadd --gid ${USER_GID} ${USERNAME}; \
    useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME}
# set matplotlib config
USER ${USER_UID}
ENV MPLCONFIGDIR=/config/matplotlib
WORKDIR ${MPLCONFIGDIR}
# go to working directory and launch yaw_cli
WORKDIR /data
ENTRYPOINT [ "yaw_cli" ]
CMD [ "-h" ]
