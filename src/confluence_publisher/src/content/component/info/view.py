from jinja2 import Template

from data.template.templates_storage import HtmlTemplatesStorage, HtmlComponentTemplateName


class InfoView:
    __template: Template

    def __init__(self, html_templates_storage: HtmlTemplatesStorage):
        self.__template = html_templates_storage.get_component(HtmlComponentTemplateName.info)

    async def render(self,
                     title: str,
                     body: str) -> str:
        render_params = {
            'title': title,
            'body': body
        }
        return await self.__template.render_async(render_params)
