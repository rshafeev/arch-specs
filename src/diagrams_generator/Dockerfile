FROM python:3.8-slim-buster
WORKDIR .
COPY core/requirements.txt requirements-core.txt
RUN pip install -r requirements-core.txt
COPY diagrams_generator/requirements.txt .
RUN pip install -r requirements.txt
COPY ./diagrams_generator /app/diagrams_generator
COPY ./diagrams_generator/res/fonts /usr/share/fonts/truetype
COPY ./core /app/core
WORKDIR /app
ENV PYTHONPATH="$PYTHONPATH:/app"
RUN useradd arch_specs && \
    mkdir -p /arch_specs_autogen && \
    chown arch_specs:arch_specs /arch_specs_autogen
USER arch_specs
CMD python /app/diagrams_generator/app.py -c /app/diagrams_generator/config/base.yaml --specs_repo_path ${output_path} --meta_path ${meta_path}