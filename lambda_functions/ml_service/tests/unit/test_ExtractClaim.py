from ml_service import ExtractClaim


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

        text_0 = "Wollen wir auch einen Channel für solche Themen anlegen?"
        titel = "Corona-Krise und Klimawandel: Fünf Desinformations-Tricks, die jeder kennen sollte " \
            "- DER SPIEGEL "
        # assert resp["urls"][0] == ""
        # assert resp["titles"][0] == ""
        # assert resp["text"][0] == text_0
        assert resp["urls"][0] == "https://www.spiegel.de/wissenschaft/mensch/corona-krise-und-klimawandel-fuenf" \
                                  "-desinformations-tricks-die-jeder-kennen-sollte-a-6892ff9b-fb28-43ae-8438-55b49d607e57" \
                                  "?sara_ecid=soci_upd_wbMbjhOSvViISjc8RPU89NcCvtlFcJ"
        assert resp["title"] == titel
        # assert resp["text"][0] == text_1
        assert resp["concatenation"]["Text"] == text_0 + ' ' + titel

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
        assert resp["concatenation"]["Text"] == ' '

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
        assert resp["concatenation"]["Text"] == ' '

    def test_extract_claim_5(self):
        event = {
            "item": {
                "content": "Was für ein Trottel ist das denn? https://www.facebook.com/karpfsebastian/photos/a.929158223891040/1854136161393237/?type=3&theater",
                "id": "123456",
                "language": ""
            }
        }
        context = ""
        resp = ExtractClaim.extract_claim(event, context)
        assert resp["concatenation"]["Text"] == 'Was für ein Trottel ist das denn?  Facebook '

    def test_extract_claim_6(self):
        event = {
            "item": {
                "content": "https://kopp-report.de/helios-kliniken-veroeffentlichen-corona-fakten-keine-pandemie-von-nationaler-tragweite/?fbclid=IwAR1fMRjkKXXYQUiNxYrgYczcffvNZbW-F3z8Q4f4Ar00caSNO1KjFtyJrG4",
                "id": "123456",
                "language": ""
            }
        }
        context = ""
        resp = ExtractClaim.extract_claim(event, context)
        assert resp["title"] == 'Helios-Kliniken veröffentlichen Corona-Fakten: Keine Pandemie von nationaler Tragweite? - Kopp Report '
