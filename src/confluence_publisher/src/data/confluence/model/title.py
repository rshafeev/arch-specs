from core.git.branch import Branch
from data.specs.service_spec_ext import ServiceSpecExt


class SystemNetworkBranchDiagramPageTitle:
    @staticmethod
    def title(branch: Branch):
        return "[{}] System Diagram".format(branch.name)


class ServiceHandbookPageTitle:
    @staticmethod
    def title(spec: ServiceSpecExt):
        return f"{spec.settings.confluence.service_prefix}{spec.service_name}"


class ServiceHandbookManualPageTitle:
    @staticmethod
    def title(spec: ServiceSpecExt):
        return f"{spec.service_name}: {spec.settings.confluence.manual_page_title}"

class ServiceHandbookOldManualPageTitle:
    @staticmethod
    def title(spec: ServiceSpecExt):
        return f"{spec.service_name}: {spec.settings.confluence.clear_manual_page_title}"


class NetworkBasicPageTitle:
    @staticmethod
    def title(spec: ServiceSpecExt):
        return "{}: communication".format(spec.service_name)


class NetworkBranchPageTitle:
    @staticmethod
    def title(spec: ServiceSpecExt, branch: Branch):
        return "{}: [{}] communication".format(spec.service_name, branch.name)


class NetworkBranchDiagramPageTitle:
    @staticmethod
    def title(spec: ServiceSpecExt, branch: Branch):
        return "{}: [{}] diagram".format(spec.service_name, branch.name)


class NetworkBranchLinksPageTitle:
    @staticmethod
    def title(spec: ServiceSpecExt, branch: Branch):
        return "{}: [{}] connections".format(spec.service_name, branch.name)


class NetworkCurrentPageTitle:
    @staticmethod
    def title(spec: ServiceSpecExt):
        return "{}: current communication".format(spec.service_name)


class NetworkCurrentDiagramPageTitle:
    @staticmethod
    def title(spec: ServiceSpecExt):
        return "{}: current diagram".format(spec.service_name)


class NetworkCurrentLinksPageTitle:
    @staticmethod
    def title(spec: ServiceSpecExt):
        return "{}: current connections".format(spec.service_name)
