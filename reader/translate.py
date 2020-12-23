from googletrans import Translator
from googletrans import urls, utils


class MyTranslator():
    def __init__(self):
        self.transltor = Translator(service_urls=[
            'translate.google.cn', ])

    def _translate(self, text, dest, src):
        token = self.token_acquirer.do(text)
        params = utils.build_params(query=text, src=src, dest=dest,
                                    token=token)
        params['client'] = 'webapp'
        url = urls.TRANSLATE.format(host=self._pick_service_url())
        r = self.session.get(url, params=params)
        if r.status_code == 200:
            data = utils.format_json(r.text)
            return data
        else:
            if self.raise_exception:
                raise Exception('Unexpected status code "{}" from {}'.format(
                    r.status_code, self.service_urls))
            DUMMY_DATA[0][0][0] = text
            return DUMMY_DATA

    def get_extra_result_of_single_word(self, word):
        """
        :param word: single word string contain no space
        :param translator: google translator object
        :return: result string
        """
        translate_res = self.transltor.translate(word, dest='zh-cn')
        extra_data = translate_res.extra_data
        if(extra_data is None):
            return translate_res.text
        all_translations_list = extra_data['parsed']
        result = translate_res.text+"\n"
        try:
            all_translations_list = all_translations_list[3][5][0]
            for translations in all_translations_list:
                result += translations[0]+":\n    "
                for translation in translations[1::3]:
                    for word in translation:
                        result += word[0]+","
                    result = result[:-1]+"\n"
        except:
            result = translate_res.text
        return result

    def get_translation_by_google(self, text_input):
        if len(text_input.split()) == 1:
            trans_result = self.get_extra_result_of_single_word(
                text_input.split()[0])
        else:
            trans_result = self.transltor.translate(
                text_input, dest='zh-cn').text
        return trans_result
