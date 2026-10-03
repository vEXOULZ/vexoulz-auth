from __future__ import annotations

from tests.conftest import BOB, Harness
from vexoulz_auth.app import CSRF_HEADER

ENTRY = {"t": 1, "duration": 9, "updatedAt": 1}


async def headers(h: Harness) -> dict[str, str]:
    return {CSRF_HEADER: (await h.me()).json()["csrf"]}


async def test_put_get_list_delete(h: Harness) -> None:
    await h.sign_in()
    hd = await headers(h)
    resp = await h.http.put("/v1/progress/v1", headers=hd, json={"t": 120.5, "duration": 3600, "updatedAt": 1000})
    assert resp.json() == {"vodId": "v1", "t": 120.5, "duration": 3600, "updatedAt": 1000}
    await h.http.put("/v1/progress/v2", headers=hd, json={"t": 5, "duration": 60, "updatedAt": 2000})
    assert (await h.http.get("/v1/progress/v1")).json()["t"] == 120.5
    items = (await h.http.get("/v1/progress")).json()["items"]
    assert [i["vodId"] for i in items] == ["v2", "v1"]  # newest first
    assert [i["vodId"] for i in (await h.http.get("/v1/progress?limit=1")).json()["items"]] == ["v2"]
    assert (await h.http.delete("/v1/progress/v1", headers=hd)).status_code == 204
    assert (await h.http.get("/v1/progress/v1")).status_code == 404


async def test_newest_wins(h: Harness) -> None:
    await h.sign_in()
    hd = await headers(h)
    await h.http.put("/v1/progress/v1", headers=hd, json={"t": 500, "duration": 900, "updatedAt": 2000})
    stale = await h.http.put("/v1/progress/v1", headers=hd, json={"t": 10, "duration": 900, "updatedAt": 1000})
    assert stale.json()["t"] == 500


async def test_merge_imports_local_progress(h: Harness) -> None:
    await h.sign_in()
    hd = await headers(h)
    await h.http.put("/v1/progress/v1", headers=hd, json={"t": 500, "duration": 900, "updatedAt": 2000})
    items = [
        {"vodId": "v1", "t": 1, "duration": 900, "updatedAt": 1000},  # older than the account's: loses
        {"vodId": "v2", "t": 2, "duration": 900, "updatedAt": 3000},
    ]
    resp = await h.http.post("/v1/progress/merge", headers=hd, json={"items": items})
    got = {i["vodId"]: i["t"] for i in resp.json()["items"]}
    assert got == {"v1": 500, "v2": 2}


async def test_progress_is_per_user(h: Harness) -> None:
    await h.sign_in()
    await h.http.put("/v1/progress/v1", headers=await headers(h), json=ENTRY)
    await h.sign_in(BOB)
    assert (await h.http.get("/v1/progress")).json() == {"items": []}
    assert (await h.http.get("/v1/progress/v1")).status_code == 404


async def test_writes_need_a_session_and_csrf(h: Harness) -> None:
    assert (await h.http.put("/v1/progress/v1", json=ENTRY)).status_code == 401
    assert (await h.http.get("/v1/progress")).status_code == 401
    await h.sign_in()
    assert (await h.http.put("/v1/progress/v1", json=ENTRY)).status_code == 403
    assert (await h.http.delete("/v1/progress/v1", headers={CSRF_HEADER: "wrong"})).status_code == 403
    assert (await h.http.post("/v1/progress/merge", json={"items": []})).status_code == 403


async def test_bad_progress_is_refused(h: Harness) -> None:
    await h.sign_in()
    hd = await headers(h)
    for bad in ({"t": -1, "duration": 9, "updatedAt": 1}, {"t": 1, "updatedAt": 1}, {"t": "x"}):
        assert (await h.http.put("/v1/progress/v1", headers=hd, json=bad)).status_code == 422
    assert (await h.http.put("/v1/progress/bad%20id", headers=hd, json=ENTRY)).status_code == 422
    too_many = [{"vodId": f"v{i}", **ENTRY} for i in range(501)]
    assert (await h.http.post("/v1/progress/merge", headers=hd, json={"items": too_many})).status_code == 422
