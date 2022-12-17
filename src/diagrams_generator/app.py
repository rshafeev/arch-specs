import argparse
import asyncio
import logging
import os

import cssutils

from core.app import AppCore
from core.git.branch import Branch
from core.git.specs_repo import GitSpecsRepositoryHelper
from core.specs.specs import ServicesSpecs
from core.task.task_pool import TasksPool
from diagrams_generator.diagrams.styles_wrapper import StylesWrapper, StyleSelector
from diagrams_generator.diagrams.template import XmlTemplate
from diagrams_generator.generator.generator import Generator
from diagrams_generator.generator.service.service_network_generator import ServiceNetworkGenerator
from diagrams_generator.generator.service.service_style_selector import ServiceStyleSelector


class App(AppCore):

    @staticmethod
    def prepare_args_parser():
        m_desc = "diagrams generator"
        path = os.path.dirname(__file__)
        args_parser = argparse.ArgumentParser(
            fromfile_prefix_chars='@', description=m_desc, formatter_class=argparse.RawTextHelpFormatter)
        args_parser.add_argument(
            "-m", "--meta_path", dest="meta_path", help="meta_path",
            required=True)
        args_parser.add_argument(
            "-specs_repo_path", "--specs_repo_path", dest="specs_repo_path", help="specs_repo_path",
            required=True)
        args_parser.add_argument(
            "-c", "--config", dest="config", help="config", default=path + "/config/base.yaml",
            required=False)
        return args_parser

    def __init__(self):
        super().__init__(self.prepare_args_parser())
        cssutils.log.setLevel(logging.FATAL)

    @property
    def max_parallel_tasks_cnt(self):
        return self.configuration['app']['max_parallel_tasks_cnt']

    async def __generate_service_diagram(self,
                                         service_name: str,
                                         services_specs: ServicesSpecs,
                                         template: XmlTemplate,
                                         styles_wrapper: StylesWrapper,
                                         app_configuration: dict,
                                         current_banch: Branch,
                                         show_connect_to_arrow):
        service = services_specs.get_service_spec(service_name)
        styles = ServiceStyleSelector(service, styles_wrapper)
        generator = ServiceNetworkGenerator(service_name,
                                            app_configuration,
                                            services_specs,
                                            template,
                                            styles,
                                            current_banch,
                                            show_connect_to_arrow)
        await generator.generate()
        await generator.save(self.args.specs_repo_path)
        logging.info("[{}]. done.".format(service_name))

    async def run(self):
        diagram_name = "network"
        show_connect_to_arrow = False
        template_path = "{}/diagrams".format(self.args.meta_path)
        current_branch = Branch(self.configuration["git"]["branch"])
        services_specs = ServicesSpecs(self.args.meta_path, GitSpecsRepositoryHelper.topics_info_fname(),
                                       current_branch)
        styles_wrapper = StylesWrapper(template_path + "/" + diagram_name + '/styles.css',
                                       template_path + "/" + diagram_name + '/props.yaml')
        styles = StyleSelector(styles_wrapper)
        template = XmlTemplate()
        await template.load(template_path, diagram_name, "template")
        generator = Generator(self.configuration,
                              services_specs,
                              template,
                              styles,
                              current_branch,
                              show_connect_to_arrow)
        await generator.generate()
        await generator.save(self.args.specs_repo_path)

        template_service = XmlTemplate()
        await template_service.load(template_path, diagram_name, "template_service")
        tasks_pool = TasksPool(self.max_parallel_tasks_cnt)
        for service_name in services_specs.available_services:
            if self.configuration["publish"]["service"] != 'all' and \
                    self.configuration["publish"]["service"] != service_name:
                continue
            await tasks_pool.append(self.__generate_service_diagram(service_name,
                                                                    services_specs,
                                                                    template_service,
                                                                    styles_wrapper,
                                                                    self.configuration,
                                                                    current_branch,
                                                                    show_connect_to_arrow))
        await tasks_pool.done()


async def main():
    app = App()
    await app.run()


if __name__ == '__main__':
    asyncio.run(main())
