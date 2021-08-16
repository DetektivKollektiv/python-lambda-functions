from core_layer.handler import url_threatcheck

def test_safe_item():
    result = url_threatcheck.threatcheck("https://codetekt.org")
    assert result is None

def test_unsafe_malware_item():
    result = url_threatcheck.threatcheck("http://testsafebrowsing.appspot.com/s/malware.html")
    assert result == "GOOGLE:MALWARE"

def test_unsafe_phishing_item():
    result = url_threatcheck.threatcheck("http://testsafebrowsing.appspot.com/s/phishing.html")
    assert result == "GOOGLE:SOCIAL_ENGINEERING"

def test_with_no_url_item():
    result = url_threatcheck.threatcheck("")
    assert result == "GOOGLE:N/A"

def test_with_not_valid_url_item():
    result = url_threatcheck.threatcheck("blabla")
    assert result is None
