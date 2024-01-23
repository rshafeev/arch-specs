from datetime import datetime
from typing import Optional
from jinja2 import Template
from data.specs.service_spec_ext import ServiceSpecExt
from data.template.templates_storage import HtmlTemplatesStorage, HtmlComponentTemplateName
import markdown2


class ServicePropertiesView:
    __template: Template

    def __init__(self, html_templates_storage: HtmlTemplatesStorage):
        self.__template = html_templates_storage.get_component(HtmlComponentTemplateName.service_properties)

    # @staticmethod
    # def account_link(user_key, owner_name):
    #     return "<ac:link><ri:user ri:account-id=\"{}\"/></ac:link>".format(user_key)
    # todo: for_cloud!

    @staticmethod
    def account_link(user_key, user_name):
        return "<ac:link><ri:user ri:userkey=\"{}\"/></ac:link>".format(user_key)

    @staticmethod
    def account_name(user_key, user_name):
        return f"<strong>{user_name}</strong>"

    @staticmethod
    def source_code_link(spec: ServiceSpecExt):
        if "src" not in spec.raw or spec.raw['src'] == '':
            return ""
        return '<p><a href="{}">gitlab: {}</a></p>'.format(spec.raw['src'], spec.service_name)

    @staticmethod
    async def form_service_responsible_content(spec: ServiceSpecExt):
        owner_keys = await spec.owner_keys()
        content = ''
        for owner_name in owner_keys:
            if len(content) > 0:
                content = content + ', '
            content = content + ServicePropertiesView.account_name(spec.raw['owner_keys'][owner_name], owner_name)
        return content

    @staticmethod
    async def form_service_responsible_link_content(spec: ServiceSpecExt):
        owner_keys = await spec.owner_keys()
        content = ''
        for owner_name in owner_keys:
            content = content + ServicePropertiesView.account_link(spec.raw['owner_keys'][owner_name], owner_name)
        return content

    @staticmethod
    def __status_colour(spec: ServiceSpecExt) -> str:
        status = spec.raw['status']
        if status == "ready":
            return "Green"
        if status == "develop":
            return "Yellow"
        return "Grey"

    @staticmethod
    def __dev_teams_s(spec: ServiceSpecExt) -> str:
        if spec.dev_teams is None:
            return ""
        teams_s = ""
        for team in spec.dev_teams:
            if 'link' in team:
                team_s = f"<p><a href=\"{team['link']}\">{team['name']}</a></p>"
                teams_s = teams_s + team_s
            else:
                teams_s = teams_s + " " + team['name']
        return teams_s

    def _set_apidocs(self, render_params: dict, spec: ServiceSpecExt):
        apidocs_s = ""
        for interface in spec.apidocs:
            apidocs = spec.apidocs[interface]
            if (apidocs is None or 'apidocs' not in apidocs or
                    apidocs['apidocs'] is None):
                if len(apidocs_s) > 0:
                    apidocs_s = apidocs_s + " "
                continue
            apidoc_list = apidocs['apidocs']
            for apidoc in apidoc_list:
                if 'swagger' in apidoc:
                    swagger_html = f"<p><a href=\"{apidoc['swagger']}\">Swagger API Docs.</a></p>"
                    if len(apidocs_s) > 0:
                        apidocs_s = apidocs_s + " "
                    apidocs_s = apidocs_s + f"{swagger_html}"
                if interface == "grpc":
                    grpc_interface_html = f"<p><a href=\"{apidoc['protocol']}\">grpc:{apidoc['service']}</a></p>"
                    if len(apidocs_s) > 0:
                        apidocs_s = apidocs_s + " "
                    apidocs_s = apidocs_s + f"{grpc_interface_html}"

        render_params["apidocs"] = apidocs_s
        render_params["has_apidocs"] = len(apidocs_s) > 0


    def markdown2html(self, md_template_text: str) -> str:
        j2_template = Template(md_template_text)
        md_text = j2_template.render()
        return markdown2.markdown(md_text)

    async def render(self, spec: ServiceSpecExt) -> str:
        settings = spec.settings
        render_params = {
            "service_name": spec.service_name,
            "desc": spec.raw['desc'] if 'desc' in spec.raw and spec.raw['desc'] is not None else "",
            "source_link": self.source_code_link(spec),
            "status": spec.raw['status'],
            "language": spec.raw['language'] if 'language' in spec.raw else "",
            "has_language": 'language' in spec.raw,
            "status_colour": self.__status_colour(spec),
            "responsible_link": await self.form_service_responsible_link_content(spec),
            "responsible": await self.form_service_responsible_content(spec),
            "service_module": settings.confluence.module_title(spec.raw['module']),
            "service_type": spec.type,
            "service_module_colour": "Blue" if spec.service_module == "botapp" else "Grey",
            "state": spec.raw['state'] if 'state' in spec.raw else "",
            "current_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "dev_teams": self.__dev_teams_s(spec),
            "no_encryption": len(spec.support_encryption) == 0,
            "has_encryption": 'encryption' in spec.raw,
            "encryption": spec.support_encryption,
            "has_image": 'image' in spec.raw,
            "image": spec.raw['image'] if 'image' in spec.raw else ""
        }
        self._set_apidocs(render_params, spec)
        return await self.__template.render_async(render_params)
