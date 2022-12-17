import xml.etree.ElementTree as ET

from aiofile import AIOFile


class XmlTemplate:
    __source: str

    async def load(self, template_path, diagram_template_name: str, template_file_name: str) -> str:
        file_name = "{}/{}/{}.xml".format(template_path, diagram_template_name, template_file_name)
        async with AIOFile(file_name, 'r') as afp:
            self.__source = await afp.read()
            return self.__source

    @property
    def source(self):
        return self.__source

    def parse(self) -> ET.Element:
        e = ET.fromstring(self.__source)
        return e
