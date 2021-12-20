from uuid import uuid4
from ml_service import ExtractClaim
from core_layer.model.item_model import Item
from core_layer.model.url_model import URL, ItemURL
from core_layer.handler import item_handler
from core_layer.db_handler import Session


class TestExtractClaim:
    def test_extract_claim_1(self):
        with Session() as session:
            urls = ["https://www.spiegel.de/wissenschaft/mensch/corona-krise-und-klimawandel-fuenf-desinformations-tricks-die-jeder-kennen-sollte-a-6892ff9b-fb28-43ae-8438-55b49d607e57?sara_ecid=soci_upd_wbMbjhOSvViISjc8RPU89NcCvtlFcJ"]
            item = create_item_with_urls(session, urls)

            event = {
                "item": {
                    "content": "Wollen wir auch einen Channel für solche Themen anlegen?"
                               "https://www.spiegel.de/wissenschaft/mensch/corona-krise-und-klimawandel-fuenf"
                               "-desinformations-tricks-die-jeder-kennen-sollte-a-6892ff9b-fb28-43ae-8438-55b49d607e57"
                               "?sara_ecid=soci_upd_wbMbjhOSvViISjc8RPU89NcCvtlFcJ",
                    "id": item.id,
                    "language": ""
                }
            }

            resp = ExtractClaim.extract_claim(event, "")
            text_0 = "Wollen wir auch einen Channel für solche Themen anlegen?"
            title = "Corona-Krise und Klimawandel: Fünf Desinformations-Tricks, die jeder kennen sollte " \
                "- DER SPIEGEL "
            assert resp["title"] == title
            assert resp["concatenation"]["Text"] == text_0 + '\n' + title
            

    def test_extract_claim_2_with_two_urls(self):
        with Session() as session:
            urls = ["https://www.spiegel.de/wissenschaft/mensch/corona-krise-und-klimawandel-fuenf-desinformations-tricks-die-jeder-kennen-sollte-a-6892ff9b-fb28-43ae-8438-55b49d607e57?sara_ecid=soci_upd_wbMbjhOSvViISjc8RPU89NcCvtlFcJ", "https://www.google.de"]
            item = create_item_with_urls(session, urls)

            event = {
                "item": {
                    "content": "Wollen wir auch einen Channel für solche Themen anlegen?"
                               "https://www.spiegel.de/wissenschaft/mensch/corona-krise-und-klimawandel-fuenf"
                               "-desinformations-tricks-die-jeder-kennen-sollte-a-6892ff9b-fb28-43ae-8438-55b49d607e57"
                               "?sara_ecid=soci_upd_wbMbjhOSvViISjc8RPU89NcCvtlFcJ Weitere Infos findest du hier: https://www.google.de",

                    "id": item.id,
                    "language": ""
                }
            }

        resp = ExtractClaim.extract_claim(event, "")
        text_0 = "Wollen wir auch einen Channel für solche Themen anlegen?"
        text_1 = " Weitere Infos findest du hier: "
        title_0 = "Corona-Krise und Klimawandel: Fünf Desinformations-Tricks, die jeder kennen sollte " \
                "- DER SPIEGEL "
        title_1 = "Google "
        assert resp["title"] == title_0
        assert resp["concatenation"]["Text"] == text_0 + text_1 + '\n' + title_0 + '\n' + title_1


    def test_extract_claim_without_url(self):
        with Session() as session:
            urls = []
            item = create_item_with_urls(session, urls)

            event = {
                "item": {
                    "content": "Einfach nur Text ohne eine URL",
                    "id": item.id,
                    "language": ""
                }
            }
            resp = ExtractClaim.extract_claim(event, "")
            text_0 = "Einfach nur Text ohne eine URL"
            assert resp["title"] == ""
            assert resp["concatenation"]["Text"] == text_0


    def test_extract_claim_4(self):
        with Session() as session:
            urls = ["https://www.facebook.com/permalink.php?story_fbid=1268489640219684&id=100011759814614"]
            item = create_item_with_urls(session, urls)

            event = {
                "item": {
                    "content": "https://www.facebook.com/permalink.php?story_fbid=1268489640219684&id=100011759814614",
                    "id": item.id,
                    "language": ""
                }
            }
            resp = ExtractClaim.extract_claim(event, "")
            assert resp["concatenation"]["Text"] == '\nTyrac Dracun - 💢  Aufgedeckt: Einführung von Impfpässen... | Facebook '


    def test_extract_claim_5(self):
        with Session() as session:
            urls = ["https://kopp-report.de/helios-kliniken-veroeffentlichen-corona-fakten-keine-pandemie-von-nationaler-tragweite/?fbclid=IwAR1fMRjkKXXYQUiNxYrgYczcffvNZbW-F3z8Q4f4Ar00caSNO1KjFtyJrG4"]
            item = create_item_with_urls(session, urls)

            event = {
                "item": {
                    "content": "https://kopp-report.de/helios-kliniken-veroeffentlichen-corona-fakten-keine-pandemie-von-nationaler-tragweite/?fbclid=IwAR1fMRjkKXXYQUiNxYrgYczcffvNZbW-F3z8Q4f4Ar00caSNO1KjFtyJrG4",
                    "id": item.id,
                    "language": ""
                }
            }
            resp = ExtractClaim.extract_claim(event, "")
            assert resp["concatenation"]["Text"] == '\nHelios-Kliniken veröffentlichen Corona-Fakten: Keine Pandemie von nationaler Tragweite? - Kopp Report '


    def test_extract_claim_6(self):
        with Session() as session:
            urls = ["https://de.rt.com/inland/110251-baden-wurttemberg-zwangseinweisung-fur-hartnackige/"]
            item = create_item_with_urls(session, urls)

            event = {
                "item": {
                    "content": "https://de.rt.com/inland/110251-baden-wurttemberg-zwangseinweisung-fur-hartnackige/",
                    "id": item.id,
                    "language": ""
                }
            }
            resp = ExtractClaim.extract_claim(event, "")
            assert resp["concatenation"]["Text"] == '\nBaden-Württemberg: Zwangseinweisung für "hartnäckige Quarantäneverweigerer" beschlossen — RT DE '


    def test_extract_claim_7(self):
        with Session() as session:
            urls = ["https://www.wochenblick.at/trauriger-rekord-bei-toten-nach-impfung-so-viele-waren-es-noch-nie/"]
            item = create_item_with_urls(session, urls)

            event = {
                "item": {
                    "content": "https://www.wochenblick.at/trauriger-rekord-bei-toten-nach-impfung-so-viele-waren-es-noch-nie/",
                    "id": item.id,
                    "language": ""
                }
            }
            resp = ExtractClaim.extract_claim(event, "")
            assert resp["concatenation"]["Text"] == '\nTrauriger Rekord bei Toten nach Impfung – so viele waren es noch nie! '


    def test_extract_claim_8(self):
        with Session() as session:
            urls = ["https://2020news.de/erschreckende-statistik-impfnebenwirkungen-jetzt-amtlich/"]
            item = create_item_with_urls(session, urls)

            event = {
                "item": {
                    "content": "https://2020news.de/erschreckende-statistik-impfnebenwirkungen-jetzt-amtlich/",
                    "id": item.id,
                    "language": ""
                }
            }
            resp = ExtractClaim.extract_claim(event, "")
            assert resp["concatenation"]["Text"] == '\nErschreckende Statistik - Impfnebenwirkungen jetzt amtlich - 2020 NEWS '


    def test_extract_claim_9(self):
        with Session() as session:
            urls = ["https://unser-mitteleuropa.com/lauterbach-nach-tod-von-32-jaehriger-impftote-fuer-impferfolg-muesse-man-hinnehmen/"]
            item = create_item_with_urls(session, urls)

            event = {
                "item": {
                    "content": "https://unser-mitteleuropa.com/lauterbach-nach-tod-von-32-jaehriger-impftote-fuer-impferfolg-muesse-man-hinnehmen/",
                    "id": item.id,
                    "language": ""
                }
            }
            resp = ExtractClaim.extract_claim(event, "")
            assert resp["concatenation"]["Text"] == '\nLauterbach nach Tod von 32-Jähriger: Impftote für Impferfolg müsse man hinnehmen | UNSER MITTELEUROPA '


    def test_extract_claim_10(self):
        with Session() as session:
            urls = ["https://2020news.de/italien-studie-belegt-stark-erhoehten-co2-wert-unter-der-maske/"]
            item = create_item_with_urls(session, urls)

            event = {
                "item": {
                    "content": "https://2020news.de/italien-studie-belegt-stark-erhoehten-co2-wert-unter-der-maske/",
                    "id": item.id,
                    "language": ""
                }
            }
            resp = ExtractClaim.extract_claim(event, "")
            assert resp["concatenation"]["Text"] == '\nItalien: Studie belegt stark erhöhten CO2-Wert unter der Maske - 2020 NEWS '


def create_item_with_urls(session, urls) -> Item:
    item = Item()
    item.language = "de"
    item = item_handler.create_item(item, session)
    for url_str in urls:
        url = URL()
        url.id = str(uuid4())
        url.url = url_str
        itemUrl = ItemURL()
        itemUrl.item_id = item.id
        itemUrl.url_id = url.id
        itemUrl.id = str(uuid4())
        session.add(url)
        session.add(itemUrl)
        session.commit()
    return item
