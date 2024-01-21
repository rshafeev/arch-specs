import hashlib

from aiofile import AIOFile


class GitSpecsRepositoryHelper:
    repo_path: str

    @classmethod
    async def file_hash(cls, filename: str) -> str:
        async with AIOFile(filename, 'r') as afp:
            f_text = await afp.read()
            return hashlib.md5(f_text.encode('utf8')).hexdigest()

    @classmethod
    def topics_info_fname(cls) -> str:
        return "{}/topics_info.yaml".format(cls.repo_path)

    @classmethod
    def system_diagram_fname(cls) -> str:
        return "{}/system_arch_diagram.xml".format(cls.repo_path)


    @classmethod
    def diagram_fname(cls, service_name: str) -> str:
        return "{}/specs/{}/network_diagram.xml".format(cls.repo_path, service_name)

    @classmethod
    def network_fname(cls, service_name: str) -> str:
        return "{}/specs/{}/network.json".format(cls.repo_path, service_name)

    @classmethod
    def topics_fname(cls, service_name: str) -> str:
        return "{}/specs/{}/topics.json".format(cls.repo_path, service_name)

    @classmethod
    def rx_topics_fname(cls, service_name: str) -> str:
        return "{}/specs/{}/rx_topics.json".format(cls.repo_path, service_name)

    @classmethod
    def tx_topics_fname(cls, service_name: str) -> str:
        return "{}/specs/{}/tx_topics.json".format(cls.repo_path, service_name)
    @classmethod
    def celery_tasks_fname(cls, service_name: str) -> str:
        return "{}/specs/{}/celery_tasks.json".format(cls.repo_path, service_name)

    @classmethod
    def rx_celery_tasks_fname(cls, service_name: str) -> str:
        return "{}/specs/{}/rx_celery_tasks.json".format(cls.repo_path, service_name)
    @classmethod
    def tx_celery_tasks_fname(cls, service_name: str) -> str:
        return "{}/specs/{}/tx_celery_tasks.json".format(cls.repo_path, service_name)

    @classmethod
    def rmq_queues_fname(cls, service_name: str) -> str:
        return "{}/specs/{}/rmq_queues.json".format(cls.repo_path, service_name)

    @classmethod
    def rmq_rx_queues_fname(cls, service_name: str) -> str:
        return "{}/specs/{}/rx_rmq_queues.json".format(cls.repo_path, service_name)

    @classmethod
    def rmq_tx_queues_fname(cls, service_name: str) -> str:
        return "{}/specs/{}/tx_rmq_queues.json".format(cls.repo_path, service_name)