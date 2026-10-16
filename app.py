import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from fitting import CITY_NAMES, CITY_STATE_INDICES, _city_series, _load_city_data, fit_city


BASE_DIR = Path(__file__).parent
CITY_CONFIG = {
    "Noltrame": {
        "code": "no",
        "start_day": 21,
        "initial_parameters": (1, 1 / 5, 0.03, 1 / 27, 0.1, 0.5, 1, 0.0564963, 0.7367226, 1, 0.6, 0.4),
    },
    "Sorya": {
        "code": "s",
        "start_day": 22,
        "initial_parameters": (2, 1 / 5, 0.033, 1 / 27, 0.1, 0.5, 1, 0.0564963, 0.7367226, 1, 0.6, 0.4),
    },
    "Neamrolt": {
        "code": "ne",
        "start_day": 6,
        "initial_parameters": (1, 1 / 4, 0.03, 1 / 28, 0.1, 0.5, 1, 0.5, 0.9, 1, 0.6, 0.4),
    },
}

PARAMETER_NAMES = ("c", "gamma_h", "rho", "mu_m", "p_h", "p_m", "p_11", "p_21", "p_12", "t_11", "t_21", "t_12")
MAX_NFEV = 100


def _plot_city_fit(city_code, predictions, observed_times, observed):
    fitted = _city_series(predictions, city_code)
    city_name = CITY_NAMES[city_code]
    labels = ("Infected", "Hospitalized", "Recovered")
    colors = ("#d62728", "#111111", "#2ca02c")

    figure, axis = plt.subplots(figsize=(10, 5))
    for values, actual, label, color in zip(fitted, observed, labels, colors):
        axis.plot(np.arange(len(values)), values, label=f"{label} prediction", color=color)
        actual_values = pd.to_numeric(actual, errors="coerce").to_numpy()
        valid = np.isfinite(actual_values)
        axis.scatter(observed_times[valid], actual_values[valid], label=f"{label} observed", color=color, s=24)
    axis.set_title(f"Dengue model - {city_name}")
    axis.set_xlabel("Day")
    axis.set_ylabel("People")
    axis.grid(alpha=0.2)
    axis.legend(ncol=2)
    figure.tight_layout()
    return figure


def run_app():
    st.set_page_config(page_title="Dengue decision support", page_icon="🦟", layout="wide")
    st.title("Dengue intervention decision support")
    st.caption("Prototype académique : les résultats sont exploratoires et ne doivent pas guider une décision de santé publique.")

    with st.sidebar:
        st.header("Simulation")
        selected_city = st.selectbox("Ville", list(CITY_CONFIG))
        run_fit = st.button("Lancer l'ajustement", type="primary", use_container_width=True)

    st.markdown(
        "Cette interface compare les observations disponibles avec la trajectoire "
        "du modèle ajusté pour la ville sélectionnée."
    )

    if run_fit:
        config = CITY_CONFIG[selected_city]
        with st.spinner(f"Ajustement de {selected_city}..."):
            result, predictions = fit_city(
                config["code"],
                start_day=config["start_day"],
                initial_parameters=config["initial_parameters"],
                dataset_path=BASE_DIR / "dataset_cities.csv",
                plot=False,
                max_nfev=MAX_NFEV,
            )
            observed_times, observed = _load_city_data(
                config["code"],
                BASE_DIR / "dataset_cities.csv",
            )

        st.session_state["fit_result"] = result
        st.session_state["predictions"] = predictions
        st.session_state["observed_times"] = observed_times
        st.session_state["observed"] = observed
        st.session_state["city_code"] = config["code"]

    if "fit_result" not in st.session_state:
        st.info("Choisis une ville puis clique sur « Lancer l'ajustement ».")
        return

    result = st.session_state["fit_result"]
    predictions = st.session_state["predictions"]
    observed_times = st.session_state["observed_times"]
    observed = st.session_state["observed"]
    city_code = st.session_state["city_code"]
    infected, hospitalized, recovered = _city_series(predictions, city_code)

    metric_columns = st.columns(4)
    metric_columns[0].metric("Pic infectés", f"{np.nanmax(infected):.0f}")
    metric_columns[1].metric("Jour du pic", f"{np.nanargmax(infected)}")
    metric_columns[2].metric("Pic hospitalisés", f"{np.nanmax(hospitalized):.0f}")
    metric_columns[3].metric("Coût d'ajustement", f"{result.cost:.1f}")

    st.pyplot(
        _plot_city_fit(city_code, predictions, observed_times, observed),
        clear_figure=True,
    )

    with st.expander("Paramètres ajustés"):
        parameters = pd.DataFrame(
            {"Paramètre": PARAMETER_NAMES, "Valeur": result.x}
        )
        st.dataframe(parameters, hide_index=True, use_container_width=True)
        st.write(f"Statut de l'optimiseur : `{result.message}`")


def launch_streamlit():
    from streamlit.web import cli as streamlit_cli

    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    sys.argv = [
        "streamlit",
        "run",
        os.path.abspath(__file__),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]
    raise SystemExit(streamlit_cli.main())


if __name__ == "__main__":
    if st.runtime.exists():
        run_app()
    else:
        launch_streamlit()
