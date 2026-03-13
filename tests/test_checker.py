from checker import check_service

def test_retorna_campos_correctos():
    """
    Verifica que check_service siempre devuelve
    un diccionario con las claves esperadas.
    """
    result = check_service("https://google.com")

    assert "url"      in result, "Falta el campo url"
    assert "status"   in result, "Falta el campo status"
    assert "response_time" in result, "Falta el campo latencia"
    assert "error"    in result, "Falta el campo error"


def test_sitio_ok():
    """
    Google debería responder sin error.
    """
    result = check_service("https://google.com")

    assert result["error"] is None
    assert result["status"] is not None
    assert result["response_time"] > 0


def test_sitio_inexistente():
    """
    Un sitio que no existe debería devolver error,
    no lanzar una excepción que rompa el programa.
    """
    result = check_service("https://sitioquenexiste123abc.com")

    assert result["error"] is not None
    assert result["status"] is None
    assert result["response_time"] is None


def test_url_se_preserva():
    """
    La URL devuelta debe ser exactamente la que se pasó.
    """
    url = "https://github.com"
    result = check_service(url)

    assert result["url"] == url