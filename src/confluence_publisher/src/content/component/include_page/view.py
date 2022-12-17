from jinja2 import Template

from data.template.templates_storage import HtmlTemplatesStorage, HtmlComponentTemplateName


class IncludePageView:
    __template: Template

    def __init__(self, html_templates_storage: HtmlTemplatesStorage):
        self.__template = html_templates_storage.get_component(HtmlComponentTemplateName.include_page)

    async def render(self, include_page_name: str) -> str:
        render_params = {
            "include_page_name": include_page_name
        }
        return await self.__template.render_async(render_params)
