from ml_service import GetEntities
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

    def test_get_entities_13(self):
        event = {
            "Text": "Schweden als Vorbild, wie man es hätte sinnvoll machen können! Doch von unseren Politikdarstellern und Massenmedien kommt schon lange nicht's sinnvolles mehr... Jetzt wird wieder alles dafür getan, die Menschen einzusperren und den zweiten Lockdown zu erzwingen. Mit Angst und Panik werden die Menschen gefügig gemacht und genügend werden wieder darauf reinfallen. Doch ebenso werden immer mehr Menschen wach und erkennen was wirklich los ist.  Der Tag wird kommen, an dem die Wahrheit ans Licht kommt und dann möchte ich nicht in der Haut der Verantwortlichen stecken. Bei unserem Volldrosten, geht es gerade los und er wird bald keinen Fuß mehr auf die Erde bekommen.  Um was es genau geht, erfährst du hier! 👇 Https://t.me/sebastiankarpf ",
            "LanguageCode": "de"
        }
        context = ""
        ret = GetEntities.get_entities(event, context)
        assert ret == ['RKI', '0,01 Prozent', 'Covid']
