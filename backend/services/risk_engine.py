from __future__ import annotations

import io
from dataclasses import asdict
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from backend.services.nlp_engine import analyze_text



FEATURE_COLUMNS = [
    "mood_score",
    "stress_score",
    "energy_score",
    "sleep_hours",
    "attendance_rate",
    "assignments_due",
    "social_connectedness",
    "exam_pressure",
    "compound",
]

LABEL_ORDER = {"Normal": 0, "Stressed": 1, "High Risk": 2}
SIMULATED_DATASET_NAME = "Simulated student wellness dataset"


class RiskEngine:
    def __init__(self) -> None:
        self.reset_to_default_dataset()

    def reset_to_default_dataset(self) -> None:
        artifact = self._train_model()
        self.model = artifact["model"]
        self.model_classes = artifact["classes"]
        self.selected_model = artifact["selected_model"]
        self.models_tested = artifact["models_tested"]
        self.dataset_profile = artifact["dataset"]
        self.preprocessing_steps = artifact["preprocessing"]


    def _build_training_dataset(
        self,
        samples: int = 1800,
        random_state: int = 42,
    ) -> tuple[pd.DataFrame, pd.Series]:
        rng = np.random.default_rng(random_state)

        academic_pressure = rng.normal(loc=0.0, scale=1.0, size=samples)
        recovery_buffer = rng.normal(loc=0.0, scale=0.8, size=samples)

        dataset = pd.DataFrame(
            {
                "mood_score": np.clip(
                    np.rint(
                        3.5 - 0.9 * academic_pressure + 0.55 * recovery_buffer + rng.normal(0, 0.7, samples)
                    ),
                    1,
                    5,
                ).astype(int),
                "stress_score": np.clip(
                    np.rint(
                        5.3 + 1.9 * academic_pressure - 0.25 * recovery_buffer + rng.normal(0, 1.1, samples)
                    ),
                    1,
                    10,
                ).astype(int),
                "energy_score": np.clip(
                    np.rint(
                        6.2 - 1.25 * academic_pressure + 0.7 * recovery_buffer + rng.normal(0, 1.1, samples)
                    ),
                    1,
                    10,
                ).astype(int),
                "sleep_hours": np.clip(
                    7.2 - 0.95 * academic_pressure + 0.35 * recovery_buffer + rng.normal(0, 0.8, samples),
                    3.0,
                    9.5,
                ),
                "attendance_rate": np.clip(
                    87.0 - 8.0 * academic_pressure + 2.4 * recovery_buffer + rng.normal(0, 6.0, samples),
                    40.0,
                    100.0,
                ),
                "assignments_due": np.clip(
                    np.rint(2.0 + 1.5 * academic_pressure + rng.normal(0, 1.2, samples)),
                    0,
                    8,
                ).astype(int),
                "social_connectedness": np.clip(
                    np.rint(
                        3.3 - 0.6 * academic_pressure + 0.65 * recovery_buffer + rng.normal(0, 0.8, samples)
                    ),
                    1,
                    5,
                ).astype(int),
                "exam_pressure": np.clip(
                    np.rint(5.7 + 2.0 * academic_pressure + rng.normal(0, 1.2, samples)),
                    1,
                    10,
                ).astype(int),
                "compound": np.clip(
                    -0.15 - 0.22 * academic_pressure + 0.18 * recovery_buffer + rng.normal(0, 0.28, samples),
                    -1.0,
                    1.0,
                ),
            }
        )

        burden_score = (
            ((5 - dataset["mood_score"]) / 4) * 100 * 0.2
            + ((dataset["stress_score"] - 1) / 9) * 100 * 0.18
            + ((10 - dataset["energy_score"]) / 9) * 100 * 0.12
            + np.maximum(0.0, (8 - dataset["sleep_hours"]) / 5) * 100 * 0.12
            + np.maximum(0.0, (85 - dataset["attendance_rate"]) / 45) * 100 * 0.08
            + np.minimum(dataset["assignments_due"] / 8, 1.0) * 100 * 0.08
            + ((5 - dataset["social_connectedness"]) / 4) * 100 * 0.1
            + ((dataset["exam_pressure"] - 1) / 9) * 100 * 0.08
            + np.maximum(0.0, -dataset["compound"]) * 100 * 0.04
            + rng.normal(0, 4.5, samples)
        )
        burden_score = np.clip(burden_score, 0.0, 100.0)

        labels = pd.Series(
            np.select(
                [burden_score >= 70, burden_score >= 40],
                ["High Risk", "Stressed"],
                default="Normal",
            ),
            name="risk_level",
        )

        return dataset, labels

    @staticmethod
    def _extract_classes(model: Any) -> list[str]:
        if hasattr(model, "classes_"):
            return [str(value) for value in model.classes_]
        if hasattr(model, "named_steps") and "classifier" in model.named_steps:
            return [str(value) for value in model.named_steps["classifier"].classes_]
        raise ValueError("Unable to determine model classes.")

    def _train_model(self) -> dict[str, Any]:
        dataset, labels = self._build_training_dataset()
        x_train, x_test, y_train, y_test = train_test_split(
            dataset[FEATURE_COLUMNS],
            labels,
            test_size=0.2,
            random_state=42,
            stratify=labels,
        )

        candidates: dict[str, Any] = {
            "Logistic Regression": Pipeline(
                steps=[
                    ("scaler", StandardScaler()),
                    (
                        "classifier",
                        LogisticRegression(
                            max_iter=2500,
                            class_weight="balanced",
                            random_state=42,
                        ),
                    ),
                ]
            ),
            "Random Forest": RandomForestClassifier(
                n_estimators=320,
                max_depth=12,
                min_samples_leaf=2,
                class_weight="balanced_subsample",
                random_state=42,
            ),
        }

        best_name = ""
        best_model: Any = None
        best_score = -1.0
        best_accuracy = -1.0
        models_tested: list[dict[str, Any]] = []

        for name, model in candidates.items():
            model.fit(x_train, y_train)
            predictions = model.predict(x_test)
            accuracy = round(float(accuracy_score(y_test, predictions)), 4)
            macro_f1 = round(float(f1_score(y_test, predictions, average="macro")), 4)
            models_tested.append(
                {
                    "name": name,
                    "accuracy": accuracy,
                    "macro_f1": macro_f1,
                }
            )

            if macro_f1 > best_score or (macro_f1 == best_score and accuracy > best_accuracy):
                best_name = name
                best_model = model
                best_score = macro_f1
                best_accuracy = accuracy

        dataset_profile = {
            "source": SIMULATED_DATASET_NAME,
            "samples": int(len(dataset)),
            "feature_count": len(FEATURE_COLUMNS),
            "train_samples": int(len(x_train)),
            "test_samples": int(len(x_test)),
            "label_distribution": labels.value_counts().sort_index().to_dict(),
        }

        preprocessing = [
            "Generated a simulated student wellness dataset with realistic ranges for mood, stress, sleep, attendance, assignments, social connection, exam pressure, and NLP compound sentiment.",
            "Created three supervised labels: Normal, Stressed, and High Risk using a weighted wellness burden score.",
            "Applied an 80/20 stratified train-test split to preserve class balance during evaluation.",
            "Standardized features for the Logistic Regression baseline and compared it with a Random Forest classifier.",
            "Selected the production classifier using macro-F1 first and accuracy as the tie-breaker.",
        ]

        return {
            "model": best_model,
            "classes": self._extract_classes(best_model),
            "selected_model": best_name,
            "models_tested": models_tested,
            "dataset": dataset_profile,
            "preprocessing": preprocessing,
        }

    def _rule_score(self, features: dict[str, float], recent_logs: pd.DataFrame | None) -> float:
        component_scores = {
            "mood": ((5 - features["mood_score"]) / 4) * 100,
            "stress": ((features["stress_score"] - 1) / 9) * 100,
            "energy": ((10 - features["energy_score"]) / 9) * 100,
            "sleep": max(0.0, (8 - features["sleep_hours"]) / 5) * 100,
            "attendance": max(0.0, (85 - features["attendance_rate"]) / 45) * 100,
            "assignments": min(features["assignments_due"] / 8, 1.0) * 100,
            "social": ((5 - features["social_connectedness"]) / 4) * 100,
            "exam": ((features["exam_pressure"] - 1) / 9) * 100,
            "compound": max(0.0, -features["compound"]) * 100,
        }
        score = (
            component_scores["mood"] * 0.2
            + component_scores["stress"] * 0.18
            + component_scores["energy"] * 0.12
            + component_scores["sleep"] * 0.12
            + component_scores["attendance"] * 0.08
            + component_scores["assignments"] * 0.08
            + component_scores["social"] * 0.1
            + component_scores["exam"] * 0.08
            + component_scores["compound"] * 0.04
        )

        if recent_logs is not None and not recent_logs.empty:
            recent_mean = recent_logs.tail(5)["mood_score"].mean()
            stress_mean = recent_logs.tail(5)["stress_score"].mean()
            if recent_mean <= 2.5:
                score += 5
            if stress_mean >= 7:
                score += 5

        return round(min(score, 100.0), 2)

    @staticmethod
    def label_from_score(score: float) -> str:
        if score >= 70:
            return "High Risk"
        if score >= 40:
            return "Stressed"
        return "Normal"

    def describe_model(self) -> dict[str, Any]:
        return {
            "selected_model": self.selected_model,
            "models_tested": self.models_tested,
            "dataset": self.dataset_profile,
            "features": FEATURE_COLUMNS,
            "labels": list(LABEL_ORDER.keys()),
            "preprocessing": self.preprocessing_steps,
            "forecast_model": "Linear Regression",
        }

    def predict(
        self,
        payload: Any,
        text_analysis: dict[str, Any],
        recent_logs: pd.DataFrame | None = None,
    ) -> dict[str, Any]:
        if hasattr(payload, "__dataclass_fields__"):
            feature_source = asdict(payload)
        else:
            feature_source = dict(payload)

        features = {
            "mood_score": float(feature_source["mood_score"]),
            "stress_score": float(feature_source["stress_score"]),
            "energy_score": float(feature_source["energy_score"]),
            "sleep_hours": float(feature_source["sleep_hours"]),
            "attendance_rate": float(feature_source["attendance_rate"]),
            "assignments_due": float(feature_source["assignments_due"]),
            "social_connectedness": float(feature_source["social_connectedness"]),
            "exam_pressure": float(feature_source["exam_pressure"]),
            "compound": float(text_analysis.get("compound", 0.0)),
        }

        frame = pd.DataFrame([features], columns=FEATURE_COLUMNS)
        model_label = str(self.model.predict(frame)[0])
        probabilities = self.model.predict_proba(frame)[0]
        probability_map = {
            label: round(float(probabilities[index]), 3)
            for index, label in enumerate(self.model_classes)
        }
        risk_score = self._rule_score(features, recent_logs)
        rule_label = self.label_from_score(risk_score)
        label = max([model_label, rule_label], key=lambda item: LABEL_ORDER[item])

        return {
            "label": label,
            "model_label": model_label,
            "selected_model": self.selected_model,
            "model_confidence": round(float(probability_map.get(model_label, 0.0)), 3),
            "dataset_source": self.dataset_profile["source"],
            "risk_score": risk_score,
            "probabilities": probability_map,
            "feature_snapshot": features,
        }

    def forecast_low_days(
        self,
        history: pd.DataFrame,
        horizon: int = 7,
    ) -> list[dict[str, Any]]:
        if history.empty:
            return []

        recent = history.sort_values("log_date").tail(14).copy()
        recent["step"] = np.arange(len(recent))
        x = recent[["step"]]

        mood_model = LinearRegression().fit(x, recent["mood_score"])
        stress_model = LinearRegression().fit(x, recent["stress_score"])

        future = []
        start = int(recent["step"].max()) + 1
        last_date = pd.to_datetime(recent["log_date"].iloc[-1])
        for offset in range(horizon):
            step = start + offset
            future_frame = pd.DataFrame({"step": [step]})
            mood_score = round(float(mood_model.predict(future_frame)[0]), 2)
            stress_score = round(float(stress_model.predict(future_frame)[0]), 2)
            future.append(
                {
                    "date": (last_date + pd.Timedelta(days=offset + 1)).date().isoformat(),
                    "predicted_mood_score": max(1.0, min(5.0, mood_score)),
                    "predicted_stress_score": max(1.0, min(10.0, stress_score)),
                    "low_day_flag": mood_score <= 2.6 or stress_score >= 7.5,
                }
            )

        return future

    def process_and_validate_dataset(
        self,
        raw_df: pd.DataFrame,
    ) -> tuple[pd.DataFrame, dict[str, Any]]:
        df = raw_df.copy()
        df.columns = [str(col).strip().lower() for col in df.columns]

        column_aliases = {
            "mood": "mood_score",
            "stress": "stress_score",
            "energy": "energy_score",
            "sleep": "sleep_hours",
            "attendance": "attendance_rate",
            "assignments": "assignments_due",
            "social": "social_connectedness",
            "exam": "exam_pressure",
            "text": "notes",
            "journal": "notes",
            "risk": "risk_level",
            "target": "risk_level",
            "label": "risk_level",
        }
        df = df.rename(columns=column_aliases)

        defaults = {
            "mood_score": 3,
            "stress_score": 5,
            "energy_score": 5,
            "sleep_hours": 7.0,
            "attendance_rate": 85.0,
            "assignments_due": 2,
            "social_connectedness": 3,
            "exam_pressure": 5,
            "compound": 0.0,
        }

        repaired_columns = []

        if "compound" not in df.columns or df["compound"].isnull().any():
            if "notes" in df.columns:
                compounds = []
                for val in df["notes"].fillna(""):
                    analysis = analyze_text(str(val))
                    compounds.append(analysis["compound"])
                df["compound"] = compounds
                repaired_columns.append("compound (computed via NLP from notes)")

        for col, default_val in defaults.items():
            if col not in df.columns:
                df[col] = default_val
                repaired_columns.append(f"{col} (defaulted to {default_val})")
            else:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(default_val)

        df["mood_score"] = np.clip(df["mood_score"].round(), 1, 5).astype(int)
        df["stress_score"] = np.clip(df["stress_score"].round(), 1, 10).astype(int)
        df["energy_score"] = np.clip(df["energy_score"].round(), 1, 10).astype(int)
        df["sleep_hours"] = np.clip(df["sleep_hours"], 1.0, 14.0)
        df["attendance_rate"] = np.clip(df["attendance_rate"], 0.0, 100.0)
        df["assignments_due"] = np.clip(df["assignments_due"].round(), 0, 20).astype(int)
        df["social_connectedness"] = np.clip(df["social_connectedness"].round(), 1, 5).astype(int)
        df["exam_pressure"] = np.clip(df["exam_pressure"].round(), 1, 10).astype(int)
        df["compound"] = np.clip(df["compound"], -1.0, 1.0)

        if "risk_level" not in df.columns or df["risk_level"].isnull().all():
            generated_labels = []
            for _, row in df.iterrows():
                feat_dict = {col: float(row[col]) for col in FEATURE_COLUMNS}
                score = self._rule_score(feat_dict, recent_logs=None)
                generated_labels.append(self.label_from_score(score))
            df["risk_level"] = generated_labels
            repaired_columns.append("risk_level (computed via rule score)")
        else:
            valid_labels = set(LABEL_ORDER.keys())
            df["risk_level"] = df["risk_level"].astype(str).map(
                lambda val: val if val in valid_labels else "Normal"
            )

        profile = {
            "total_rows": int(len(df)),
            "feature_count": len(FEATURE_COLUMNS),
            "label_distribution": df["risk_level"].value_counts().to_dict(),
            "repaired_columns": repaired_columns,
        }

        return df, profile

    def retrain_with_custom_dataset(
        self,
        raw_df: pd.DataFrame,
        dataset_name: str = "Uploaded Custom Dataset",
    ) -> dict[str, Any]:
        df, profile = self.process_and_validate_dataset(raw_df)
        x = df[FEATURE_COLUMNS]
        y = df["risk_level"]

        if len(df) < 10:
            raise ValueError("Dataset must contain at least 10 rows for training.")

        try:
            x_train, x_test, y_train, y_test = train_test_split(
                x, y, test_size=0.2, random_state=42, stratify=y
            )
        except Exception:
            x_train, x_test, y_train, y_test = train_test_split(
                x, y, test_size=0.2, random_state=42
            )

        candidates: dict[str, Any] = {
            "Logistic Regression": Pipeline(
                steps=[
                    ("scaler", StandardScaler()),
                    (
                        "classifier",
                        LogisticRegression(
                            max_iter=2500,
                            class_weight="balanced",
                            random_state=42,
                        ),
                    ),
                ]
            ),
            "Random Forest": RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_leaf=2,
                class_weight="balanced_subsample",
                random_state=42,
            ),
        }

        best_name = ""
        best_model: Any = None
        best_score = -1.0
        best_accuracy = -1.0
        models_tested: list[dict[str, Any]] = []

        for name, model in candidates.items():
            model.fit(x_train, y_train)
            preds = model.predict(x_test)
            acc = round(float(accuracy_score(y_test, preds)), 4)
            f1 = round(float(f1_score(y_test, preds, average="macro")), 4)
            models_tested.append(
                {
                    "name": name,
                    "accuracy": acc,
                    "macro_f1": f1,
                }
            )
            if f1 > best_score or (f1 == best_score and acc > best_accuracy):
                best_name = name
                best_model = model
                best_score = f1
                best_accuracy = acc

        test_preds = best_model.predict(x_test)
        classes_present = sorted(list(set(y_test.tolist() + test_preds.tolist())))
        cm = confusion_matrix(y_test, test_preds, labels=classes_present).tolist()
        report = classification_report(y_test, test_preds, output_dict=True, zero_division=0)

        feature_importances = {}
        rf_candidate = candidates.get("Random Forest")
        if rf_candidate and hasattr(rf_candidate, "feature_importances_"):
            for col, imp in zip(FEATURE_COLUMNS, rf_candidate.feature_importances_):
                feature_importances[col] = round(float(imp), 4)

        self.model = best_model
        self.model_classes = self._extract_classes(best_model)
        self.selected_model = best_name
        self.models_tested = models_tested
        self.dataset_profile = {
            "source": dataset_name,
            "samples": int(len(df)),
            "feature_count": len(FEATURE_COLUMNS),
            "train_samples": int(len(x_train)),
            "test_samples": int(len(x_test)),
            "label_distribution": y.value_counts().to_dict(),
        }
        self.preprocessing_steps = [
            f"Parsed and validated user dataset '{dataset_name}' with {len(df)} records.",
            f"Repaired/computed fields: {', '.join(profile['repaired_columns']) if profile['repaired_columns'] else 'None required'}.",
            "Applied 80/20 train-test split for model training and benchmark evaluation.",
            f"Evaluated candidates; selected {best_name} (Accuracy: {best_accuracy * 100:.1f}%, Macro-F1: {best_score:.4f}).",
        ]

        return {
            "dataset_profile": self.dataset_profile,
            "selected_model": best_name,
            "models_tested": models_tested,
            "test_accuracy": best_accuracy,
            "test_macro_f1": best_score,
            "confusion_matrix": {
                "classes": classes_present,
                "matrix": cm,
            },
            "classification_report": report,
            "feature_importances": feature_importances,
            "repaired_columns": profile["repaired_columns"],
        }

    def predict_single_sample(self, sample_dict: dict[str, Any]) -> dict[str, Any]:
        features = {
            "mood_score": float(sample_dict.get("mood_score", 3)),
            "stress_score": float(sample_dict.get("stress_score", 5)),
            "energy_score": float(sample_dict.get("energy_score", 5)),
            "sleep_hours": float(sample_dict.get("sleep_hours", 7.0)),
            "attendance_rate": float(sample_dict.get("attendance_rate", 85.0)),
            "assignments_due": float(sample_dict.get("assignments_due", 2)),
            "social_connectedness": float(sample_dict.get("social_connectedness", 3)),
            "exam_pressure": float(sample_dict.get("exam_pressure", 5)),
            "compound": float(sample_dict.get("compound", 0.0)),
        }

        frame = pd.DataFrame([features], columns=FEATURE_COLUMNS)
        model_label = str(self.model.predict(frame)[0])
        probabilities = self.model.predict_proba(frame)[0]
        probability_map = {
            label: round(float(probabilities[index]), 3)
            for index, label in enumerate(self.model_classes)
        }
        risk_score = self._rule_score(features, recent_logs=None)
        rule_label = self.label_from_score(risk_score)
        final_label = max([model_label, rule_label], key=lambda item: LABEL_ORDER[item])

        return {
            "timestamp": pd.Timestamp.now().isoformat(),
            "label": final_label,
            "model_label": model_label,
            "risk_score": risk_score,
            "model_confidence": round(float(probability_map.get(model_label, 0.0)), 3),
            "probabilities": probability_map,
            "features": features,
            "dataset_source": self.dataset_profile["source"],
        }

    def generate_sample_wellness_csv(self) -> str:
        df, labels = self._build_training_dataset(samples=100, random_state=123)
        df["risk_level"] = labels
        df["notes"] = [
            "Feeling okay, managing coursework."
            if r == "Normal"
            else "Feeling stressed about upcoming exams and project deadlines."
            if r == "Stressed"
            else "Exhausted, low sleep, struggling with deadlines."
            for r in df["risk_level"]
        ]
        return df.to_csv(index=False)


risk_engine = RiskEngine()

