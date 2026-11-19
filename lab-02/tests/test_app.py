import app

HTTP_OK = 200
HTTP_BAD_GATEWAY = 502
HTTP_UNAVAILABLE = 503

HEALTH_BODY = b"ok\n"
FILE_STORE_PREFIX = "file:"
FILE_STORE = "file"
FIRST_VISIT = 1
SECOND_VISIT = 2
UNREACHABLE_DATABASE_URL = "postgresql://nobody@127.0.0.1:1/none"

SKU = "MK-II"
PRICE = 1999
CURRENCY = "UAH"
PARTNER_ANSWER = {"price": PRICE, "currency": CURRENCY}
DEAD_PARTNER_HOST = "127.0.0.1:9"
DEAD_PARTNER_URL = f"http://{DEAD_PARTNER_HOST}"
SHORT_TIMEOUT = 0.25


class FakePartnerResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return PARTNER_ANSWER


def test_health_says_ok(client):
    response = client.get("/health")
    assert response.status_code == HTTP_OK
    assert response.data == HEALTH_BODY


def test_ready_reports_file_store(client):
    response = client.get("/ready")
    assert response.status_code == HTTP_OK
    assert response.json["ready"] is True
    assert response.json["store"].startswith(FILE_STORE_PREFIX)


def test_ready_is_503_when_db_is_unreachable(client, monkeypatch):
    monkeypatch.setattr(app, "DATABASE_URL", UNREACHABLE_DATABASE_URL)
    response = client.get("/ready")
    assert response.status_code == HTTP_UNAVAILABLE
    assert response.json["ready"] is False


def test_visits_counts_from_one(client):
    first = client.get("/visits")
    second = client.get("/visits")
    assert first.json["visits"] == FIRST_VISIT
    assert second.json["visits"] == SECOND_VISIT
    assert second.json["store"] == FILE_STORE


def test_price_uses_partner_answer(client, monkeypatch):
    monkeypatch.setattr(app.requests, "get", lambda *args, **kwargs: FakePartnerResponse())
    response = client.get(f"/price/{SKU}")
    assert response.status_code == HTTP_OK
    assert response.json["price"] == PRICE
    assert response.json["currency"] == CURRENCY
    assert response.json["sku"] == SKU


def test_price_is_502_when_partner_is_down(client, monkeypatch):
    monkeypatch.setattr(app, "PARTNER_URL", DEAD_PARTNER_URL)
    monkeypatch.setattr(app, "PARTNER_TIMEOUT", SHORT_TIMEOUT)
    response = client.get(f"/price/{SKU}")
    assert response.status_code == HTTP_BAD_GATEWAY
    assert response.json["sku"] == SKU
    assert DEAD_PARTNER_HOST in response.json["source"]
