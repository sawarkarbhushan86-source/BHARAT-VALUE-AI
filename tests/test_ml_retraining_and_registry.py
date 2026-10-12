"""Tests for ML Retraining Pipeline, Validation Gates, and Model Registry Rollback."""
import pytest
from bharat_value_ai.ml.registry import model_registry
from bharat_value_ai.ml.pipeline import ml_ranking_lab


def test_model_registry_gates_enforcement():
    """Verify registry gates reject models with insufficient sample size or weak rank correlation."""
    # Attempt 1: Too few samples (< 40)
    res_small = model_registry.register_candidate_model(
        version="v_small_test",
        spearman_rho=0.40,
        top_quintile_return=5.0,
        sample_size=15,
        feature_names=["pe", "roce"],
        train_window="2022Q1-2023Q1",
        test_window="2023Q2-2023Q4",
        metrics={"test_spearman_rho": 0.40}
    )
    assert res_small["promoted"] is False
    assert res_small["model_entry"]["status"] == "REJECTED_GATE_FAILURE"
    assert any("sample size" in r for r in res_small["model_entry"]["gate_rejection_reasons"])

    # Attempt 2: Negative or weak Spearman correlation (< 0.05)
    res_weak = model_registry.register_candidate_model(
        version="v_weak_test",
        spearman_rho=-0.10,
        top_quintile_return=2.0,
        sample_size=50,
        feature_names=["pe", "roce"],
        train_window="2022Q1-2023Q1",
        test_window="2023Q2-2023Q4",
        metrics={"test_spearman_rho": -0.10}
    )
    assert res_weak["promoted"] is False
    assert any("Spearman" in r for r in res_weak["model_entry"]["gate_rejection_reasons"])

    # Attempt 3: Valid model meeting all gates
    res_valid = model_registry.register_candidate_model(
        version="v_valid_gate_pass",
        spearman_rho=0.35,
        top_quintile_return=8.5,
        sample_size=50,
        feature_names=["pe", "roce"],
        train_window="2022Q1-2023Q1",
        test_window="2023Q2-2023Q4",
        metrics={"test_spearman_rho": 0.35}
    )
    assert res_valid["promoted"] is True
    assert model_registry.get_active_model_info()["version"] == "v_valid_gate_pass"


def test_model_registry_rollback():
    """Verify rollback restores previous validated model version."""
    # Ensure active version has a known previous version
    model_registry.data["previous_version"] = "v2.1-Audited"
    rb_res = model_registry.rollback()
    assert rb_res["status"] == "SUCCESS"
    assert rb_res["current_active"] == "v2.1-Audited"
    assert model_registry.get_active_model_info()["version"] == "v2.1-Audited"


def test_ml_pipeline_train_and_rank_universe():
    """Verify ML pipeline trains across broad active universe and computes institutional factors."""
    response = ml_ranking_lab.train_and_rank()

    assert response.model_version is not None
    assert response.benchmark_name == "NIFTY SMALLCAP 100"
    assert len(response.top_ranked) > 0
    assert response.spearman_rank_correlation is not None

    # Check baseline comparison
    assert response.baseline_comparison is not None
    assert "ridge_linear_spearman_rho" in response.baseline_comparison
    assert "heuristic_quality_spearman_rho" in response.baseline_comparison

    # Check top-k performance and execution drag
    assert response.top_k_performance is not None
    assert "friction_cost_deduction_pct" in response.top_k_performance
    assert "top_quintile_annualized_return_pct" in response.top_k_performance

    # Check features and coverage
    assert len(response.feature_importance) >= 10
    assert "roce_pct" in response.feature_importance
    assert "pe_ratio" in response.feature_importance
    assert "debt_to_equity" in response.feature_importance
