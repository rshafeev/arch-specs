from datetime import datetime

from jinja2 import Template
from data.template.templates_storage import HtmlTemplatesStorage, HtmlPageTemplateName


class DiagramView:
    diagram_name = "arch_diagram"

    __template: Template

    __html_templates_storage: HtmlTemplatesStorage

    def __init__(self, html_templates_storage: HtmlTemplatesStorage):
        self.__html_templates_storage = html_templates_storage
        self.__template = html_templates_storage.get_page(HtmlPageTemplateName.diagram)

    async def render(self) -> str:
        render_params = {
            "diagram_name": f"{self.diagram_name}_diagram",
            "current_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        html_s = await self.__template.render_async(render_params)
        return html_s
