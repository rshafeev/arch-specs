import urllib.parse
from datetime import datetime
from jinja2 import Template

from content.component.include_page.view import IncludePageView
from content.component.info.view import InfoView
from core.git.branch import Branch
from data.confluence.model.title import NetworkBranchLinksPageTitle, \
    NetworkBasicPageTitle
from data.specs.service_spec_ext import ServiceSpecExt
from data.template.templates_storage import HtmlTemplatesStorage, HtmlPageTemplateName


class NetworkCurrentLinksView:
    __template: Template

    __html_templates_storage: HtmlTemplatesStorage

    __include_page_view: IncludePageView

    __info_view: InfoView

    def __init__(self, html_templates_storage: HtmlTemplatesStorage):
        self.__html_templates_storage = html_templates_storage
        self.__template = html_templates_storage.get_page(HtmlPageTemplateName.network_current_links)
        self.__include_page_view = IncludePageView(html_templates_storage)
        self.__info_view = InfoView(html_templates_storage)

    async def render(self, spec: ServiceSpecExt, selected_branch: Branch) -> str:
        link = "{}/{}/{}".format(
            spec.settings.confluence.link,
            spec.settings.confluence.space,
            urllib.parse.quote_plus(NetworkBasicPageTitle.title(spec)))
        render_params = {
            "branch_version_info": await self.__info_view.render("Version", selected_branch.name.upper()),
            "all_versions_link": link,
            "include_page_network_links": await self.__include_page_view.render(
                NetworkBranchLinksPageTitle.title(spec, selected_branch)),
            "current_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        html_s = await self.__template.render_async(render_params)
        return html_s
