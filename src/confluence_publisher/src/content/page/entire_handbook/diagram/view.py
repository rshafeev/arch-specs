from datetime import datetime

from jinja2 import Template

from data.specs.service_spec_ext import ServiceSpecExt
from data.template.templates_storage import HtmlTemplatesStorage, HtmlPageTemplateName


class EntireDiagramView:

    __template: Template

    __html_templates_storage: HtmlTemplatesStorage

    def __init__(self, html_templates_storage: HtmlTemplatesStorage):
        self.__html_templates_storage = html_templates_storage
        self.__template = html_templates_storage.get_page(HtmlPageTemplateName.entire_diagram)

    async def render(self, spec: ServiceSpecExt) -> str:
        render_params = {
            "service_name": spec.service_name,
            "current_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        html_s = await self.__template.render_async(render_params)
        return html_s
