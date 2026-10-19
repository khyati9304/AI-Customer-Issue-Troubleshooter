import streamlit as st

from app.graph import troubleshoot


st.set_page_config(
    page_title="AI Customer Issue Troubleshooter",
    page_icon="🛠️",
    layout="wide",
)


st.title("🛠️ AI Customer Issue Troubleshooter")

st.markdown(
    """
    Investigate software issues using an LLM-powered workflow,
    simulated diagnostic tools, and evidence-based recommendations.
    """
)

st.info(
    "Demo environment: diagnostic checks use simulated data, "
    "not real production systems."
)

with st.form("issue_form"):
    issue = st.text_area(
        "Describe your technical issue",
        placeholder=(
            "Example: My API returns HTTP 401 after I rotated "
            "my API key yesterday."
        ),
        height=140,
    )

    submitted = st.form_submit_button(
        "Investigate issue",
        type="primary",
    )


if submitted:
    if not issue.strip():
        st.warning("Please describe the issue first.")

    else:
        try:
            with st.spinner(
                "Analyzing the issue and running diagnostics..."
            ):
                result = troubleshoot(issue)

            report = result.get("final_report")

            st.subheader("Investigation summary")

            st.write(
                f"**Issue category:** {result.get('issue_type', 'unknown')}"
            )

            st.write(
                "**Diagnostic checks completed:** "
                f"{result.get('investigation_steps', 0)}"
            )

            if report:
                st.subheader("Diagnosis")

                st.write("**Issue summary**")
                st.write(report["issue_summary"])

                st.write("**Probable root cause**")
                st.write(report["probable_root_cause"])

                st.write("**Severity**")
                st.write(report["severity"].upper())

                st.write("**Estimated confidence**")
                st.progress(
                    float(report["confidence"]),
                    text=f"{report['confidence']:.0%} (model estimate)",
                )

                st.write("**Supporting evidence**")

                for item in report["supporting_evidence"]:
                    st.markdown(f"- {item}")

                st.write("**Recommended actions**")

                for action in report["recommended_actions"]:
                    st.markdown(f"- {action}")

                st.write("**Escalation required**")
                st.write(
                    "Yes" if report["needs_escalation"] else "No"
                )

                if report["limitations"]:
                    st.warning("Limitations")

                    for limitation in report["limitations"]:
                        st.markdown(f"- {limitation}")

            with st.expander("View diagnostic evidence"):
                st.json(result.get("diagnostic_results", []))

            if result.get("errors"):
                with st.expander("Investigation warnings"):
                    st.json(result["errors"])

            with st.expander("View complete report as JSON"):
                st.json(report)

        except Exception as exc:
            st.error(
                "The investigation could not be completed. "
                "Check the application configuration and terminal logs."
            )
            print(f"Application error: {type(exc).__name__}: {exc}")