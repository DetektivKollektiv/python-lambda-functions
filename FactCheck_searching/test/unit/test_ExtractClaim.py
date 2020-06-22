import ExtractClaim


class TestExtractClaim:
    def test_extract_claim_1(self):
        event = {
            "item": {
                "content": "Wollen wir auch einen Channel für solche Themen anlegen? "
                           "https://www.spiegel.de/wissenschaft/mensch/corona-krise-und-klimawandel-fuenf"
                           "-desinformations-tricks-die-jeder-kennen-sollte-a-6892ff9b-fb28-43ae-8438-55b49d607e57"
                           "?sara_ecid=soci_upd_wbMbjhOSvViISjc8RPU89NcCvtlFcJ ",
                "id": "123456",
                "language": ""
            }
        }
        context = ""
        urls, titles, text = ExtractClaim.extract_claim(event, context)
        assert urls[0] == ""
        assert titles[0] == ""
        assert text[0] == "b'Wollen wir auch einen Channel f\\xc3\\xbcr solche Themen anlegen? " \
                          "https://www.spiegel.de/wissenschaft/mensch/corona-krise-und-klimawandel-fuenf" \
                          "-desinformations-tricks-die-jeder-kennen-sollte-a-6892ff9b-fb28-43ae-8438-55b49d607e57" \
                          "?sara_ecid=soci_upd_wbMbjhOSvViISjc8RPU89NcCvtlFcJ '"
        assert urls[1] == "https://www.spiegel.de/wissenschaft/mensch/corona-krise-und-klimawandel-fuenf" \
                          "-desinformations-tricks-die-jeder-kennen-sollte-a-6892ff9b-fb28-43ae-8438-55b49d607e57" \
                          "?sara_ecid=soci_upd_wbMbjhOSvViISjc8RPU89NcCvtlFcJ"
        assert titles[1] == "Corona-Krise und Klimawandel: Fünf Desinformations-Tricks, die jeder kennen sollte - " \
                            "DER SPIEGEL"
        assert text[1] == "US-Präsident Donald Trump, Fachmann für Falschinformation Haben Sie auch solche " \
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
                          "Paläoklimaforschung, Veränderungen von Meeresströmungen und Meeresspiegel sowie " \
                          "Wetterextreme. Diese fünf Tricks wurden 2009 in einem Aufsatz von Pascal Diethelm " \
                          "und Martin McKee in der wissenschaftlichen Zeitschrift \"European Journal of " \
                          "Public Health\" " \
                          "beschrieben, und mit etwas Übung kann sie auch ein Laie durchschauen. Das griffige " \
                          "Schlagwort für die fünf Tricks lautet PLURV. Diese Abkürzung steht für: Um eine " \
                          "Gegenthese zum etablierten Wissensstand zu lancieren, werden oft Pseudoexperten " \
                          "aufgeboten. Die haben keine eigenen relevanten Forschungsleistungen vorzuweisen, " \
                          "vorzugsweise aber Professorentitel oder Ähnliches, was für den Laien nach " \
                          "Kompetenz klingt. Häufig allerdings sind sie keine Experten in dem Fachgebiet, " \
                          "zu dem sie sich äußern. Nicht selten handelt es sich um lange pensionierte Herren. " \
                          "Das kann bedeuten, dass sie sich nicht mehr mit der Forschung beschäftigen und " \
                          "nicht auf dem aktuellen Stand sind. Durch Wissenschaftsdatenbanken wie Scopus oder " \
                          "Web of Science ist leicht ersichtlich, wer ernsthaft zu einem Thema forscht. " \
                          "Kostenfrei für jeden zugänglich ist Google Scholar. Dort sieht man sofort, " \
                          "dass Christian Drosten Hunderte Fachpublikationen in der Virologie hat, " \
                          "die Zehntausende Male von anderen Studien zitiert wurden - viele davon zu " \
                          "Coronaviren. Von Wolfgang Wodarg, der jede Gefahr durch das neue Coronavirus " \
                          "bestritten hat, findet Google Scholar zwar einige Meinungsbeiträge, aber keine " \
                          "relevante Forschungsarbeit. Am 31. Dezember wandte sich China erstmals an die " \
                          "Weltgesundheitsorganisation (WHO). In der Millionenstadt Wuhan häuften sich Fälle " \
                          "einer rätselhaften Lungenentzündung. Mittlerweile sind mehr als sieben Millionen " \
                          "Menschen weltweit nachweislich erkrankt, die Situation ändert sich von Tag zu Tag. " \
                          "Auf dieser Seite finden Sie einen Überblick über alle SPIEGEL-Artikel zum Thema. " \
                          "Ein Beispiel: \"In Deutschland sind nur 8500 Menschen mit Corona gestorben - daher " \
                          "waren die Gegenmaßnahmen unnötig oder mindestens überzogen.\"\xa0Umgekehrt wird " \
                          "ein Schuh daraus: Dank der Maßnahmen sind relativ wenige Menschen gestorben. " \
                          "Einige Länder haben weniger gut reagiert. Das von einem Wissenschaftsleugner " \
                          "regierte Brasilien überholt gerade die USA bei Neuinfektionen. Und Schweden, " \
                          "das auf freiwillige Maßnahmen setzte, ist inzwischen Weltspitze bei den täglichen " \
                          "Todesfällen pro Einwohner. Einer der klassischen Logikfehler beim Klimawandel " \
                          "ist die These, das Klima habe sich schon immer geändert, also sei der Mensch nicht " \
                          "schuld. Das ist so, als fände man eine Leiche mit einem Messer im Rücken und würde " \
                          "argumentieren, Menschen würden von Natur aus sterben, also sei dies kein Mord. Die " \
                          "Ursache der modernen globalen Erwärmung ist zweifelsfrei nachgewiesen. Zweifler " \
                          "fordern gern unmögliche Beweise - etwa, dass bei den Toten mit Corona bewiesen " \
                          "werden muss, dass sie nicht nur mit, sondern auch an dem Coronavirus gestorben " \
                          "sind. Oder den experimentellen Nachweis, dass die globale Erwärmung durch den " \
                          "CO2-Anstieg verursacht wird. Die Grundlage - dass CO2 langwellige Strahlung " \
                          "einfängt - ist freilich seit 1869 experimentell im Labor bewiesen, aber das reicht " \
                          "den Leugnern nicht. Ein Experiment mit der ganzen Erde muss her. Das kann man " \
                          "freilich nur einmal durchführen - wir stecken gerade mittendrin und sind die " \
                          "Versuchskaninchen. Gute Wissenschaftler wollen die Welt verstehen - und wägen " \
                          "dazu alle verfügbaren Informationen kritisch ab. Ideologen wollen ihre vorgefasste " \
                          "Meinung bestätigen, picken sich dazu die passenden Daten heraus und übersehen " \
                          "geflissentlich einen Berg gegenläufiger Belege. Wer die Coronakrise verharmlosen " \
                          "will, sucht sich einige Studien heraus, die eine möglichst geringe Sterblichkeit " \
                          "der Infizierten ergeben - was an zu kleinen oder nicht repräsentativen Stichproben " \
                          "oder an unzuverlässigen Tests liegen kann. Sie übersehen viele andere Studien und " \
                          "das, was an den Orten geschah, wo Corona sich stark verbreitet hat. In New York " \
                          "City starben 0,25 Prozent an Corona - und zwar der Gesamtbevölkerung, " \
                          "nicht der Infizierten. Die Sterberate unter den Infizierten liegt nach aktuellem " \
                          "Forschungsstand aus verschiedenen Ländern zwischen einem halben und einem Prozent. " \
                          "Selbst für ganze Länder sticht die Coronakrise in der Gesamtsterblichkeit heraus; " \
                          "in Frankreich wird die Höhe des Corona-Peaks in den letzten 50 Jahren nur durch " \
                          "die Hitzewelle 2003 übertroffen. Auch diese Rosinenpickerei kennt jeder " \
                          "Klimaforscher - mal kühlt die Erde sich angeblich ab, mal sinkt der Meeresspiegel " \
                          "(Björn Lomborg), oder es gibt einen Rekordzuwachs an Polareis (nämlich wenn im " \
                          "Winter in der Polarnacht der arktische Ozean wieder zufriert, nach einem " \
                          "Rekordminimum im Sommer). Oder es gibt gerade kaltes Wetter dort, wo man wohnt. Um " \
                          "wahr zu sein, würden viele Fake-Geschichten eine atemberaubende Inkompetenz von " \
                          "Wissenschaftlern erfordern. Doch natürlich können professionelle Virologen Viren " \
                          "von Bakterien unterscheiden. Und ja - professionelle Klimaforscher wissen, " \
                          "dass das Klima sich schon vor dem Einfluss des Menschen geändert hat. " \
                          "Klimaforscher haben das selbst detailliert dokumentiert und benutzen die " \
                          "natürlichen Klimaveränderungen schon seit Jahrzehnten, um Modelle zu testen und um " \
                          "die Empfindlichkeit des Klimas gegenüber Störungen zu quantifizieren. Da " \
                          "Wissenschaftler wohl kaum so inkompetent sein können, wird eine große Verschwörung " \
                          "der Forscher behauptet, die gezielt Daten fälschen und die Öffentlichkeit " \
                          "täuschen. Allerdings würde es sich dabei um eine extrem große, internationale " \
                          "Verschwörung handeln, deren wasserdichte Organisation ziemlich unmöglich ist. Zum " \
                          "Stichwort \"Klimawandel\" etwa erscheinen jährlich über 20.000 Studien in der " \
                          "Fachliteratur, von Forschern aller Kulturen und politischen Vorlieben, die nichts " \
                          "lieber täten, als etwas sensationell Neues, Anderes belegen zu können als den " \
                          "langweiligen \"Mainstream\". Wer sich unsicher ist, was von Außenseiterthesen zu " \
                          "halten ist, dem helfen die Webportale sciencefeedback.co (sowohl zu Klima als auch " \
                          "Gesundheit) sowie klimafakten.de und skepticalscience.com (nur zum Klima). Doch " \
                          "nicht nur die PLURV-Methode gleicht sich - es sind auch häufig dieselben Leute, " \
                          "die Corona- und Klimakrise herunterspielen. Angefangen mit Donald Trump, " \
                          "der in beiden Fällen die gleichen Argumente verwendet hat, von \"Es ist ein " \
                          "Scherz\" bis \"China ist schuld\", wie diese schöne Videozusammenstellung seiner " \
                          "Aussagen zeigt: An dieser Stelle finden Sie einen externen Inhalt von " \
                          "YouTube, der den Artikel ergänzt. Sie können ihn sich mit einem Klick anzeigen " \
                          "lassen und wieder ausblenden. \nIch bin damit einverstanden, dass mir externe " \
                          "Inhalte angezeigt werden. Damit können personenbezogene Daten an Drittplattformen " \
                          "übermittelt werden.\n\nMehr dazu in unserer Datenschutzerklärung.\n\n" \
                          " In den USA sind weitere Beispiele Alex Jones von Infowars und Thinktanks wie das " \
                          "Heartland Institute, in Australien der Kolumnist Andrew Bolt, in Europa Björn " \
                          "Lomborg und die vorwiegend aus älteren Herren bestehende Gruppe, " \
                          "die sich etikettenschwindlerisch \"Europäisches Institut für Klima und Energie (" \
                          "EIKE)\" nennt, aber freimütig bekennt \"wir brauchen keine Klimaforscher\". Die " \
                          "Behauptungen dieser Menschen und Organisationen haben offensichtlich mehr mit " \
                          "deren Weltanschauung - häufig mit der starken Abneigung gegenüber staatlichen " \
                          "Maßnahmen wie Klimaschutz oder der Corona-Prävention - zu tun, als mit einer " \
                          "Wissenschaftsdebatte. Es sind Menschen, die sich lieber durch Wunschdenken leiten " \
                          "lassen, als mutig und nüchtern auch einer unerfreulichen Realität ins Auge zu " \
                          "blicken. __localized_intro__ __localized_unblockIntro__ \n" \
                          "__localized_unblockInstructions:0__\n" \
                          "__localized_unblockInstructions:1____localized_unblockInstructions:2__\n " \
                          "__localized_purIntro__ __localized_purIntroApp__ \n" \
                          "__localized_purDetailsAppText:0__\n" \
                          "__localized_purDetailsAppText:1____localized_purDetailsAppText:2__\n " \
                          "__localized_purLoginAppText:0____localized_purLoginAppText" \
                          ":1____localized_purLoginAppText:2__\n " \
                          "__localized_purLogoutAppText:0____localized_purLogoutAppText" \
                          ":1____localized_purLogoutAppText:2__\n \n__localized_itunesTerms:0__\n" \
                          "__localized_itunesTerms:1__\n\n__localized_itunesTerms:2__\n" \
                          "__localized_itunesTerms:3__\n__localized_itunesTerms:4__\n US-Präsident " \
                          "Donald Trump, Fachmann für Falschinformation Melden Sie sich an und diskutieren " \
                          "Sie mit "
