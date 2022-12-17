import datetime
from typing import Set, List, Tuple


class Branch(object):
    name: str

    date: datetime

    def __init__(self, branch_name: str):
        self.name = branch_name
        self.date = None
        self.__parse(branch_name)

    def __eq__(self, other: 'Branch'):
        if isinstance(other, Branch):
            return self.name == self.name
        return NotImplemented

    def __hash__(self):
        return hash(self.name)

    @property
    def date_s(self) -> str:
        return self.date.strftime('%Y-%m-%d')

    @property
    def is_release(self) -> bool:
        return self.date is not None

    @property
    def is_master(self) -> bool:
        return self.name == "develop"

    def __parse(self, branch_name: str):
        if branch_name.find("release-") < 0 or len("release-") == len(branch_name):
            return
        branch_date_s = branch_name[len("release-"): len(branch_name)]
        try:
            self.date = datetime.datetime.strptime(branch_date_s, '%Y-%m-%d')
        except Exception as ex:
            self.date = None

    @classmethod
    def latest_release_branches(cls, release_branches: Set['Branch'], cnt: int) -> List['Branch']:
        sorted_branches = []
        for b in release_branches:
            sorted_branches.append(b)
        if len(sorted_branches) == 0:
            return sorted_branches
        sorted_branches.sort(key=lambda x: x.date,  reverse=True)
        return sorted_branches[0: min(cnt, len(sorted_branches))]

    @classmethod
    def expand_index(cls, release_branches: List['Branch'], has_master_branch: bool) -> Tuple[List['Branch'], int]:
        branches = []
        if has_master_branch:
            branches.append(Branch("develop"))
        release_branches.sort(key=lambda x: x.date, reverse=True)
        branches.extend(release_branches)
        return branches, min(1 if has_master_branch else 0, max(0, len(branches) - 1))

    @classmethod
    def selected(cls, release_branches: List['Branch'], has_master_branch: bool) -> 'Branch':
        branches, expand_branch_index = Branch.expand_index(release_branches, has_master_branch)
        return branches[expand_branch_index]
