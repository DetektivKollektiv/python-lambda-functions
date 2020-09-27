import ExtractClaim


class TestExtractClaim:
    def test_extract_claim_1(self):
        event = {
            "item": {
                "content": "Wollen wir auch einen Channel für solche Themen anlegen?"
                           "https://www.spiegel.de/wissenschaft/mensch/corona-krise-und-klimawandel-fuenf"
                           "-desinformations-tricks-die-jeder-kennen-sollte-a-6892ff9b-fb28-43ae-8438-55b49d607e57"
                           "?sara_ecid=soci_upd_wbMbjhOSvViISjc8RPU89NcCvtlFcJ",
                "id": "123456",
                "language": ""
            }
        }
        context = ""
        resp = ExtractClaim.extract_claim(event, context)

        text_0 = "Wollen wir auch einen Channel für solche Themen anlegen?" \
                 "https://www.spiegel.de/wissenschaft/mensch/corona-krise-und-klimawandel-fuenf" \
                 "-desinformations-tricks-die-jeder-kennen-sollte-a-6892ff9b-fb28-43ae-8438-55b49d607e57" \
                 "?sara_ecid=soci_upd_wbMbjhOSvViISjc8RPU89NcCvtlFcJ"
        text_1 = '\n \n \n\n US-Präsident Donald Trump, Fachmann für Falschinformation Haben Sie auch solche ' \
                 "Nachrichten über soziale Medien bekommen: Covid-19 ist nicht schlimmer als die " \
                 "normale Grippe? Und wird in Wahrheit durch Bakterien, nicht Viren verursacht? " \
                 "Bill Gates hat die Coronakrise erfunden, um die Menschheit zwangsweise zu impfen? " \
                 "Atemmasken sind gefährlich, weil sich dahinter Kohlenmonoxid und Kohlendioxid " \
                 "staut? " \
                 "Ich verlinke die Quellen absichtlich nicht, denn es sind Falschmeldungen. Aber " \
                 "womöglich haben Sie doch gezögert, ob vielleicht etwas dran sein könnte? Und sich " \
                 "gefragt: Wie kann ich unwissenschaftliche Falschmeldungen erkennen? Das ist nicht " \
                 "immer einfach. Aber es hilft zu wissen, mit welchen Tricks die Urheber von " \
                 "Desinformation arbeiten. Egal ob es um die Ursache von Aids, die Evolutionstheorie, " \
                 "den Klimawandel oder jetzt um Corona geht: die Leugner wissenschaftlicher " \
                 "Erkenntnisse " \
                 "verwenden immer wieder dieselben fünf Tricks, um ihr Laienpublikum zu verführen. " \
                 "Stefan Rahmstorf  schreibt regelmäßig für den SPIEGEL über die Klimakrise. Er ist " \
                 "Klima- und Meeresforscher und leitet die Abteilung Erdsystemanalyse am " \
                 "Potsdam-Institut " \
                 "für Klimafolgenforschung (PIK). Seit 2000 ist er zudem Professor für Physik " \
                 "der " \
                 "Ozeane an der Universität Potsdam. Zu seinen Forschungsschwerpunkten gehören die " \
                 "Paläoklimaforschung, Veränderungen von Meeresströmungen und Meeresspiegel sowie Wetterextreme. "

        # assert resp["urls"][0] == ""
        # assert resp["titles"][0] == ""
        # assert resp["text"][0] == text_0
        assert resp["urls"][0] == "https://www.spiegel.de/wissenschaft/mensch/corona-krise-und-klimawandel-fuenf" \
                                  "-desinformations-tricks-die-jeder-kennen-sollte-a-6892ff9b-fb28-43ae-8438-55b49d607e57" \
                                  "?sara_ecid=soci_upd_wbMbjhOSvViISjc8RPU89NcCvtlFcJ"
        assert resp["title"] == "Corona-Krise und Klimawandel: Fünf Desinformations-Tricks, die jeder kennen sollte " \
                                "- DER SPIEGEL "
        # assert resp["text"][0] == text_1
        assert resp["concatenation"]["Text"] == text_0 + ' ' + text_1

    def test_extract_claim_2(self):
        event = {
            "item": {
                "content": "Stimmt das? "
                           "www.compact-online.de/utes-moma-2-8-altmaier-will-haertere-strafen-bei-verstoessen-gegen"
                           "-die-corona-regeln",
                "id": "123456",
                "language": ""
            }
        }
        context = ""
        resp = ExtractClaim.extract_claim(event, context)
        assert resp["urls"] == []

    def test_extract_claim_3(self):
        event = {
            "item": {
                "content": "http://LOCALHOST/utes-moma-127-8-altmaier-will-haertere-strafen-bei-verstoessen-gegen-die"
                           "-corona-regeln/",
                "id": "123456",
                "language": ""
            }
        }
        context = ""
        resp = ExtractClaim.extract_claim(event, context)
        assert resp["concatenation"]["Text"] == event["item"]["content"] + ' '

    def test_extract_claim_4(self):
        event = {
            "item": {
                "content": "http://127.0.0.1/utes-moma-127-8-altmaier-will-haertere-strafen-bei-verstoessen-gegen-die"
                           "-corona-regeln/",
                "id": "123456",
                "language": ""
            }
        }
        context = ""
        resp = ExtractClaim.extract_claim(event, context)
        assert resp["concatenation"]["Text"] == event["item"]["content"] + ' '
