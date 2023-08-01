ARG python=python:3.10-slim
ARG config=/config

# create a container to build and install the package
FROM jlvdb/yet_another_wizz:latest AS build
USER root
ENV PATH=/venv/bin:$PATH
WORKDIR /yaw_cli
# copy required files for build
COPY . .
RUN pip install .

# final stage
FROM ${python} as release
# install missing object and clean up
USER root
RUN set -eux; \
    apt-get update; \
    apt-get install libgomp1; \
    apt-get autoremove -y; \
    apt-get clean -y; \
    rm -rf /var/lib/apt/lists/*
# copy the virtual environment
COPY --from=build /venv /venv
ENV PATH=/venv/bin:$PATH
# create a non-root user and add a working directory
RUN set -eux; \
    addgroup --system --gid 1001 yaw; \
    adduser --system --no-create-home --uid 1001 --gid 1001 yaw
# set matplotlib config
USER yaw
ENV MPLCONFIGDIR=${config}/matplotlib
WORKDIR ${MPLCONFIGDIR}
# go to working directory and launch yaw_cli
WORKDIR /data
ENTRYPOINT [ "yaw_cli" ]
CMD [ "-h" ]
