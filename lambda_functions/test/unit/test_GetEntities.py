import GetEntities
import pytest


class TestGetEntities:
    def test_get_entities_1(self):
        event = {
            "Text": "At the university hospital in Toulouse, France, there are four very critical cases of "
                    "coronavirus in [young people] who do not have any health problems. Their problem is that when "
                    "they all appeared to have symptoms, they all took painkillers like ibuprofen",
            "LanguageCode": "en"
        }
        context = ""
        ret = GetEntities.get_entities(event, context)
        assert ret == ['Toulouse, France', 'four very critical cases']

    def test_get_entities_2(self):
        event = {
            "Text": "At the university hospital in Toulouse, France, there are four very critical cases of "
                    "coronavirus in [young people] who do not have any health problems. Their problem is that when "
                    "they all appeared to have symptoms, they all took painkillers like ibuprofen",
            "LanguageCode": "tr"
        }
        context = ""
        with pytest.raises(Exception) as excinfo:
            GetEntities.get_entities(event, context)
        assert "Language Code not supported!" in str(excinfo.value)

    def test_get_entities_3(self):
        event = {
            "LanguageCode": "en"
        }
        context = ""
        ret = GetEntities.get_entities(event, context)
        assert ret == []

    def test_get_entities_4(self):
        event = {
            "Text": "At the university hospital in Toulouse, France, there are four very critical cases of "
                    "coronavirus in [young people] who do not have any health problems. Their problem is that when "
                    "they all appeared to have symptoms, they all took painkillers like ibuprofen"
        }
        context = ""
        with pytest.raises(Exception) as excinfo:
            GetEntities.get_entities(event, context)
        assert "Please provide a Language Code!" in str(excinfo.value)

    def test_get_entities_5(self):
        event = {
            "Text": "Spanien korrigiert Anzahl der  Corona-Toten von über 26.000 auf 2.000. Bin mal gespannt, "
                    "wie lange D-A-CH noch an den FAKE-Zahlen festhalten wollen.",
            "LanguageCode": "de"
        }
        context = ""
        ret = GetEntities.get_entities(event, context)
        assert ret == ['über 26.000', 'Spanien', '2.000', 'D', 'CH']

    def test_get_entities_6(self):
        event = {
            "Text": "GERADE VON NTV AUFGENOMMEN!!!! MERKEL EMPFÄNGT MINSITERPRÄSIDENTEN IM KANZLERAMT.WO IST DER "
                    "SICHERHEITSABSTAND, WO SIND DIE MASKEN??? SELBST SÖDER TRÄGT KEINE, ABER WEHE DER STEHT IN "
                    "BAYERN VOR EINER PK, DA KOMMT DER DANN MIT MASKE REIN.WAS EIN VERLOGENES VOLK",
            "LanguageCode": "de"
        }
        context = ""
        ret = GetEntities.get_entities(event, context)
        assert ret == ['NTV', 'BAYERN']
