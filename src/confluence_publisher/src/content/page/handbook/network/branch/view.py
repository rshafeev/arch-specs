from datetime import datetime

from content.component.expand.view import ExpandView
from content.component.include_page.view import IncludePageView
from core.git.branch import Branch
from core.specs.service.spec import ServiceType
from data.confluence.model.title import NetworkBranchDiagramPageTitle, NetworkBranchLinksPageTitle
from data.specs.service_spec_ext import ServiceSpecExt
from data.template.templates_storage import HtmlTemplatesStorage, HtmlPageTemplateName


class NetworkBranchView:
    __html_templates_storage: HtmlTemplatesStorage

    __include_page_view: IncludePageView

    __expand_view: ExpandView

    def __init__(self, html_templates_storage: HtmlTemplatesStorage):
        self.__html_templates_storage = html_templates_storage
        self.__include_page_view = IncludePageView(html_templates_storage)
        self.__expand_view = ExpandView(html_templates_storage)

    def __template(self, spec: ServiceSpecExt):
        if spec.type == str(ServiceType.kafka.value):
            template_name = HtmlPageTemplateName.network_branch_kafka
        else:
            template_name = HtmlPageTemplateName.network_branch
        return self.__html_templates_storage.get_page(template_name)

    async def render(self, spec: ServiceSpecExt, branch: Branch) -> str:
        render_params = {
            "include_page_network_diagram": await self.__include_page_view.render(
                NetworkBranchDiagramPageTitle.title(spec, branch)),
            "include_page_network_links": await self.__include_page_view.render(
                NetworkBranchLinksPageTitle.title(spec, branch)),
            "current_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        html_s = await self.__template(spec).render_async(render_params)
        return html_s
