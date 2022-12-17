FROM python:3.8-slim-buster
WORKDIR .
COPY core/requirements.txt requirements-core.txt
RUN pip install -r requirements-core.txt
COPY specs_generator/requirements.txt .
RUN pip install -r requirements.txt
COPY ./specs_generator /app/specs_generator
COPY ./core /app/core
WORKDIR /app
ENV PYTHONPATH="$PYTHONPATH:/app"
RUN useradd arch_specs && \
    mkdir -p /arch_specs_autogen && \
    chown arch_specs:arch_specs /arch_specs_autogen
USER arch_specs
CMD python /app/specs_generator/app.py -c /app/specs_generator/config/base.yaml --specs_repo_path ${output_path} --meta_path ${meta_path} --validate