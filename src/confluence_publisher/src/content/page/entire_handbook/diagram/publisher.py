import logging

from content.page.system.branch.diagram.view import SystemNetworkBranchDiagramView
from core.git.branch import Branch
from core.git.specs_repo import GitSpecsRepositoryHelper
from core.specs.settings import Settings, ConfluenceSettings
from data.confluence.api.property import PropertyKey
from data.confluence.model.page import ConfluencePage
from data.confluence.service import ConfluenceService
from data.specs.service_spec_ext import ServiceSpecExt
from data.template.templates_storage import HtmlTemplatesStorage


class ServiceDiagramPublisher:
    __confluence: ConfluenceService

    __settings: Settings

    def __init__(self,
                 confluence: ConfluenceService,
                 settings: Settings):
        self.__confluence = confluence
        self.__settings = settings

    async def publish(self, page: ConfluencePage, spec: ServiceSpecExt):
        diagram_confluence_name = "{}_network_diagram".format(spec.service_name)
        diagram_attachment = await self.__confluence.attachments.get(page.id, diagram_confluence_name)
        diagram_fname = GitSpecsRepositoryHelper.diagram_fname(spec.service_name)
        repo_diagram_hash_commit = await GitSpecsRepositoryHelper.file_hash(diagram_fname)
        logging.info(
            "Page '{}'. Current The draw.io component diagram hash: {}".format(page.title, repo_diagram_hash_commit))
        if diagram_attachment is None:
            await self.__confluence.attachments.create(page.id, diagram_fname, diagram_confluence_name)
            await self.__confluence.properties.set(page.id, PropertyKey.network_diagram_hash, repo_diagram_hash_commit)

            logging.info("Page '{}'. The draw.io component diagram was created.".format(page.title))
        else:
            confluenece_diagram_hash = await self.__confluence.properties.get(page.id, PropertyKey.network_diagram_hash)
            if confluenece_diagram_hash is None or confluenece_diagram_hash != repo_diagram_hash_commit:
                await self.__confluence.attachments.update(page.id, diagram_attachment['id'], diagram_fname,
                                                           diagram_confluence_name)
                await self.__confluence.properties.set(page.id, PropertyKey.network_diagram_hash,
                                                       repo_diagram_hash_commit)
                logging.info("Page '{}'. The draw.io component diagram was updated.".format(page.title))
            else:
                logging.info("Page '{}'. The draw.io component diagram is not changed [CACHE].".format(page.title))

