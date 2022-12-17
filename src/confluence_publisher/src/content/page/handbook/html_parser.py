from data.confluence.model.page import PAGE_PROPERTIES_MACRO_ID


class HtmlParser:
    _html_s: str

    def __init__(self, html_s: str):
        self._html_s = html_s

    @property
    def html_s(self) -> str:
        return self._html_s

    @html_s.setter
    def html_s(self, value: str):
        self._html_s = value


class ServiceHandbookPageParser(HtmlParser):

    def update_service_properties_section(self, service_properties_html_s: str):
        open_signature_props = '<ac:structured-macro ac:name="details" ac:schema-version="1" ac:macro-id="{}">'.format(
            PAGE_PROPERTIES_MACRO_ID)
        open_signature = '<ac:structured-macro'
        close_signature = '</ac:structured-macro>'
        start_ind = self.html_s.find(open_signature_props)
        if start_ind < 0:
            return
        curr_pos = start_ind + len(open_signature_props)
        open_counter = 1
        close_counter = 0
        while close_counter != open_counter:
            open_ind = self.html_s.find(open_signature, curr_pos)
            close_ind = self.html_s.find(close_signature, curr_pos)
            if open_ind < 0 and close_ind < 0:
                break
            if 0 <= open_ind < close_ind:
                open_counter = open_counter + 1
                curr_pos = open_ind + len(open_signature)
            elif 0 <= close_ind < open_ind:
                close_counter = close_counter + 1
                curr_pos = close_ind + len(close_signature)
        if close_counter == open_counter:
            new_html_s = self.html_s[0:start_ind] + service_properties_html_s + self.html_s[curr_pos:len(self.html_s)]
            self.html_s = new_html_s
