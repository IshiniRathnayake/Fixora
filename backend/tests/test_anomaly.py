import numpy as np
import pandas as pd

from app.services.anomaly import AnomalyDetectionService
from app.services.log_parser import LogParserService


def test_isolation_forest_detects_errors():
    df = pd.DataFrame(
        {
            "level": ["INFO"] * 20 + ["ERROR"] * 3,
            "message": ["ok"] * 20 + ["deadlock detected"] * 3,
            "template_id": ["1"] * 20 + ["99"] * 3,
        }
    )
    features = LogParserService.build_feature_matrix(df)
    detector = AnomalyDetectionService(contamination=0.1)
    is_anomaly, _ = detector.fit_detect(features)
    assert is_anomaly.sum() >= 1


def test_rule_baseline():
    df = pd.DataFrame({"level": ["INFO", "ERROR"], "message": ["a", "b"]})
    mask = AnomalyDetectionService.rule_based_baseline(df)
    assert mask[1]
