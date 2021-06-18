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
        assert resp["concatenation"]["Text"] == text_0 + ' \n' + titel

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
                "content": "https://www.facebook.com/permalink.php?story_fbid=1268489640219684&id=100011759814614",
                "id": "123456",
                "language": ""
            }
        }
        context = ""
        resp = ExtractClaim.extract_claim(event, context)
        assert resp["concatenation"]["Text"] == ' \nTyrac Dracun - 💢  Aufgedeckt: Einführung von Impfpässen... | Facebook '

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
        assert resp["concatenation"]["Text"] == ' \nHelios-Kliniken veröffentlichen Corona-Fakten: Keine Pandemie von nationaler Tragweite? - Kopp Report '

    def test_extract_claim_7(self):
        event = {
            "item": {
                "content": "https://de.rt.com/inland/110251-baden-wurttemberg-zwangseinweisung-fur-hartnackige/",
                "id": "123456",
                "language": ""
            }
        }
        context = ""
        resp = ExtractClaim.extract_claim(event, context)
        assert resp["concatenation"]["Text"] == ' \nBaden-Württemberg: Zwangseinweisung für "hartnäckige Quarantäneverweigerer" beschlossen — RT DE '

    def test_extract_claim_8(self):
        event = {
            "item": {
                "content": "https://www.wochenblick.at/trauriger-rekord-bei-toten-nach-impfung-so-viele-waren-es-noch-nie/",
                "id": "123456",
                "language": ""
            }
        }
        context = ""
        resp = ExtractClaim.extract_claim(event, context)
        assert resp["concatenation"]["Text"] == ' \nTrauriger Rekord bei Toten nach Impfung – so viele waren es noch nie! '

    def test_extract_claim_9(self):
        event = {
            "item": {
                "content": "https://2020news.de/erschreckende-statistik-impfnebenwirkungen-jetzt-amtlich/",
                "id": "123456",
                "language": ""
            }
        }
        context = ""
        resp = ExtractClaim.extract_claim(event, context)
        assert resp["concatenation"]["Text"] == ' \nErschreckende Statistik - Impfnebenwirkungen jetzt amtlich - 2020 NEWS '

    def test_extract_claim_10(self):
        event = {
            "item": {
                "content": "https://unser-mitteleuropa.com/lauterbach-nach-tod-von-32-jaehriger-impftote-fuer-impferfolg-muesse-man-hinnehmen/",
                "id": "123456",
                "language": ""
            }
        }
        context = ""
        resp = ExtractClaim.extract_claim(event, context)
        assert resp["concatenation"]["Text"] == ' \nLauterbach nach Tod von 32-Jähriger: Impftote für Impferfolg müsse man hinnehmen | UNSER MITTELEUROPA '

    def test_extract_claim_11(self):
        event = {
            "item": {
                "content": "https://2020news.de/italien-studie-belegt-stark-erhoehten-co2-wert-unter-der-maske/",
                "id": "123456",
                "language": ""
            }
        }
        context = ""
        resp = ExtractClaim.extract_claim(event, context)
        assert resp["concatenation"]["Text"] == ' \nItalien: Studie belegt stark erhöhten CO2-Wert unter der Maske - 2020 NEWS '

    def test_extract_claim_12(self):
        event = {
            "item": {
                "content": "https://www.wahrheiten.org/blog/klimaluege/",
                "id": "123456",
                "language": ""
            }
        }
        context = ""
        resp = ExtractClaim.extract_claim(event, context)
        assert resp["concatenation"]["Text"] == ' \nItalien: Studie belegt stark erhöhten CO2-Wert unter der Maske - 2020 NEWS '
