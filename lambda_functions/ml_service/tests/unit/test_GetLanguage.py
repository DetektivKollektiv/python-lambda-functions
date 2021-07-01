from ml_service import GetLanguage
import pytest


class TestGetLanguage:
    def test_get_language_1(self):
        event = {
            "Text": "Wenn Sie eine laufende Nase und einen Auswurf in Ihrer Erkältung haben, können Sie keine neue "
                    "Art von Coronavirus-Pneumonie haben, da Coronavirus-Pneumonie ein trockener Husten ohne laufende "
                    "Nase ist. "
        }
        context = ""
        ret = GetLanguage.get_language(event, context)
        assert ret == "de"

    def test_get_language_2(self):
        event = {
            "Text": "At the university hospital in Toulouse, France, there are four very critical cases of "
                    "coronavirus in [young people] who do not have any health problems. Their problem is that when "
                    "they all appeared to have symptoms, they all took painkillers like ibuprofen "
        }
        context = ""
        ret = GetLanguage.get_language(event, context)
        assert ret == "en"

    def test_get_language_3(self):
        event = {
            "Text": "Eine Freundin von mir ist an der Uniklinik in Wien. Sie haben mal ein bisschen Forschung "
                    "betrieben, warum in Italien so viele heftige Corona-Fälle aufgetreten sind. Sie haben "
                    "festgestellt, dass die Leute, die mit schweren Symptomen in die Klinik eingeliefert worden sind, "
                    "mehr oder weniger alle daheim Ibuprofen vorher genommen hatten. At the university hospital in "
                    "Toulouse, France, there are four very critical cases of coronavirus in [young people] who do not "
                    "have any health problems. Their problem is that when they all appeared to have symptoms, "
                    "they all took painkillers like ibuprofen."
        }
        context = ""
        ret = GetLanguage.get_language(event, context)
        assert ret == "de"

    def test_get_language_4(self):
        event = {
            "Text": "At the university hospital in Toulouse, France, there are four very critical cases of "
                    "coronavirus in [young people] who do not have any health problems. Their problem is that when "
                    "they all appeared to have symptoms, they all took painkillers like ibuprofen. Sie haben "
                    "festgestellt, dass die Leute alle daheim Ibuprofen vorher genommen hatten. "
        }
        context = ""
        ret = GetLanguage.get_language(event, context)
        assert ret == "en"

    def test_get_language_5(self):
        event = {
            "Text": ""
        }
        context = ""
        with pytest.raises(Exception) as excinfo:
            GetLanguage.get_language(event, context)
        assert "Please provide a text of at least 20 characters!" in str(
            excinfo.value)

    def test_get_language_6(self):
        event = {
            "Test": "Wenn Sie eine laufende Nase und einen Auswurf in Ihrer Erkältung haben, können Sie keine neue "
                    "Art von Coronavirus-Pneumonie haben, da Coronavirus-Pneumonie ein trockener Husten ohne laufende "
                    "Nase ist. "
        }
        context = ""
        with pytest.raises(Exception) as excinfo:
            GetLanguage.get_language(event, context)
        assert "Please provide Text!" in str(excinfo.value)

    def test_get_language_7(self):
        event = {
            "Text": "asdfjbjkriisdfbkncblsrgiuqütqweorqwelöjadklfnlkdnfdfgeirtqerojakjaldknv,dnf,amdnfgakdgjqieuterjga"
        }
        context = ""
        ret = GetLanguage.get_language(event, context)
        assert ret != "en"
        assert ret != "de"

    def test_get_language_8(self):
        event = {
            "Text": "https://www.compact-online.de/die-vergessenen-corona-opfer-jugend-psychiatrien-melden-rekordansturm/"
        }
        context = ""
        ret = GetLanguage.get_language(event, context)
        assert ret != ""

    def test_get_language_9(self):
        event = {
            "Text": "Min. viermal krabbeln einem im Jahr Spinnen in den Mund während man schläft. Hab ich gehört. :-)"
        }
        context = ""
        ret = GetLanguage.get_language(event, context)
        assert ret == "de"

    def test_get_language_10(self):
        event = {
            "Text": "@Alice_Weidel Feb 18 \"50.000 Grenzkontrollen, 10.000 Zurückweisungen: #Seehofer ist stolz auf seine Lockdown-Kontrollbilanz an den Außengrenzen. Zur Erinnerung: Wir haben derzeit 359.000 Migranten ohne Bleiberecht im Land, weil die Grenzen seit 2015 angeblich nicht kontrolliert werden konnten! #AfD"
        }
        context = ""
        ret = GetLanguage.get_language(event, context)
        assert ret == "de"
