from core_layer.db_handler import Session
from ml_service import GetEntities, GetTags, UpdateFactChecks, EnrichItem
from core_layer.model.item_model import Item
from core_layer.handler import item_handler
import os
import random
import time


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
        # with pytest.raises(Exception) as excinfo:
        ret = GetEntities.get_entities(event, context)
        # assert "Language Code not supported!" in str(excinfo.value)
        assert ret == []

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
        # with pytest.raises(Exception) as excinfo:
        ret = GetEntities.get_entities(event, context)
        # assert "Please provide a Language Code!" in str(excinfo.value)
        assert ret == []

    def test_get_entities_5(self):
        event = {
            "Text": "Spanien korrigiert Anzahl der  Corona-Toten von über 26.000 auf 2.000. Bin mal gespannt, "
                    "wie lange D-A-CH noch an den FAKE-Zahlen festhalten wollen.",
            "LanguageCode": "de"
        }
        context = ""
        ret = GetEntities.get_entities(event, context)
        assert ret == ['über 26.000', 'Spanien', '2.000']

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

    def test_get_entities_7(self):
        event = {
            "Text": "Obama finanzierte Labor in Wuhan. | Viral Virus - Lass es jeden wissen ",
            "LanguageCode": "de"
        }
        context = ""
        ret = GetEntities.get_entities(event, context)
        assert ret == ['Wuhan', 'Obama', 'jeden']

    def test_get_entities_8(self):
        event = {
            "Text": "https://viralvirus.de/politik/obama-finanzierte-labor-in-wuhan/?fbclid=IwAR3qOdSnC"
                    "-A7h6wvPQcOFmuFPgLGNOImn_Ee6_vjAGeAmVJ9MVZnoNeFMBk Dass Bill Gates offenbar zu den Finanziers "
                    "und Drahtziehern des Ausbruchs dieser Coronavirus-Pandemie gehört, wird derzeit wild in den "
                    "Staaten diskutiert und steht außer Frage. Dass Ex-US-Präsident Obama genau dieses Labor 2015 mit "
                    "3,7 Millionen US-Dollar finanziell unterstützt hat, wusste bis dato noch niemand. Dokumente, "
                    "die der britischen Zeitung „Daily Mail“ vorliegen, belegen, dass Wissenschaftler im Rahmen eines "
                    "vom US-amerikanischen National Institute of Health (NIH) finanzierten Projekts Experimente an "
                    "Fledermäusen durchgeführt haben sollen. Dem Labor in Wuhan wurde dafür von der "
                    "Obama-Administration ein Fonds von 3,7 Millionen Dollar gewährt. Selbst Donald Trump bestätigte "
                    "dies in einer kürzlich ausgestrahlten Pressekonferenz. I’m against funding Chinese research in "
                    "our country, but I’m sure against funding it in China. The NIH gives a $3.7 million grant to the "
                    "Wuhan Institute of Virology [and] they then advertise that they need coronavirus researchers and "
                    "following that, coronavirus erupts in Wuhan.",
            "LanguageCode": "de"
        }
        context = ""
        ret = GetEntities.get_entities(event, context)
        assert ret == ['Bill Gates', 'Donald Trump', 'Wuhan']

    def test_get_entities_9(self):
        event = {
            "Text": "Der Postillon: Erstes Baby mit Maske geboren ",
            "LanguageCode": "de"
        }
        context = ""
        ret = GetEntities.get_entities(event, context)
        assert ret == ['Erstes Baby']

    def test_get_entities_10(self):
        event = {
            "Text": "https://www.der-postillon.com/2020/09/baby-maske.html \n  München (dpo) - Sensation in der "
                    "Frauenklinik Neuperlach! Dort ist in der\n  Nacht von Dienstag auf Mittwoch das weltweit erste "
                    "Baby mit Mund-Nasen-Schutz geboren. Genetiker vermuten, dass die kleine Mia-Doreen Müller (0) "
                    "ein klares\n  Zeichen dafür ist, dass sich der Mensch evolutionär an die Corona-Pandemie\n  "
                    "anpasst.\n \n  \"Hätt' ich's nicht selbst gesehen, ich hätt's nicht geglaubt\", erinnert sich "
                    "Hebamme Natalie Bechthold an die\n  ungewöhnliche Geburt. \"Wir wussten ja zuerst gar nicht, "
                    "was wir da vor uns haben,\n  als wir die Kleine herausgeholt haben. Plötzlich hat die da dieses "
                    "blaue Ding vor dem Mund.\"\n \n Erste Untersuchungen ergaben, dass es sich bei der Maske um "
                    "einen\n  Mund-Nasen-Schutz des Typ II handelt. Die Besonderheit: Obwohl es in seiner "
                    "Beschaffenheit herkömmlichen\n  medizinischen Einwegmasken ähnelt, scheint das Material komplett "
                    "aus\n  menschlichen Zellen gebildet worden zu sein.  \"Wir vermuten, sie trug die Maske, "
                    "weil sie in der Fruchtblase die 1,50 Meter \nSicherheitsabstand von ihrer Mutter nicht einhalten "
                    "konnte\", so Bechthold.",
            "LanguageCode": "de"
        }
        context = ""
        ret = GetEntities.get_entities(event, context)
        assert ret == ['Natalie Bechthold', '1,50 Meter',
                       'https://www.der-postillon.com/2020/09/baby-maske.html']

    def test_get_entities_11(self):
        event = {
            "Text": "RKI bestätigt Covid-19 Sterblichkeitsrate von 0,01 Prozent in (...) - Corona Transition ",
            "LanguageCode": "de"
        }
        context = ""
        ret = GetEntities.get_entities(event, context)
        assert ret == ['RKI', '0,01 Prozent', 'Covid']

    def test_get_entities_12(self):
        event = {
            "Text": "\nVeröffentlicht am 26. Juni 2020 von VG.\n Dem Papier zufolge gab es bis zum 24. Juni 2020 in "
                    "Deutschland insgesamt 8’914 Todesfälle im Zusammenhang mit der Erkrankung. Bei 83 Millionen "
                    "Einwohnern beträgt somit die absolute Sterblichkeitsrate seit Ausbruch der Coronakrise bis heute "
                    "in Deutschland 0,01 Prozent. Die Zahlen bergen politischen Sprengstoff. Denn unter Federführung "
                    "von Bundeskanzlerin Angela Merkel erlebte die Bundesrepublik einen noch nie dagewesenen "
                    "Lockdown, bei gleichzeitiger Aushebelung der im Grundgesetz verankerten Grundrechte. Die "
                    "deutsche Wirtschaft steckt infolge der verhängten Coronamaßnahmen in der tiefsten Krise seit dem "
                    "2. Weltkrieg, mehr als 10 Millionen Menschen befinden sich derzeit in Kurzarbeit. Der "
                    "Lagebericht des RKI stellt durch seine Daten die Verhältnismäßigkeit der verhängten Maßnahmen in "
                    "Frage. Gleichzeitig verdeutlicht das Zahlenmaterial, dass es keine Anzeichen einer sogenannten "
                    "zweiten Welle gibt. «In den letzten 7 Tagen wurden aus 136 Kreisen keine Fälle übermittelt», "
                    "schreibt das RKI. ",
            "LanguageCode": "de"
        }
        context = ""
        ret = GetEntities.get_entities(event, context)
        assert ret == ['26. Juni 2020', 'Deutschland', '0,01 Prozent']


class TestGetTags:    
    def test_get_tags_1(self):
        event = {
            "Text": "RKI bestätigt Covid-19 Sterblichkeitsrate von 0,01 Prozent in (...) - Corona Transition ",
            "LanguageCode": "de"
        }
        context = ""
        ret = GetEntities.get_tags(event, context)
        assert ret == ['RKI', 'Covid', 'Corona Transition']    

    def test_predict_tags_1(self):
        os.environ["STAGE"] = "dev"
        df_factchecks = UpdateFactChecks.read_df("factchecks_de.csv")
        for ind in range(1):
            claim_text = random.choice(df_factchecks)['claim_text']
            event = {
                "Text": claim_text,
                "LanguageCode": "de"
            }
            context = ""
            ret = GetTags.predict_tags(event, context)
            assert ret != []

    def test_predict_tags_2(self):
        os.environ["STAGE"] = "dev"
        LanguageCode = "de"
        taxonomy_json = GetTags.download_taxonomy(LanguageCode)

        for category in taxonomy_json:
            if category == "similarity-threshold":
                continue
            if category == "excluded-terms":
                continue
            for tag in taxonomy_json[category]:
                for term in taxonomy_json[category][tag]:
                    event = {
                        "Text": term,
                        "LanguageCode": LanguageCode
                    }
                    context = ""
                    ret = GetTags.predict_tags(event, context)
                    assert ret == [tag]

    def test_predict_tags_3(self):
        os.environ["STAGE"] = "dev"
        LanguageCode = "de"

        term = "ffp2"

        event = {
            "Text": term,
            "LanguageCode": LanguageCode
        }
        context = ""
        ret = GetTags.predict_tags(event, context)
        assert ret == ["Masken"]

    def test_predict_tags_4(self):
        os.environ["STAGE"] = "qa"
        LanguageCode = "de"
        taxonomy_json = GetTags.download_taxonomy(LanguageCode)
        df_factchecks = UpdateFactChecks.read_df("factchecks_de.csv")

        for _ in range(1):
            claim_text = random.choice(df_factchecks)['claim_text']
            for stopword in ["\"", ",", ".", "!", "?", "«", "»", "(", ")", "-"]:
                claim_text = claim_text.replace(stopword, " ")
            new_text = ""
            tags = []
            for substr in claim_text.split():
                substr = str.lower(substr)
                term_found = False
                for category in taxonomy_json:
                    if category == "similarity-threshold":
                        continue
                    if category == "excluded-terms":
                        continue
                    for tag in taxonomy_json[category]:
                        for term in taxonomy_json[category][tag]:
                            if substr == term:
                                term_found = True
                                if tag not in tags:
                                    tags.append(tag)
                                break
                        if term_found:
                            break
                if not term_found:
                    new_text += substr+" "
            event = {
                "Text": new_text,
                "LanguageCode": LanguageCode
            }
            context = ""
            ret = GetTags.predict_tags(event, context)
            assert ret == tags

    def test_predict_tags_5(self):
        os.environ["STAGE"] = "dev"
        LanguageCode = ""

        term = "ffp2"

        event = {
            "Text": term,
            "LanguageCode": LanguageCode
        }
        context = ""
        ret = GetTags.predict_tags(event, context)
        assert ret == []

    def test_create_tagreport_1(self):
        os.environ["STAGE"] = "dev"

        with Session() as session:

            # creating items
            item = Item()
            item.content = "RKI bestätigt Covid-19 Sterblichkeitsrate von 0,01 Prozent in (...) - Corona Transition "
            item.language = "de"
            item = item_handler.create_item(item, session)
            list_tags = ['Corona-Maßnahmen', 'Senkung der Treibhausgasemissionen', 'China', 'Film', 'Menschen', 'Kanzlerkandidatur', 'sars-cov-2', '#verunglimpft', 'g.co/privacytools', 'Gregor Gysi', 'Bundestagswahl2021', '19', '-', 'Statistik falsch interpretiert', 'Bild.de', 'JF', 'MdB Hansjörg Müller (AFD)', '100 Tage', 'Gruene', '#notwendige Polizeimaßnahmen', 'Sonne']
            for _ in range(200):
                list_tags.append(random.choice(list_tags)+"-"+random.choice(list_tags))
            # store tags
            event = {
                "item": item.to_dict(),
                "Tags": list_tags
            }
            context = ""
            EnrichItem.store_itemtags(event, context)

            event = ""
            context = ""
            s = time.perf_counter()
            GetTags.create_tagreport(event, context)
            elapsed = time.perf_counter() - s
            assert elapsed < 30
