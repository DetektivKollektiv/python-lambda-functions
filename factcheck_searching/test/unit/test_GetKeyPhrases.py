import GetKeyPhrases
import pytest


class TestGetKeyPhrases:
    def test_get_phrases_1(self):
        event = {
            "Text": "At the university hospital in Toulouse, France, there are four very critical cases of "
                    "coronavirus in [young people] who do not have any health problems. Their problem is that when "
                    "they all appeared to have symptoms, they all took painkillers like ibuprofen",
            "LanguageCode": "en"
        }
        context = ""
        ret = GetKeyPhrases.get_phrases(event, context)
        assert ret == ['coronavirus',
                        'Their problem',
                        'ibuprofen',
                        'painkillers',
                        'the university hospital']

    def test_get_phrases_2(self):
        event = {
            "Text": "At the university hospital in Toulouse, France, there are four very critical cases of "
                    "coronavirus in [young people] who do not have any health problems. Their problem is that when "
                    "they all appeared to have symptoms, they all took painkillers like ibuprofen",
            "LanguageCode": "tr"
            }
        context = ""
        with pytest.raises(Exception) as excinfo:
            GetKeyPhrases.get_phrases(event, context)
        assert "Language Code not supported!" in str(excinfo.value)

    def test_get_phrases_3(self):
        event = {
            "LanguageCode": "en"
        }
        context = ""
        with pytest.raises(Exception) as excinfo:
            GetKeyPhrases.get_phrases(event, context)
        assert "Please provide Text!" in str(excinfo.value)

    def test_get_phrases_4(self):
        event = {
            "Text": "At the university hospital in Toulouse, France, there are four very critical cases of "
                    "coronavirus in [young people] who do not have any health problems. Their problem is that when "
                    "they all appeared to have symptoms, they all took painkillers like ibuprofen"
        }
        context = ""
        with pytest.raises(Exception) as excinfo:
            GetKeyPhrases.get_phrases(event, context)
        assert "Please provide a Language Code!" in str(excinfo.value)
