import hashlib
import json
import os.path
from datetime import datetime

from core.git.branch import Branch
from core.git.specs_repo import GitSpecsRepositoryHelper
from core.specs.service.spec import ServiceType
from data.specs.service_spec_ext import ServiceSpecExt
from data.template.templates_storage import HtmlTemplatesStorage, HtmlPageTemplateName


class EntireLinksView:
    __html_templates_storage: HtmlTemplatesStorage

    def __init__(self, html_templates_storage: HtmlTemplatesStorage):
        self.__html_templates_storage = html_templates_storage

    def __template(self, spec: ServiceSpecExt):
        if spec.is_broker:
            template_name = HtmlPageTemplateName.entire_broker_links
        else:
            template_name = HtmlPageTemplateName.entire_links
        return self.__html_templates_storage.get_page(template_name)

    async def render(self, spec: ServiceSpecExt) -> str:
        network_json_name = GitSpecsRepositoryHelper.network_fname(spec.service_name)
        with open(network_json_name) as f:
            network_table = json.loads(f.read())
        topics_table = []
        if spec.is_kafka_broker:
            topics_json_name = GitSpecsRepositoryHelper.topics_fname(spec.service_name)
            with open(topics_json_name) as f:
                topics_table = json.loads(f.read())
        celery_tasks_table = []
        if spec.is_celery_broker:
            celery_tasks_json_name = GitSpecsRepositoryHelper.celery_tasks_fname(spec.service_name)
            with open(celery_tasks_json_name) as f:
                celery_tasks_table = json.loads(f.read())

        rx_celery_tasks_table = []
        rx_celery_tasks_json_name = GitSpecsRepositoryHelper.rx_celery_tasks_fname(spec.service_name)
        if os.path.isfile(rx_celery_tasks_json_name):
            with open(rx_celery_tasks_json_name) as f:
                rx_celery_tasks_table = json.loads(f.read())

        tx_celery_tasks_table = []
        tx_celery_tasks_json_name = GitSpecsRepositoryHelper.tx_celery_tasks_fname(spec.service_name)
        if os.path.isfile(tx_celery_tasks_json_name):
            with open(tx_celery_tasks_json_name) as f:
                tx_celery_tasks_table = json.loads(f.read())

        rx_topics_table = []
        rx_topics_json_name = GitSpecsRepositoryHelper.rx_topics_fname(spec.service_name)
        if os.path.isfile(rx_topics_json_name):
            with open(rx_topics_json_name) as f:
                rx_topics_table = json.loads(f.read())

        tx_topics_table = []
        tx_topics_json_name = GitSpecsRepositoryHelper.tx_topics_fname(spec.service_name)
        if os.path.isfile(tx_topics_json_name):
            with open(tx_topics_json_name) as f:
                tx_topics_table = json.loads(f.read())

        render_params = {
            "service_name": spec.service_name,
            "has_internal_storages": "internal_storage" in spec.raw and spec.raw["internal_storage"] is not None,
            "table_rows": network_table,
            "topics_rows": topics_table,
            "celery_tasks_rows": celery_tasks_table,
            "rx_celery_tasks_rows": rx_celery_tasks_table,
            "tx_celery_tasks_rows": tx_celery_tasks_table,
            "rx_topics_rows": rx_topics_table,
            "tx_topics_rows": tx_topics_table,
            "has_topics": len(topics_table) > 0,
            "has_celery_tasks": len(celery_tasks_table) > 0,
            "has_service_topics": len(rx_topics_table) + len(tx_topics_table)> 0,
            "has_service_rx_topics": len(rx_topics_table) > 0,
            "has_service_tx_topics": len(tx_topics_table) > 0,
            "has_service_celery_tasks": len(rx_celery_tasks_table) + len(tx_celery_tasks_table) > 0,
            "has_service_rx_celery_tasks": len(rx_celery_tasks_table) > 0,
            "has_service_tx_celery_tasks": len(tx_celery_tasks_table) > 0
        }
        render_params["current_hash"] = hashlib.md5(json.dumps(render_params, ensure_ascii=False).encode('utf8')).hexdigest()
        html_s = await self.__template(spec).render_async(render_params)
        return html_s
