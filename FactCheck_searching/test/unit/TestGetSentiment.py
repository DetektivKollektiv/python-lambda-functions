import GetSentiment
import pytest


class TestGetSentiment:
    def test_get_sentiment_1(self):
        event = {
            "Text": "At the university hospital in Toulouse, France, there are four very critical cases of "
                    "coronavirus in [young people] who do not have any health problems. Their problem is that when "
                    "they all appeared to have symptoms, they all took painkillers like ibuprofen",
            "LanguageCode": "en"
        }
        context = ""
        ret = GetSentiment.get_sentiment(event, context)
        assert ret == "NEUTRAL"

    def test_get_sentiment_2(self):
        event = {
            "Text": "At the university hospital in Toulouse, France, there are four very critical cases of "
                    "coronavirus in [young people] who do not have any health problems. Their problem is that when "
                    "they all appeared to have symptoms, they all took painkillers like ibuprofen",
            "LanguageCode": "tr"
        }
        context = ""
        with pytest.raises(Exception) as excinfo:
            GetSentiment.get_sentiment(event, context)
        assert "Language Code not supported!" in str(excinfo.value)

    def test_get_sentiment_3(self):
        event = {
            "LanguageCode": "en"
        }
        context = ""
        with pytest.raises(Exception) as excinfo:
            GetSentiment.get_sentiment(event, context)
        assert "Please provide Text!" in str(excinfo.value)

    def test_get_sentiment_4(self):
        event = {
            "Text": "At the university hospital in Toulouse, France, there are four very critical cases of "
                    "coronavirus in [young people] who do not have any health problems. Their problem is that when "
                    "they all appeared to have symptoms, they all took painkillers like ibuprofen"
        }
        context = ""
        with pytest.raises(Exception) as excinfo:
            GetSentiment.get_sentiment(event, context)
        assert "Please provide a Language Code!" in str(excinfo.value)

    def test_get_sentiment_5(self):
        event = {
            "Text": "Spanien korrigiert Anzahl der  Corona-Toten von über 26.000 auf 2.000. Bin mal gespannt, "
                    "wie lange D-A-CH noch an den FAKE-Zahlen festhalten wollen.",
            "LanguageCode": "de"
        }
        context = ""
        ret = GetSentiment.get_sentiment(event, context)
        assert ret == "NEUTRAL"
