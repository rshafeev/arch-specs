import subprocess
from asyncio import create_subprocess_exec
from typing import List, Set

from git import Repo

from core.git.branch import Branch


class GitSpecsRepository:
    _repo_path: str

    __repo: Repo

    def __init__(self, repo_path: str):
        self._repo_path = repo_path

    async def _init(self):
        self.__repo = Repo(self._repo_path)

    @classmethod
    async def create(cls, repos_path):
        self = GitSpecsRepository(repos_path)
        await self._init()
        return self

    @property
    def branches(self) -> Set[Branch]:
        remote_refs = self.__repo.remote().refs
        out = set()
        for refs in remote_refs:
            out.add(Branch(refs.remote_head))
        return out

    def has_branch(self, branch_name) -> bool:
        for branch in self.branches:
            if branch_name == branch.name:
                return True
        return False

    @property
    def release_branches(self) -> Set[Branch]:
        branches = set()
        for branch in self.branches:
            if branch.is_release:
                branches.add(branch)
        return branches

    def latest_release_branches(self, cnt: int) -> List[Branch]:
        return Branch.latest_release_branches(self.release_branches, cnt)

    async def get_diagram_hash_commit(self, service_name: str) -> str:
        return await self.get_file_hash_commit("specs/{}/network_diagram.xml".format(service_name))

    async def get_file_hash_commit(self, filename: str) -> str:
        proc = await create_subprocess_exec(
            "git", "-C", self._repo_path, "log", "-n", "1", "--pretty=format:%H", "--", filename,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        file_hash = await proc.stdout.readline()
        if not file_hash:
            return ""
        file_hash = file_hash.decode('utf-8').replace("'", "")
        return file_hash

    async def current_hash_commit(self) -> str:
        proc = await create_subprocess_exec(
            "git", "-C", self._repo_path, "log", "-n", "1", "--pretty=format:%H",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        hash_commit = await proc.stdout.readline()
        if not hash_commit:
            return ""
        hash_commit = hash_commit.decode('utf-8').replace("'", "")
        return hash_commit

    async def current_branch(self) -> Branch:
        return Branch(self.__repo.active_branch.name)
