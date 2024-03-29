from core_layer.db_handler import Session

from core_layer.model.item_model import Item
from ml_service import ExtractClaim, GetLanguage, GetKeyPhrases, GetEntities, SearchFactChecks
from core_layer.handler import item_handler, url_handler
import os
import re

import logging

class TestDocSim:
    def test_DocSim_vs_RegExp(self):
        os.environ["STAGE"] = "dev"

        with Session() as session:

            claim_factcheck_dicts = [
                {
                    "claim": "https://www.facebook.com/DieSteffi82/posts/5064896943550398",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/23/nein-abstrichstaebchen-von-corona-schnelltests-sind-nicht-verseucht/",
                    "stepfunction": {}
                },
                {
                    # nicht extrahierbar
                    "claim": "In Ägypten war das eine Strafe für Slaves... Breche die Drüse der Blutenzephalitis: https://www.facebook.com/photo.php?fbid=3591706030868619&set=a.368339826538605&type=3",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/23/nein-nasenabstriche-fuer-einen-corona-test-gleichen-nicht-einer-strafe-fuer-sklaven-im-alten-aegypten/",
                    "stepfunction": {}
                },
                {
                    # twitter benötigt eine andere extraktionsmethode
                    "claim": "An der Universität Cambridge wurden alle 9000 Studenten mit PCR getestet. Alle Tests stellten sich im nach hinein als falsch positiv heraus - 100% falsche Ergebnisse und auf diesem Test beruhen, Foderungen  und Massnahmen. Es reicht jetzt wirklich.: https://twitter.com/LuanaNussbaum/status/1336956296017350657?s=20",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/23/nein-an-der-universitaet-cambridge-wurden-nicht-9-000-studierende-falsch-positiv-auf-corona-getestet/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://www.facebook.com/Silberjungede-Wir-wollen-Augen-öffnen-Thorsten-Schulte-155330287422/videos/381310726307004/",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/22/dauer-lockdown-angela-merkels-aussage-wird-irrefuehrend-interpretiert/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://www.facebook.com/svensworld000/videos/2792271450987454/",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/21/video-keine-belege-dass-ein-corona-schnelltest-positiv-auf-fruchtsaft-reagierte/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://corona-transition.org/rki-bestatigt-covid-19-sterblichkeitsrate-von-0-01-prozent-in" \
                        "-deutschland?fbclid=IwAR2vLIkW_3EejFaeC5_wC_410uKhN_WMpWDMAcI-dF9TTsZ43MwaHeSl4n8%22 ",
                    "factcheck": "https://correctiv.org/faktencheck/2020/07/09/nein-rki-bestaetigt-nicht-eine-covid-19-sterblichkeitsrate-von-001-prozent-in-deutschland/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://kopp-report.de/helios-kliniken-veroeffentlichen-corona-fakten-keine-pandemie-von-nationaler-tragweite/?fbclid=IwAR1fMRjkKXXYQUiNxYrgYczcffvNZbW-F3z8Q4f4Ar00caSNO1KjFtyJrG4",
                    "factcheck": "https://correctiv.org/faktencheck/medizin-und-gesundheit/2020/11/06/corona-zahlen-ueber-patienten-auf-intensivstationen-in-helios-kliniken-werden-irrefuehrend-verbreitet/",
                    "stepfunction": {}
                },
                {
                    "claim": "Manche Corona-Tests brauchen keine externe Qualitätskontrolle",
                    "factcheck": "https://www.br.de/nachrichten/wissen/warum-viele-corona-tests-noch-keine-qualitaetskontrolle-brauchen,SI1KrNC",
                    "stepfunction": {}
                },
    #            {
    #                "claim": "https://viralvirus.de/politik/obama-finanzierte-labor-in-wuhan/?fbclid=IwAR3qOdSnC-A7h6wvPQcOFmuFPgLGNOImn_Ee6_vjAGeAmVJ9MVZnoNeFMBk",
    #                "factcheck": "https://correctiv.org/faktencheck/2020/07/21/nein-die-us-regierung-unter-obama-hat-das-institut-fuer-virologie-in-wuhan-nicht-mit-37-millionen-dollar-unterstuetzt/",
    #                "stepfunction": {}
    #            },
                {
                    "claim": "Spanien korrigiert Anzahl der  Corona-Toten von über 26.000 auf 2.000. Bin mal gespannt, wie lange D-A-CH noch an den FAKE-Zahlen festhalten wollen.",
                    "factcheck": "https://correctiv.org/faktencheck/2020/06/16/nein-spanien-hat-die-zahl-der-corona-toten-nicht-auf-2-000-korrigiert/",
                    "stepfunction": {}
                },
                {
                    "claim": "GERADE VON NTV AUFGENOMMEN!!!! MERKEL EMPFÄNGT MINSITERPRÄSIDENTEN IM KANZLERAMT.WO IST DER SICHERHEITSABSTAND, WO SIND DIE MASKEN??? SELBST SÖDER TRÄGT KEINE, ABER WEHE DER STEHT IN BAYERN VOR EINER PK, DA KOMMT DER DANN MIT MASKE REIN.WAS EIN VERLOGENES VOLK",
                    "factcheck": "https://correctiv.org/faktencheck/2020/06/24/nein-merkel-hat-die-ministerpraesidenten-nicht-ohne-sicherheitsabstand-empfangen/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://www.bitchute.com/video/WGkyGAUdwqlh/",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/17/sprachnachricht-verbreitet-unbelegte-behauptung-ueber-corona-tests-mit-voreingestelltem-ergebnis/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://www.facebook.com/corinnas.angelika.winkler/videos/4668198303252715",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/16/video-nein-corona-schnelltest-reagiert-nicht-positiv-auf-rotwein/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://www.facebook.com/steffen.mono/videos/1531749847023893/",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/16/positiver-corona-test-bei-apfelmus-hat-keine-aussagekraft/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://www.ots.at/presseaussendung/OTS_20201210_OTS0242/fpoe-schnedlitz-macht-live-coronatest-im-parlament",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/15/antigen-schnelltest-falsch-durchgefuehrt-fpoe-politiker-testet-cola-auf-corona/",
                    "stepfunction": {}
                },
                {
                    # twitter benötigt eine andere extraktionsmethode
                    "claim": "Ich übersetzte das mal für die #Gerichte: Jeder Patient mit #Lungenentzündung, der Kontakt mit einer positiv getesteten Person hatte, wird als Covid19 Fall gemeldet, auch wenn er selbst negativ getestet wurde. https://twitter.com/QuakDr/status/1332601338514038784",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/15/es-stimmt-nicht-dass-jeder-patient-mit-lungenentzuendung-als-corona-fall-gezaehlt-wird/",
                    "stepfunction": {}
                },
                {
                    # nicht extrahierbar
                    "claim": "Lothar Wieler vom RKI: Wir haben viel gelernt.. unabhängig davon ob es das Virus gibt, oder nicht Diese Aussage muss man sich mal auf der Zunge zergehen lassen! https://www.facebook.com/photo.php?fbid=3466879523407507&set=a.897173730378112&type=3",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/15/ob-es-das-virus-gibt-oder-nicht-zitat-von-rki-chef-lothar-wieler-aus-dem-kontext-gerissen/",
                    "stepfunction": {}
                },
                {
                    # nicht extrahierbar
                    "claim": "Die Schweizer Zulassungsbehörde hat soeben den deutschen mRNA-Corona-Impfstoff als zu gefährlich und unkalkulierbar ABGELEHNT. ***** TELEBASEL.CH Swissmedic: Stand heute können wir keine Zulassung für einen Impfstoff erteilen https://www.facebook.com/photo.php?fbid=1187531251644128&set=a.135783410152256&type=3",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/14/schweiz-nein-einem-corona-impfstoff-wurde-nicht-die-zulassung-verweigert-weil-er-zu-gefaehrlich-und-unkalkulierbar-sei/",
                    "stepfunction": {}
                },
                {
                    # Forbidden to extract
                    "claim": "Italien: Studie belegt stark erhöhten CO2-Wert unter der Maske https://2020news.de/italien-studie-belegt-stark-erhoehten-co2-wert-unter-der-maske/",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/14/nein-eine-angebliche-studie-belegt-keinen-zu-hohen-co2-wert-unter-masken/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://www.facebook.com/yhardt/videos/10222050726953076",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/10/impfstudie-alles-deutet-darauf-hin-dass-dieser-arzt-in-brasilien-nicht-durch-eine-corona-impfung-starb/",
                    "stepfunction": {}
                },
                {
                    # nicht extrahierbar
                    "claim": "Warum ist es notwendig, tief in der Nase nach dem Virus zu suchen?... Wäre es nicht ausreichend, auf das Stäbchen zu spucken, wenn doch angeblich das Virus au einem Meter schon ansteckend sein soll? https://www.facebook.com/photo.php?fbid=1773053819513552&set=a.794989853986625&type=3",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/10/deshalb-wird-der-abstrich-fuer-pcr-tests-meist-am-nasenrachen-gemacht/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://fingersblog.com/2020/11/19/niederlande-nur-wer-geimpft-ist-darf-sich-wieder-frei-bewegen/",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/10/vorteile-fuer-menschen-die-sich-gegen-covid-19-impfen-lassen-niederlaendischer-gesundheitsminister-spricht-von-missverstaendnis/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://corona-transition.org/amtliche-anweisung-an-arzte-und-apotheker-bitte-sprechen-sie-die-risiken-nicht",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/09/nein-jens-spahn-hat-nicht-gesagt-dass-apotheker-keine-bedenken-zu-corona-impfstoffen-aeussern-sollen/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://www.youtube.com/watch?v=io5ShKM4MV8&feature=youtu.be",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/09/unwissenheit-ueber-covid-19-impfstoffe-aelteres-interview-mit-rki-chef-wieler-wird-irrefuehrend-verbreitet/",
                    "stepfunction": {}
                },
                {
                    # nicht extrahierbar
                    "claim": "Weisheit des Tages: Wenn man an COVID stirbt, wird man sehr leicht... https://www.facebook.com/groups/648478082346782/permalink/978930515968202/",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/07/nein-diese-bilder-von-leichensaecken-und-einem-sarg-zeigen-nicht-dass-corona-todesfaelle-inszeniert-werden/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://www.facebook.com/permalink.php?story_fbid=2992046007562267&id=353649981401896",
                    "factcheck": "https://correctiv.org/faktencheck/2020/12/07/nein-das-tragen-einer-maske-fuehrt-nicht-zu-sauerstoffmangel-bei-kindern/",
                    "stepfunction": {}
                },
                {
                    "claim": "Es gibt fünf Gruppen in Deutschland, denen steigende Energiekosten ziemlich egal sind. Millionäre, Hartzer, Flüchtlinge, Migranten, Häftlinge. Der Rest geht arbeiten und bezahlt das",
                    "factcheck": "https://correctiv.org/faktencheck/2021/11/09/steigende-stromkosten-betreffen-auch-gefluechtete-und-hartz-iv-empfaenger/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://t.me/rabbitresearch/6103",
                    "factcheck": "https://correctiv.org/faktencheck/2021/11/11/astroworld-festival-warum-es-zu-herzstillstaenden-bei-opfern-von-massenpaniken-kommt/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://t.me/medusa_auge/66",
                    "factcheck": "https://correctiv.org/faktencheck/2021/11/09/nein-in-italien-sind-nicht-nur-3-783-menschen-an-covid-19-gestorben/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://t.me/rabbitresearch/5867",
                    "factcheck": "https://correctiv.org/faktencheck/2021/11/05/queensland-australien-quarantaenezentrum-ist-fuer-einreisende-nicht-fuer-ungeimpfte/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://politikstube.com/lettland-ungeimpfte-duerfen-kuenftig-keinen-supermarkt-mehr-betreten/",
                    "factcheck": "https://correctiv.org/faktencheck/2021/11/04/lettland-duerfen-geimpfte-und-ungeimpfte-im-supermarkt-einkaufen/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://www.facebook.com/christin.friedemann.5/posts/4744025482297806",
                    "factcheck": "https://correctiv.org/faktencheck/2021/11/03/nein-geimpfte-zaehlen-nicht-als-ungeimpfte-sobald-sie-symptome-entwickeln/",
                    "stepfunction": {}
                },
                {
                    "claim": "https://www.facebook.com/permalink.php?story_fbid=248120460708233&id=100065308425434",
                    "factcheck": "https://correctiv.org/faktencheck/2021/11/02/nein-argentinien-setzt-die-covid-19-impfstoffe-von-moderna-und-pfizer-nicht-bis-2023-aus/",
                    "stepfunction": {}
                },

            ]

            # search fact checks for all items
            count_fcExists = 0
            count_kp_tp = 0
            count_kp_fn = 0
            count_noFc = 0
            count_kp_tn = 0
            count_kp_fp = 0

            for i in range(len(claim_factcheck_dicts)):
                # creating item
                item = Item()
                item.content = claim_factcheck_dicts[i]["claim"]
                item = item_handler.create_item(item, session)
                if item.content:
                    str_urls = re.findall('http[s]?://(?:[a-zA-ZäöüÄÖÜ]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', item.content)
                    url_handler.prepare_and_store_urls(item, str_urls, session)
                claim_factcheck_dicts[i]["stepfunction"]["item"] =  {
                        "id": item.id,
                        "content": item.content,
                        "language": item.language,
                    }

                #extract claim
                event = {
                    "item": claim_factcheck_dicts[i]["stepfunction"]["item"]
                }
                context = ""
                claim = ExtractClaim.extract_claim(event, context)
                claim_factcheck_dicts[i]["stepfunction"]["Claim"] = claim

                # detect language
                event = {
                    "Text": claim["concatenation"]["Text"]
                }
                try:
                    claim_factcheck_dicts[i]["stepfunction"]["item"]["language"] = GetLanguage.get_language(event, context)
                except:
                    continue

                # increment count of factchecks
                if claim_factcheck_dicts[i]["factcheck"] == "":
                    count_noFc = count_noFc+1
                else:
                    count_fcExists = count_fcExists+1

                # detect key phrases
                event["LanguageCode"] = claim_factcheck_dicts[i]["stepfunction"]["item"]["language"]
                claim_factcheck_dicts[i]["stepfunction"]["KeyPhrases"] = GetKeyPhrases.get_phrases(event, context)

                # detect entities
                claim_factcheck_dicts[i]["stepfunction"]["Entities"] = GetEntities.get_entities(event, context)

                # search factchecks with KeyPhrases
                event = {
                    "item": claim_factcheck_dicts[i]["stepfunction"]["item"],
                    "KeyPhrases": claim_factcheck_dicts[i]["stepfunction"]["KeyPhrases"],
                    "Entities": claim_factcheck_dicts[i]["stepfunction"]["Entities"]
                }
                ret = SearchFactChecks.get_FactChecks(event, context)
                url = ""
                if 'claimReview' in ret[0]:
                    url = ret[0]['claimReview'][0]['url']
                if url == claim_factcheck_dicts[i]["factcheck"]:
                    if url == "":
                        count_kp_tn = count_kp_tn+1
                    else:
                        count_kp_tp = count_kp_tp+1
                else:
                    if url == "":
                        count_kp_fn = count_kp_fn+1
                    else:
                        count_kp_fp = count_kp_fp+1

            # calculate rate of false factchecks
            kp_fp = count_kp_fp/(count_fcExists+count_noFc)
            # calculate precision
            kp_pr = count_kp_tp/(count_kp_tp+count_kp_fp)
            # calculate Specitivity
            if count_noFc>0:
                kp_tn = count_kp_tn/count_noFc
            else:
                kp_tn = 1.
            if count_fcExists>0:
                # calculate Recall or Sensitivity, respectively
                kp_tp = count_kp_tp/count_fcExists
                # calculate false negatives
                kp_fn = count_kp_fn/count_fcExists
            else:
                kp_tp = 1.
                kp_fn = 1.

            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            logger.info('Precision (How much of the found factchecks are correct) for FactCheck Search: {}'.format(kp_pr))
            logger.info('Recall (Sensitivity, how much of the factchecks were found) for FactCheck Search: {}'.format(kp_tp))
            logger.info('Specifity (if no factcheck was found, how much of them are really without existing factcheck): {}'.format(kp_tn))
            logger.info('False factchecks found: {}'.format(kp_fp))
            logger.info('Existing Factcheck not found: {}'.format(kp_fn))
