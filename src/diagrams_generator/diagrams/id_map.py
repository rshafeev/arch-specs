from typing import Optional


# class IdMapper:
#
#     __ids: dict
#
#     __tags: dict
#
#     def __init__(self):
#         self.__ids = {}
#         self.__tags = {}
#
#     def id(self, id_to_xml: str) -> str:
#         if id_to_xml not in self.__ids:
#             new_id = 10
#             for e in self.__ids:
#                 new_id = max(new_id, self.__ids[e])
#             self.__ids[id_to_xml] = new_id + 1
#         return str(self.__ids[id_to_xml])
#
#     def id_s(self, id_from_xml: str) -> Optional[str]:
#         for e in self.__ids:
#             if str(self.__ids[e]) == id_from_xml:
#                 return e
#         return None
#
#     def tag(self, tag_to_xml: str) -> str:
#         if tag_to_xml == 'arrow':
#             self.__tags[tag_to_xml] = 'arrow'
#             return str(self.__tags[tag_to_xml])
#         if tag_to_xml not in self.__tags:
#             new_tag = 10
#             for e in self.__tags:
#                 if e == 'arrow':
#                     continue
#                 new_tag = max(new_tag, self.__tags[e])
#             self.__tags[tag_to_xml] = new_tag + 1
#         return str(self.__tags[tag_to_xml])
#
#     def tag_s(self, tag_from_xml: str) -> Optional[str]:
#         for e in self.__tags:
#             if str(self.__tags[e]) == tag_from_xml:
#                 return e
#         return None

class IdMapper:

    __ids: dict

    __tags: dict

    def __init__(self):
        self.__ids = {}
        self.__tags = {}

    def id(self, id_to_xml: str) -> str:
        return id_to_xml

    def id_s(self, id_from_xml: str) -> Optional[str]:
        return id_from_xml

    def tag(self, tag_to_xml: str) -> str:
        return tag_to_xml

    def tag_s(self, tag_from_xml: str) -> Optional[str]:
        return tag_from_xml


ID_MAP = IdMapper()
