# DEPRECATED: This test file is no longer in use as of the multi-tenant refactor (August 2025).
# All budget sharing logic has been removed from the codebase.
        "/api/budgets/share",
        params={"budget_id": budget_id, "user_id": 2, "can_write": True},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 200, resp.text
    resp = client.post(
        "/api/budgets/share",
        params={"budget_id": budget_id, "user_id": 3, "can_write": False},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 200, resp.text

    # Owner, USER2 (write), USER3 (read) list budgets
    for token in [owner_token, shared_token, readonly_token]:
        resp = client.get("/api/budgets/", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200, resp.text
        names = [b["name"] for b in resp.json()]
        assert "Shared Budget" in names

    # Owner can add category
    resp = client.post(
        "/api/categories/",
        json={"name": "OwnerCat", "budget_id": budget_id},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 200, resp.text
    owner_cat_id = resp.json()["id"]

    # USER2 (write) can add category
    resp = client.post(
        "/api/categories/",
        json={"name": "SharedCat", "budget_id": budget_id},
        headers={"Authorization": f"Bearer {shared_token}"},
    )
    assert resp.status_code == 200, resp.text
    shared_cat_id = resp.json()["id"]

    # USER3 (read only) cannot add category
    resp = client.post(
        "/api/categories/",
        json={"name": "ReadCat", "budget_id": budget_id},
        headers={"Authorization": f"Bearer {readonly_token}"},
    )
    assert resp.status_code == 403

    # Owner can add transaction to own category
    txn = {"amount": 10, "note": "OwnerTxn", "category_id": owner_cat_id}
    resp = client.post(
        "/api/transactions/",
        json=txn,
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 200, resp.text

    # USER2 (write) can add transaction to shared category
    txn = {"amount": 20, "note": "SharedTxn", "category_id": shared_cat_id}
    resp = client.post(
        "/api/transactions/",
        json=txn,
        headers={"Authorization": f"Bearer {shared_token}"},
    )
    assert resp.status_code == 200, resp.text

    # USER3 (read only) cannot add transaction
    txn = {"amount": 30, "note": "ReadTxn", "category_id": owner_cat_id}
    resp = client.post(
        "/api/transactions/",
        json=txn,
        headers={"Authorization": f"Bearer {readonly_token}"},
    )
    assert resp.status_code == 403
