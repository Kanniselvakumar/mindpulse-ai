from __future__ import annotations

import time
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from frontend.ui import apply_branding, get_logo_data_uri, render_sidebar_profile
from shared.gateway import (
    bootstrap,
    get_sample_wellness_csv,
    predict_realtime_sample,
    retrain_model,
    upload_dataset,
)

st.set_page_config(
    page_title="Realtime & Datasets Studio - MindPulse AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

bootstrap()
apply_branding()
profile = render_sidebar_profile()

logo_src = get_logo_data_uri()
logo_img = f'<img src="{logo_src}" style="width: 38px; height: 38px; border-radius: 8px; margin-right: 0.6rem; vertical-align: middle;" alt="Logo"/>' if logo_src else ''
st.markdown(f"<div style='display:flex; align-items:center; margin-bottom: 0.2rem;'>{logo_img}<h1 style='margin:0; font-size: 2rem;'>Real-Time Data & Dataset Studio</h1></div>", unsafe_allow_html=True)
st.caption(
    "Upload custom student wellness datasets, retrain ML classifiers, evaluate performance metrics, and stream live wellness data in real-time."
)

tab1, tab2 = st.tabs(
    ["📁 Dataset Upload & Custom ML Training", "⚡ Live Real-Time Streamer & Simulator"]
)

# ─── TAB 1: DATASET UPLOAD & CUSTOM ML TRAINING ──────────────────────────────
with tab1:
    st.subheader("1. Custom Dataset Ingestion & Validation")
    st.write(
        "Upload a `.csv` or `.json` dataset containing student wellness metrics (`mood_score`, `stress_score`, `sleep_hours`, `attendance_rate`, etc.). Missing features or text notes will be automatically imputed using NLP sentiment scoring."
    )

    col_up1, col_up2 = st.columns([2, 1])

    with col_up1:
        uploaded_file = st.file_uploader(
            "Upload Wellness Dataset (CSV or JSON)",
            type=["csv", "json"],
            help="Supported headers: mood_score, stress_score, energy_score, sleep_hours, attendance_rate, assignments_due, social_connectedness, exam_pressure, notes/text, risk_level",
        )

    with col_up2:
        st.markdown("**Need a sample dataset?**")
        sample_csv = get_sample_wellness_csv()
        st.download_button(
            label="📥 Download Sample CSV (100 Rows)",
            data=sample_csv,
            file_name="sample_student_wellness_dataset.csv",
            mime="text/csv",
            use_container_width=True,
        )
        if st.button("⚡ Use Built-in Sample Dataset", use_container_width=True):
            st.session_state["active_dataset_content"] = sample_csv
            st.session_state["active_dataset_name"] = "Sample Benchmark Dataset (100 rows)"
            st.success("Loaded benchmark dataset into memory!")

    # Check if user uploaded a file
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        st.session_state["active_dataset_content"] = file_bytes.decode("utf-8", errors="replace")
        st.session_state["active_dataset_name"] = uploaded_file.name

    if "active_dataset_content" in st.session_state:
        dataset_content = st.session_state["active_dataset_content"]
        dataset_name = st.session_state.get("active_dataset_name", "Uploaded Dataset")

        with st.spinner("Processing & validating dataset..."):
            try:
                eval_res = upload_dataset(dataset_content, dataset_name)
                profile_info = eval_res["profile"]
                preview_df = pd.DataFrame(eval_res["preview"])

                st.success(f"Successfully processed dataset: **{dataset_name}**")

                mcol1, mcol2, mcol3, mcol4 = st.columns(4)
                mcol1.metric("Total Records", profile_info["total_rows"])
                mcol2.metric("Features Extracted", profile_info["feature_count"])
                normal_count = profile_info["label_distribution"].get("Normal", 0)
                stressed_count = profile_info["label_distribution"].get("Stressed", 0)
                high_risk_count = profile_info["label_distribution"].get("High Risk", 0)
                mcol3.metric("Normal / Stressed", f"{normal_count} / {stressed_count}")
                mcol4.metric("High Risk Records", high_risk_count)

                if profile_info.get("repaired_columns"):
                    st.info(
                        "ℹ️ Auto-repaired / computed fields: "
                        + ", ".join(profile_info["repaired_columns"])
                    )

                st.subheader("Data Preview & Distribution")
                pcol1, pcol2 = st.columns([1.5, 1])

                with pcol1:
                    st.dataframe(preview_df, use_container_width=True, height=260)

                with pcol2:
                    dist_df = pd.DataFrame(
                        list(profile_info["label_distribution"].items()),
                        columns=["Risk Level", "Count"],
                    )
                    fig_dist = px.pie(
                        dist_df,
                        names="Risk Level",
                        values="Count",
                        title="Class Target Distribution",
                        color="Risk Level",
                        color_discrete_map={
                            "Normal": "#10B981",
                            "Stressed": "#F59E0B",
                            "High Risk": "#F43F5E",
                        },
                        hole=0.4,
                    )
                    fig_dist.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10))
                    st.plotly_chart(fig_dist, use_container_width=True)

                st.markdown("---")
                st.subheader("2. Model Retraining & Performance Evaluation")
                st.write(
                    "Click below to retrain the `Logistic Regression` baseline and `Random Forest` ensemble classifiers on your dataset, evaluate test accuracy, and update the active risk engine model."
                )

                if st.button("🚀 Retrain ML Engine on Uploaded Dataset", type="primary"):
                    with st.spinner("Retraining classifiers and computing confusion matrix..."):
                        retrain_res = retrain_model(dataset_content, dataset_name)
                        st.session_state["retrain_results"] = retrain_res
                        st.toast("Model retrained successfully!", icon="🎉")

                if "retrain_results" in st.session_state:
                    results = st.session_state["retrain_results"]

                    r1, r2, r3 = st.columns(3)
                    r1.metric("Selected Champion Model", results["selected_model"])
                    r2.metric("Test Accuracy", f"{results['test_accuracy'] * 100:.1f}%")
                    r3.metric("Test Macro-F1", f"{results['test_macro_f1']:.4f}")

                    st.markdown("##### Candidate Model Comparison")
                    comp_df = pd.DataFrame(results["models_tested"])
                    comp_df["accuracy"] = (comp_df["accuracy"] * 100).round(1).astype(str) + "%"
                    st.dataframe(comp_df, use_container_width=True)

                    c1, c2 = st.columns(2)

                    with c1:
                        st.markdown("##### Confusion Matrix")
                        cm_data = results["confusion_matrix"]
                        classes = cm_data["classes"]
                        matrix = cm_data["matrix"]

                        fig_cm = px.imshow(
                            matrix,
                            x=classes,
                            y=classes,
                            text_auto=True,
                            color_continuous_scale="Blues",
                            labels=dict(x="Predicted Label", y="True Label"),
                            title="Confusion Matrix (Test Set)",
                        )
                        fig_cm.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
                        st.plotly_chart(fig_cm, use_container_width=True)

                    with c2:
                        st.markdown("##### Feature Importance Breakdown")
                        feat_imps = results.get("feature_importances", {})
                        if feat_imps:
                            fi_df = (
                                pd.DataFrame(
                                    list(feat_imps.items()),
                                    columns=["Feature", "Importance"],
                                )
                                .sort_values("Importance", ascending=True)
                            )
                            fig_fi = px.bar(
                                fi_df,
                                x="Importance",
                                y="Feature",
                                orientation="h",
                                title="Random Forest Feature Importances",
                                color="Importance",
                                color_continuous_scale="Viridis",
                            )
                            fig_fi.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
                            st.plotly_chart(fig_fi, use_container_width=True)
                        else:
                            st.info("Feature importance is available for Random Forest classifier.")

            except Exception as e:
                st.error(f"Error analyzing dataset: {str(e)}")

# ─── TAB 2: LIVE REAL-TIME STREAMER & SIMULATOR ──────────────────────────────
with tab2:
    st.subheader("Real-Time Data Streaming & Live Sensor Simulation")
    st.write(
        "Simulate live incoming stream data from wearable devices or student check-ins. Stream row-by-row data to observe real-time ML classifications, scrolling risk graphs, and automated high-risk alert triggers."
    )

    # Initialize stream buffer in session_state
    if "realtime_buffer" not in st.session_state:
        st.session_state["realtime_buffer"] = []

    ctrl1, ctrl2, ctrl3 = st.columns([1.5, 1, 1])

    with ctrl1:
        stream_mode = st.radio(
            "Stream Source Mode",
            options=["Live Synthetic Generator", "Replay Active Uploaded Dataset"],
            horizontal=True,
        )

    with ctrl2:
        tick_interval = st.slider("Stream Tick Interval (seconds)", 0.2, 2.0, 0.5, 0.1)

    with ctrl3:
        st.markdown("<br/>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            run_stream = st.button("▶️ Stream 10 Ticks", type="primary", use_container_width=True)
        with col_btn2:
            if st.button("🧹 Clear Stream", use_container_width=True):
                st.session_state["realtime_buffer"] = []
                st.rerun()

    # If stream triggered
    if run_stream:
        # Load dataset rows if replay mode selected
        replay_df = None
        if stream_mode == "Replay Active Uploaded Dataset":
            if "active_dataset_content" in st.session_state:
                try:
                    eval_res = upload_dataset(
                        st.session_state["active_dataset_content"],
                        st.session_state.get("active_dataset_name", "dataset.csv"),
                    )
                    replay_df = pd.DataFrame(eval_res["preview"])
                except Exception:
                    st.warning("Could not parse active uploaded dataset. Defaulting to synthetic generator.")

        progress_bar = st.progress(0)
        status_text = st.empty()

        for tick in range(10):
            if replay_df is not None and not replay_df.empty:
                row_idx = (len(st.session_state["realtime_buffer"]) + tick) % len(replay_df)
                row = replay_df.iloc[row_idx].to_dict()
                sample_input = {
                    "mood_score": float(row.get("mood_score", 3)),
                    "stress_score": float(row.get("stress_score", 5)),
                    "energy_score": float(row.get("energy_score", 5)),
                    "sleep_hours": float(row.get("sleep_hours", 7.0)),
                    "attendance_rate": float(row.get("attendance_rate", 85.0)),
                    "assignments_due": float(row.get("assignments_due", 2)),
                    "social_connectedness": float(row.get("social_connectedness", 3)),
                    "exam_pressure": float(row.get("exam_pressure", 5)),
                    "compound": float(row.get("compound", 0.0)),
                }
            else:
                # Generate synthetic incoming data tick
                base_stress = np.random.choice([3, 5, 8, 9], p=[0.4, 0.3, 0.2, 0.1])
                sample_input = {
                    "mood_score": int(np.clip(6 - base_stress / 2 + np.random.randint(-1, 2), 1, 5)),
                    "stress_score": int(np.clip(base_stress + np.random.randint(-1, 2), 1, 10)),
                    "energy_score": int(np.clip(7 - base_stress / 2 + np.random.randint(-1, 2), 1, 10)),
                    "sleep_hours": round(float(np.clip(8.5 - base_stress * 0.4 + np.random.normal(0, 0.5), 3.0, 9.5)), 1),
                    "attendance_rate": round(float(np.clip(90.0 - base_stress * 3.0 + np.random.normal(0, 2.0), 50.0, 100.0)), 1),
                    "assignments_due": int(np.clip(np.random.poisson(base_stress / 2), 0, 8)),
                    "social_connectedness": int(np.clip(5 - base_stress / 3 + np.random.randint(-1, 2), 1, 5)),
                    "exam_pressure": int(np.clip(base_stress + np.random.randint(0, 2), 1, 10)),
                    "compound": round(float(np.clip(0.3 - base_stress * 0.1, -1.0, 1.0)), 2),
                }

            res = predict_realtime_sample(sample_input)
            st.session_state["realtime_buffer"].append(res)

            if res["label"] == "High Risk":
                st.toast(
                    f"⚠️ HIGH RISK ALERT DETECTED! Risk Score: {res['risk_score']}",
                    icon="🚨",
                )

            progress_bar.progress((tick + 1) / 10)
            status_text.text(f"Processed stream tick {tick + 1}/10... Label: {res['label']}")
            time.sleep(tick_interval)

        status_text.text("Streaming batch complete!")

    # Display live dashboard metrics if buffer has data
    buffer = st.session_state.get("realtime_buffer", [])

    if not buffer:
        st.info("No real-time stream data recorded yet. Click '▶️ Stream 10 Ticks' above to launch live data streaming!")
    else:
        st.markdown("### 📊 Real-Time Stream Monitoring Panel")

        tot_samples = len(buffer)
        normal_cnt = sum(1 for item in buffer if item["label"] == "Normal")
        stressed_cnt = sum(1 for item in buffer if item["label"] == "Stressed")
        high_risk_cnt = sum(1 for item in buffer if item["label"] == "High Risk")
        latest_item = buffer[-1]

        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        kpi1.metric("Stream Ticks Processed", tot_samples)
        kpi2.metric("Normal %", f"{(normal_cnt / tot_samples) * 100:.1f}%")
        kpi3.metric("Stressed %", f"{(stressed_cnt / tot_samples) * 100:.1f}%")
        kpi4.metric("High Risk %", f"{(high_risk_cnt / tot_samples) * 100:.1f}%")
        kpi5.metric("Latest Risk Score", latest_item["risk_score"], delta=latest_item["label"])

        st.markdown("---")

        # Scrolling real-time Plotly graph
        gcol1, gcol2 = st.columns([2, 1])

        with gcol1:
            st.markdown("##### Dynamic Real-Time Signal Stream")
            stream_df = pd.DataFrame([
                {
                    "tick": idx + 1,
                    "timestamp": item["timestamp"],
                    "mood_score": item["features"]["mood_score"],
                    "stress_score": item["features"]["stress_score"],
                    "sleep_hours": item["features"]["sleep_hours"],
                    "risk_score": item["risk_score"],
                    "risk_level": item["label"],
                }
                for idx, item in enumerate(buffer)
            ])

            fig_stream = go.Figure()
            fig_stream.add_trace(go.Scatter(x=stream_df["tick"], y=stream_df["mood_score"], name="Mood Score (1-5)", mode="lines+markers", line=dict(color="#14B8A6", width=2)))
            fig_stream.add_trace(go.Scatter(x=stream_df["tick"], y=stream_df["stress_score"], name="Stress Score (1-10)", mode="lines+markers", line=dict(color="#6366F1", width=2)))
            fig_stream.add_trace(go.Scatter(x=stream_df["tick"], y=stream_df["risk_score"], name="ML Risk Score (0-100)", mode="lines+markers", line=dict(color="#F43F5E", width=3, dash="dot")))

            fig_stream.update_layout(
                xaxis_title="Stream Tick #",
                yaxis_title="Score Value",
                height=350,
                margin=dict(l=10, r=10, t=20, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_stream, use_container_width=True)

        with gcol2:
            st.markdown("##### Real-Time Risk Level Breakdown")
            risk_df = pd.DataFrame([
                {"Risk Level": "Normal", "Count": normal_cnt},
                {"Risk Level": "Stressed", "Count": stressed_cnt},
                {"Risk Level": "High Risk", "Count": high_risk_cnt},
            ])
            fig_bar = px.bar(
                risk_df,
                x="Risk Level",
                y="Count",
                color="Risk Level",
                color_discrete_map={
                    "Normal": "#10B981",
                    "Stressed": "#F59E0B",
                    "High Risk": "#F43F5E",
                },
                title="Live Risk Class Counts",
            )
            fig_bar.update_layout(height=350, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("##### Live Streamed Log Table (Recent 10 Records)")
        display_data = []
        for idx, item in list(enumerate(buffer))[-10:]:
            display_data.append({
                "Tick #": idx + 1,
                "Timestamp": item["timestamp"],
                "Predicted Risk Level": item["label"],
                "ML Risk Score": item["risk_score"],
                "Model Confidence": f"{item['model_confidence'] * 100:.1f}%",
                "Mood Score": item["features"]["mood_score"],
                "Stress Score": item["features"]["stress_score"],
                "Sleep Hours": item["features"]["sleep_hours"],
                "Attendance %": item["features"]["attendance_rate"],
            })
        st.dataframe(pd.DataFrame(display_data), use_container_width=True)
