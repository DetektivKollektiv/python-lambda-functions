import SearchFactChecks


class TestSearchFactChecks:
    def test_search_checks_1(self):
        event = {
                "item": {
                    "id": "3fb83912-7a97-423a-b820-36718d51b1a6",
                    "content": "https://corona-transition.org/rki-bestatigt-covid-19-sterblichkeitsrate-von-0-01"
                               "-prozent-in-deutschland?fbclid=IwAR2vLIkW_3EejFaeC5_wC_410uKhN_WMpWDMAcI"
                               "-dF9TTsZ43MwaHeSl4n8%22",
                    "language": "de",
                },
                "KeyPhrases": [
                    "das Zahlenmaterial",
                    "es",
                    "den letzten 7 Tagen",
                    "das RKI",
                    "sich"
                ],
                "Entities": [
                    "RKI",
                    "Deutschland",
                    "RKI",
                    "136 Kreisen",
                    "Bundeskanzlerin"
                ],
                "TitleEntities": [
                    "RKI",
                    "0,01 Prozent",
                    "19 Sterblichkeitsrate",
                    "Corona Transition",
                    "Covid"
                ],
                "Sentiment": "NEUTRAL"
            }
        context = ""
        ret = SearchFactChecks.get_FactChecks(event, context)
        assert 'claimReview' in ret[0]
