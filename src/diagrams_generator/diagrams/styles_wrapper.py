from typing import Optional

import cssutils
from cssutils.css import CSSStyleSheet, CSSStyleRule, CSSRule

from core.specs.service.connector import ServiceSpecConnector
from core.specs.service.spec import ServiceSpec
from core.specs.specs import read_yaml


class Style:
    __overrides: dict

    def __init__(self, css: CSSStyleRule):
        self.css = css
        self.__overrides = {}

    @staticmethod
    def __get_key_in_drawio_format(key: str):
        s = ""
        for idx, ch in enumerate(key):
            if ch == '-':
                continue
            if idx > 0 and key[idx - 1] == '-':
                s = s + key[idx].upper()
            else:
                s = s + ch
        return s

    def value(self, key: str):
        if key in self.__overrides:
            return self.__overrides[key]
        for e in self.css.style:
            if key == e.name:
                val = e.value
                if len(val) > 2 and val[0] == '"' and val[len(val) - 1] == '"':
                    return val[1:len(val) - 1]
                return e.value
        return None

    def set_value(self, key: str, value: str):
        self.__overrides[key] = value

    def __repr__(self):
        s = ""
        for e in self.css.style:
            val = self.value(e.name)
            if val == '__':
                s = s + "{};".format(self.__get_key_in_drawio_format(e.name))
                continue
            s = s + "{}={};".format(self.__get_key_in_drawio_format(e.name), val)
        return s

    def font_size(self):
        return self.value('font-size')

    def font_family(self):
        return self.value('font-family')


class StylesWrapper:
    stylesheet: CSSStyleSheet

    props: dict

    def __init__(self, css_filename: str, props_filename: str):
        css_parser = cssutils.CSSParser()
        self.stylesheet = css_parser.parseFile(css_filename)
        self.props = read_yaml(props_filename)

    def style(self, name: str) -> Optional[Style]:
        style_name = '.' + name
        for each_rule in self.stylesheet.cssRules:
            if each_rule.type == CSSRule.STYLE_RULE and style_name == each_rule.selectorText:
                return Style(each_rule)
        return None

    def first_available(self, names: list):
        for name in names:
            if name is None:
                continue
            s = self.style(name)
            if s is not None:
                return s
        return None


class StyleSelector:
    styles: StylesWrapper

    def __init__(self, styles: StylesWrapper):
        self.styles = styles

    @property
    def props(self):
        return self.styles.props

    def style(self, name: str) -> Optional[Style]:
        return self.styles.style(name)

    def kafka_image_style(self) -> Optional[Style]:
        names = ['kafka-image']
        return self.styles.first_available(names)

    def service_style(self, spec: ServiceSpec) -> Optional[Style]:
        names = []
        names.append('service-container-{}-{}'.format(spec.type, spec.service_module))
        names.append('service-container-' + spec.type)
        names.append('service-container')
        return self.styles.first_available(names)

    def service_image_style(self, spec: ServiceSpec) -> Optional[Style]:
        names = []
        style_name = 'service-container-image-' + spec.service_module
        names.append(style_name)
        names.append('service-container-image')
        return self.styles.first_available(names)

    def service_label_style(self, spec: ServiceSpec) -> Optional[Style]:
        names = []
        style_name = 'service-container-core-label-' + spec.service_module
        names.append(style_name)
        names.append('service-container-core-label')
        return self.styles.first_available(names)

    def service_status_label_style(self, spec: ServiceSpec) -> Optional[Style]:
        names = []
        style_name = 'service-status-label-' + spec.status.name
        names.append(style_name)
        names.append('service-status-label')
        return self.styles.first_available(names)


    def topic_style(self, spec: ServiceSpec, connector: ServiceSpecConnector, topic_name: str) -> Optional[Style]:
        names = []
        style_name = "service-topic-{}".format(connector.data_direction)
        names.append(style_name)
        return self.styles.first_available(names)

    def topic_disable_style(self, spec: ServiceSpec, connector: ServiceSpecConnector, topic_name: str) -> Optional[Style]:
        names = []
        style_name = "service-topic-disable-{}".format(connector.data_direction)
        names.append(style_name)
        return self.styles.first_available(names)

    def topic_container_style(self, spec: ServiceSpec, connector: ServiceSpecConnector) -> Optional[Style]:
        names = ['service-topics-container-' + spec.service_module, 'service-topics-container']
        return self.styles.first_available(names)

    def topic_container_label_style(self, spec: ServiceSpec, connector: ServiceSpecConnector) -> Optional[Style]:
        names = ['service-topics-container-label-' + spec.service_module, 'service-topics-container-label']
        return self.styles.first_available(names)

    def connector_core_style(self, spec: ServiceSpec, connector: ServiceSpecConnector) -> Optional[Style]:
        names = ['service-connector-core-' + spec.service_module, 'service-connector-core']
        return self.styles.first_available(names)

    def connector_ellipse_style(self, spec: ServiceSpec, connector: ServiceSpecConnector) -> Optional[Style]:
        names = ['service-connector-ellipse-' + spec.service_module, 'service-connector-ellipse']
        return self.styles.first_available(names)

    def connector_label_style(self, spec: ServiceSpec, connector: ServiceSpecConnector) -> Optional[Style]:
        names = ['service-connector-label-' + spec.service_module, 'service-connector-label']
        return self.styles.first_available(names)

    def connector_arrow_style(self, spec: ServiceSpec, connector: ServiceSpecConnector) -> Optional[Style]:
        names = ['service-connector-arrow-' + spec.service_module, 'service-connector-arrow']
        return self.styles.first_available(names)
