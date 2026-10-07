from __future__ import annotations

import io
import pandas as pd

from shared.gateway import (
    get_sample_wellness_csv,
    predict_realtime_sample,
    retrain_model,
    upload_dataset,
)


def test_get_sample_wellness_csv(isolated_env):
    csv_str = get_sample_wellness_csv()
    assert isinstance(csv_str, str)
    assert len(csv_str) > 100
    df = pd.read_csv(io.StringIO(csv_str))
    assert len(df) == 100
    assert "mood_score" in df.columns
    assert "risk_level" in df.columns


def test_upload_and_validate_custom_dataset(isolated_env):
    custom_df = pd.DataFrame({
        "mood": [1, 2, 4, 5, 3],
        "stress": [9, 8, 2, 1, 5],
        "energy": [2, 3, 8, 9, 6],
        "sleep": [4.0, 5.0, 8.0, 8.5, 7.0],
        "text": [
            "I feel exhausted and terrible",
            "Very stressed about exams",
            "Great day today",
            "Feeling happy and energetic",
            "Normal day",
        ],
    })
    csv_bytes = custom_df.to_csv(index=False).encode("utf-8")

    result = upload_dataset(csv_bytes, "custom_test.csv")
    assert result["filename"] == "custom_test.csv"
    assert result["profile"]["total_rows"] == 5
    assert len(result["preview"]) == 5
    # Verify auto-repaired fields
    repaired = result["profile"]["repaired_columns"]
    assert any("compound" in s for s in repaired)
    assert any("risk_level" in s for s in repaired)


def test_retrain_model_with_custom_dataset(isolated_env):
    sample_csv = get_sample_wellness_csv()
    retrain_res = retrain_model(sample_csv, "sample_benchmark.csv")

    assert retrain_res["selected_model"] in {"Logistic Regression", "Random Forest"}
    assert retrain_res["test_accuracy"] >= 0.0
    assert "confusion_matrix" in retrain_res
    assert "classification_report" in retrain_res
    assert retrain_res["dataset_profile"]["source"] == "sample_benchmark.csv"


def test_predict_realtime_sample(isolated_env):
    sample = {
        "mood_score": 1,
        "stress_score": 9,
        "energy_score": 2,
        "sleep_hours": 4.0,
        "attendance_rate": 65.0,
        "assignments_due": 5,
        "social_connectedness": 1,
        "exam_pressure": 9,
        "compound": -0.8,
    }

    pred = predict_realtime_sample(sample)
    assert pred["label"] in {"Stressed", "High Risk"}
    assert pred["risk_score"] > 50.0
    assert "model_confidence" in pred
    assert "timestamp" in pred


def test_dataset_rest_endpoints(isolated_env):
    from backend import create_app

    app = create_app()
    client = app.test_client()

    # Test sample GET endpoint
    res_sample = client.get("/api/dataset/sample")
    assert res_sample.status_code == 200
    assert "csv" in res_sample.get_json()

    # Test upload POST endpoint
    sample_csv = res_sample.get_json()["csv"]
    res_upload = client.post("/api/dataset/upload", json={"content": sample_csv, "filename": "test.csv"})
    assert res_upload.status_code == 200
    assert res_upload.get_json()["profile"]["total_rows"] == 100

    # Test retrain POST endpoint
    res_retrain = client.post("/api/dataset/retrain", json={"content": sample_csv, "filename": "test.csv"})
    assert res_retrain.status_code == 200
    assert "test_accuracy" in res_retrain.get_json()

    # Test realtime predict POST endpoint
    res_pred = client.post("/api/realtime/predict", json={"mood_score": 5, "stress_score": 1})
    assert res_pred.status_code == 200
    assert res_pred.get_json()["label"] == "Normal"
