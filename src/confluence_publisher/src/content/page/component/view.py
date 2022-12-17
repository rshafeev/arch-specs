from datetime import datetime

from jinja2 import Template

from core.git.branch import Branch
from data.template.templates_storage import HtmlTemplatesStorage, HtmlPageTemplateName


class ComponentBranchDiagramView:
    diagram_name = "component_arch_diagram"

    __template: Template

    __html_templates_storage: HtmlTemplatesStorage

    def __init__(self, html_templates_storage: HtmlTemplatesStorage):
        self.__html_templates_storage = html_templates_storage
        self.__template = html_templates_storage.get_page(HtmlPageTemplateName.component_branch_diagram)

    async def render(self, branch: Branch) -> str:
        render_params = {
            "diagram_name": self.diagram_name,
            "current_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "branch_name": branch.name
        }
        html_s = await self.__template.render_async(render_params)
        return html_s
