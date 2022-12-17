import logging
import os
from typing import Tuple

from PIL import ImageFont

from diagrams_generator.diagrams.styles_wrapper import Style


def get_text_dimensions(text: str, font_size: int, font_file='times.ttf') -> Tuple[float, float]:
    font = ImageFont.truetype(font_file, font_size)
    size = font.getsize(text)
    return size


class TextPixelSize:
    config: dict

    def __init__(self, config: dict):
        self.config = config

    def __get_font_filename(self, font_family: str):
        path = os.path.dirname(__file__)
        for e in self.config['fonts']:
            if e["family"] == font_family:
                return "{}/../res/fonts/{}".format(path, e['file'])
        return None

    def text_dimensions(self, text, style: Style) -> Tuple[float, float]:
        font_size = int(style.font_size())
        font_family = style.font_family()
        font_file = self.__get_font_filename(font_family)
        if font_file is None:
            logging.error("Could not find font '{}' in the system".format(font_family))
        return get_text_dimensions(text, font_size, font_file)

    @staticmethod
    def text_dim(config, text, style: Style) -> Tuple[float, float]:
        return TextPixelSize(config).text_dimensions(text, style)
