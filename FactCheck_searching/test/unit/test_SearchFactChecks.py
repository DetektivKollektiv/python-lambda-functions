import SearchFactChecks
import pytest


class TestSearchFactChecks:
    def test_search_checks_1(self):
        event = {
            "Text": "At the university hospital in Toulouse, France, there are four very critical cases of "
                    "coronavirus in [young people] who do not have any health problems. Their problem is that when "
                    "they all appeared to have symptoms, they all took painkillers like ibuprofen",
            "LanguageCode": "en",
            "KeyPhrases": [
                "coronavirus",
                "Their problem",
                "ibuprofen",
                "painkillers",
                "the university hospital"
            ]
        }
        context = ""
        ret = SearchFactChecks.get_FactChecks(event, context)
        assert 'claimReview' in ret[0]
