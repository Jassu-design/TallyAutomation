import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_api_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Bank-to-TallyPrime" in data["service"]

def test_api_dashboard_summary(client):

    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "tally_status" in data
    assert "attention" in data

def test_api_mappings_list_and_test(client):
    response = client.get("/api/mappings")
    assert response.status_code == 200
    mappings = response.json()
    assert len(mappings) > 0
    assert any(m["keyword"] == "AMAZON" for m in mappings)

    # Test preview match
    test_req = {
        "description": "UPI/AMAZON PAY SELLER",
        "transaction_type": "DEBIT"
    }
    test_res = client.post("/api/mappings/test", json=test_req)
    assert test_res.status_code == 200
    test_data = test_res.json()
    assert test_data["matched"] is True
    assert test_data["suggested_ledger"] == "Amazon Expenses"

def test_api_tally_status(client):
    response = client.get("/api/tally/status")
    assert response.status_code == 200
    status = response.json()
    assert "connected" in status

def test_api_upload_sample_statement(client):

    sample_file_path = "C:/Users/hp/.gemini/antigravity/scratch/bank-tally-automation/data/sample_bank_statements/hdfc_oct_sample.csv"
    with open(sample_file_path, "rb") as f:
        response = client.post(
            "/api/bank/upload",
            files={"file": ("hdfc_oct_sample.csv", f, "text/csv")},
            data={"bank": "HDFC Bank", "company": "ABC Pvt Ltd"}
        )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["summary"]["total_transactions"] == 15
    batch_id = res_data["batch_id"]

    # Verify transactions are in database
    txns_res = client.get(f"/api/transactions?import_id={batch_id}")
    assert txns_res.status_code == 200
    txns = txns_res.json()
    assert txns["total"] == 15

    # Check that duplicates are detected if re-uploaded
    with open(sample_file_path, "rb") as f:
        reupload_res = client.post(
            "/api/bank/upload",
            files={"file": ("hdfc_oct_sample.csv", f, "text/csv")},
            data={"bank": "HDFC Bank", "company": "ABC Pvt Ltd"}
        )
    assert reupload_res.status_code == 200
    reupload_data = reupload_res.json()
    # All 15 transactions should now be detected as duplicates!
    assert reupload_data["summary"]["duplicates"] == 15

def test_api_upload_sample_pdf(client):
    pdf_path = "C:/Users/hp/.gemini/antigravity/scratch/bank-tally-automation/data/sample_bank_statements/demo_bank_statement.pdf"
    with open(pdf_path, "rb") as f:
        response = client.post(
            "/api/bank/upload",
            files={"file": ("demo_bank_statement.pdf", f, "application/pdf")},
            data={"bank": "HDFC Bank", "company": "ABC Pvt Ltd"}
        )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["summary"]["total_transactions"] == 10
    assert res_data["bank_name"] == "HDFC Bank"

def test_api_sample_pdf_endpoint(client):
    response = client.post("/api/bank/sample-pdf")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["summary"]["total_transactions"] == 10

