FROM python:3.8-slim-buster
WORKDIR .
COPY core/requirements.txt requirements-core.txt
RUN pip install -r requirements-core.txt
COPY confluence_publisher/requirements.txt .
RUN pip install -r requirements.txt
COPY ./confluence_publisher /app/confluence_publisher
COPY ./core /app/confluence_publisher/src/core
WORKDIR /app
ENV PYTHONPATH="$PYTHONPATH:/app/confluence_publisher/src"
RUN useradd arch_specs && \
    mkdir -p /arch_specs_autogen && \
    chown arch_specs:arch_specs /arch_specs_autogen
USER arch_specs
CMD python /app/confluence_publisher/src/app.py -c /app/confluence_publisher/config/base.yaml --specs_repo_path ${output_path} --meta_path ${meta_path} --cache_path ${cache_path} ${validate_only_flag}
