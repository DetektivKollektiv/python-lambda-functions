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
                       'the university hospital',
                       'Their problem',
                       'symptoms',
                       'Toulouse, France']

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

    def test_get_phrases_5(self):
        event = {
            "Text": "Spanien korrigiert Anzahl der  Corona-Toten von über 26.000 auf 2.000. Bin mal gespannt, "
                    "wie lange D-A-CH noch an den FAKE-Zahlen festhalten wollen.",
            "LanguageCode": "de"
        }
        context = ""
        ret = GetKeyPhrases.get_phrases(event, context)
        assert ret == ['Spanien', 'Anzahl der  Corona-Toten', 'den FAKE-Zahlen', 'über 26.000', 'Bin']

    def test_get_phrases_6(self):
        event = {
            "Text": "GERADE VON NTV AUFGENOMMEN!!!! MERKEL EMPFÄNGT MINSITERPRÄSIDENTEN IM KANZLERAMT.WO IST DER "
                    "SICHERHEITSABSTAND, WO SIND DIE MASKEN??? SELBST SÖDER TRÄGT KEINE, ABER WEHE DER STEHT IN "
                    "BAYERN VOR EINER PK, DA KOMMT DER DANN MIT MASKE REIN.WAS EIN VERLOGENES VOLK",
            "LanguageCode": "de"
        }
        context = ""
        ret = GetKeyPhrases.get_phrases(event, context)
        assert ret == ['BAYERN VOR EINER PK',
                       'DA KOMMT DER DANN MIT MASKE REIN.WAS',
                       '??? SELBST SÖDER TRÄGT KEINE',
                       'WO',
                       'ABER WEHE DER STEHT']
