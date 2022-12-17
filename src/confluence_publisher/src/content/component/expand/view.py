from jinja2 import Template

from data.template.templates_storage import HtmlTemplatesStorage, HtmlComponentTemplateName


class ExpandView:
    __template: Template

    def __init__(self, html_templates_storage: HtmlTemplatesStorage):
        self.__template = html_templates_storage.get_component(HtmlComponentTemplateName.expand)

    async def render(self,
                     title: str,
                     body: str,
                     expanded: bool) -> str:
        render_params = {
            'title': title,
            'body': body,
            'expanded': "true" if expanded else "false"
        }
        return await self.__template.render_async(render_params)
