from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas
from scipy import optimize


PARAMETER_LOWER_BOUNDS = np.zeros(12)
PARAMETER_UPPER_BOUNDS = np.array(
    [np.inf, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    dtype=float,
)

CITY_STATE_INDICES = {
    "no": {"infected": (9, 10, 11), "hospitalized": (27, 28, 29), "recovered": (18, 19, 20)},
    "s": {"infected": (12, 13, 14), "hospitalized": (30, 31, 32), "recovered": (21, 22, 23)},
    "ne": {"infected": (15, 16, 17), "hospitalized": (33, 34, 35), "recovered": (24, 25, 26)},
}

CITY_NAMES = {"no": "Noltrame", "s": "Sorya", "ne": "Neamrolt"}
FITTED_PARAMETER_INDICES = {"no": (0,), "s": (0, 2, 4, 5), "ne": (0, 7, 8)}
DEFAULT_MAX_NFEV = 100


def _city_series(predictions, city):
    indices = CITY_STATE_INDICES[city]
    return tuple(predictions[:, index].sum(axis=1) for index in indices.values())


def _load_city_data(city, dataset_path):
    dataset = pandas.read_csv(dataset_path)
    city_name = CITY_NAMES[city]
    observed = (
        dataset[f"Infected {city_name}"],
        dataset[f"Hospitalized {city_name}"],
        dataset[f"Recovered {city_name}"],
    )
    return dataset["Date"].to_numpy(), observed


def fit_city(
    city,
    *,
    start_day,
    initial_parameters,
    dataset_path=None,
    plot=False,
    max_nfev=None,
):
    """Fit the transmission model to one city's observed time series."""
    if city not in CITY_STATE_INDICES:
        raise ValueError(f"Unknown city code: {city}")
    if len(initial_parameters) != 12:
        raise ValueError("initial_parameters must contain 12 values")

    import Simulation

    path = Path(dataset_path) if dataset_path else Path(__file__).with_name("dataset_cities.csv")
    observed_times, observed = _load_city_data(city, path)
    simulation_times = np.arange(0, 201, dtype=float)
    model_times = simulation_times
    initial_state = Simulation.creation_Y0()
    fitted_indices = FITTED_PARAMETER_INDICES[city]
    initial_parameters = np.asarray(initial_parameters, dtype=float)
    fitted_initial_parameters = initial_parameters[list(fitted_indices)]
    fitted_lower_bounds = PARAMETER_LOWER_BOUNDS[list(fitted_indices)]
    fitted_upper_bounds = PARAMETER_UPPER_BOUNDS[list(fitted_indices)]

    def residuals(fitted_parameters):
        parameters = initial_parameters.copy()
        parameters[list(fitted_indices)] = fitted_parameters
        model = Simulation.integrate.odeint(
            Simulation.deriv_workers,
            initial_state,
            observed_times,
            args=tuple(parameters.tolist()),
        )
        predicted = _city_series(model, city)
        residual = np.concatenate(
            [
                np.asarray(actual - expected, dtype=float)
                for actual, expected in zip(observed, predicted)
            ]
        )
        return np.nan_to_num(residual, nan=0.0)

    result = optimize.least_squares(
        residuals,
        fitted_initial_parameters,
        bounds=(fitted_lower_bounds, fitted_upper_bounds),
        max_nfev=max_nfev or DEFAULT_MAX_NFEV,
    )
    fitted_parameters = initial_parameters.copy()
    fitted_parameters[list(fitted_indices)] = result.x
    full_predictions = Simulation.integrate.odeint(
        Simulation.deriv_workers,
        initial_state,
        simulation_times,
        args=tuple(fitted_parameters.tolist()),
    )
    predictions = full_predictions
    result.x = fitted_parameters

    if plot:
        _plot_fit(city, model_times, predictions, observed_times, observed)

    return result, predictions


def _plot_fit(city, model_times, predictions, observed_times, observed):
    fitted = _city_series(predictions, city)
    city_name = CITY_NAMES[city]
    labels = ("Infected", "Hospitalized", "Recovered")
    colors = ("red", "black", "green")

    plt.figure(figsize=(12, 6))
    for values, actual, label, color in zip(fitted, observed, labels, colors):
        plt.plot(model_times, values, label=f"{label} {city_name}", color=color)
        plt.plot(observed_times, actual, "o", color=color)
    plt.title(f"Fitting of {city_name}")
    plt.xlabel("t (days)")
    plt.ylabel("Number of individuals")
    plt.legend()
    plt.show()


def fit_sorya(**kwargs):
    return fit_city(
        "s",
        start_day=22,
        initial_parameters=(2, 1 / 5, 0.033, 1 / 27, 0.1, 0.5, 1, 0.0564963, 0.7367226, 1, 0.6, 0.4),
        **kwargs,
    )


def fit_noltrame(**kwargs):
    return fit_city(
        "no",
        start_day=21,
        initial_parameters=(1, 1 / 5, 0.03, 1 / 27, 0.1, 0.5, 1, 0.0564963, 0.7367226, 1, 0.6, 0.4),
        **kwargs,
    )


def fit_neamrolt(**kwargs):
    return fit_city(
        "ne",
        start_day=6,
        initial_parameters=(1, 1 / 4, 0.03, 1 / 28, 0.1, 0.5, 1, 0.5, 0.9, 1, 0.6, 0.4),
        **kwargs,
    )
