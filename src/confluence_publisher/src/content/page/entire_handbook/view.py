from content.component.include_page.view import IncludePageView
from content.component.service_properties.view import ServicePropertiesView
from content.page.entire_handbook.diagram.view import EntireDiagramView
from content.page.entire_handbook.links.view import EntireLinksView
from content.page.handbook.html_parser import ServiceHandbookPageParser
from core.specs.service.spec import ServiceType
from data.confluence.model.title import NetworkCurrentDiagramPageTitle, \
    NetworkCurrentLinksPageTitle, ServiceHandbookManualPageTitle
from data.specs.service_spec_ext import ServiceSpecExt
from data.template.templates_storage import HtmlTemplatesStorage, HtmlPageTemplateName


class EntireHandbookPageView:
    __html_templates_storage: HtmlTemplatesStorage

    __props_view: ServicePropertiesView

    __include_page_view: IncludePageView

    __diagram_view: EntireDiagramView

    __links_view: EntireLinksView


    def __init__(self, html_templates_storage: HtmlTemplatesStorage):
        self.__html_templates_storage = html_templates_storage
        self.__props_view = ServicePropertiesView(html_templates_storage)
        self.__include_page_view = IncludePageView(html_templates_storage)
        self.__diagram_view = EntireDiagramView(html_templates_storage)
        self.__links_view = EntireLinksView(html_templates_storage)

    async def __update_service_handbook_page(self, spec: ServiceSpecExt, page_body_s: str) -> str:
        service_properties_html_s = await self.__props_view.render(spec)
        current_content = ServiceHandbookPageParser(page_body_s)
        current_content.update_service_properties_section(service_properties_html_s)
        return current_content.html_s

    def __template(self, spec: ServiceSpecExt):
        if spec.is_broker:
            template_name = HtmlPageTemplateName.entire_service_kafka
        else:
            template_name = HtmlPageTemplateName.entire_service
        return self.__html_templates_storage.get_page(template_name)

    async def render(self, spec: ServiceSpecExt, page_body_s=None) -> str:
        if page_body_s is not None:
            return await self.__update_service_handbook_page(spec, page_body_s)
        render_params = {
            "service_properties": await self.__props_view.render(spec),
            "include_page_network_diagram": await self.__diagram_view.render(spec),
            "include_page_network_links": await self.__links_view.render(spec),
            "include_page_handbook_manual": await self.__include_page_view.render(
                ServiceHandbookManualPageTitle.title(spec))

        }
        html_s = await self.__template(spec).render_async(render_params)
        return html_s
