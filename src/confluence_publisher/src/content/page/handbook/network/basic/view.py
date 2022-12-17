from datetime import datetime
from typing import List

from jinja2 import Template

from content.component.expand.view import ExpandView
from content.component.include_page.view import IncludePageView
from core.git.branch import Branch
from data.confluence.model.title import NetworkBranchPageTitle, NetworkCurrentPageTitle, NetworkCurrentDiagramPageTitle, \
    NetworkCurrentLinksPageTitle
from data.specs.service_spec_ext import ServiceSpecExt
from data.template.templates_storage import HtmlTemplatesStorage, HtmlPageTemplateName


class NetworkBasicPageView:
    __template: Template

    __html_templates_storage: HtmlTemplatesStorage

    __include_page_view: IncludePageView

    __expand_view: ExpandView

    def __init__(self, html_templates_storage: HtmlTemplatesStorage):
        self.__html_templates_storage = html_templates_storage
        self.__template = html_templates_storage.get_page(HtmlPageTemplateName.network_basic)
        self.__include_page_view = IncludePageView(html_templates_storage)
        self.__expand_view = ExpandView(html_templates_storage)

    async def render(self, spec: ServiceSpecExt, release_branches: List[Branch], has_master_branch: bool) -> str:
        render_params = {
            "include_page_network_diagram": await self.__include_page_view.render(
                NetworkCurrentDiagramPageTitle.title(spec)),
            "include_page_network_links": await self.__include_page_view.render(
                NetworkCurrentLinksPageTitle.title(spec)),
            "current_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        html_s = await self.__template.render_async(render_params)
        return html_s
