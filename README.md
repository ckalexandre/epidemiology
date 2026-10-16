# Dengue Intervention Decision-Support Prototype

An epidemiological simulation and decision-support prototype for exploring how dengue can spread across three interconnected cities and how intervention scenarios may change the trajectory of an outbreak.

The project combines:

- A compartmental human-and-mosquito transmission model
- Three-city population movement
- Observed city-level time-series data
- Parameter fitting with nonlinear least squares
- Baseline epidemic projections
- Early exploration of treatment and vector-control interventions
- SQLite and SQL-based exploratory analysis

> **Status:** Academic/research prototype. The model is intended for portfolio demonstration and scenario exploration, not operational public-health decision-making.

## Product idea

Public-health teams often need to decide where and when to intervene while information is incomplete. This prototype explores a product concept that would let a decision-maker compare epidemic trajectories across connected cities and evaluate intervention timing.

The intended product outcome is not simply a graph. It is a decision such as:

> “Which city should receive limited intervention resources first, and how much could an intervention reduce the projected burden?”

## Project structure

| File | Purpose |
|---|---|
| [`Simulation.py`](./Simulation.py) | Core transmission model, city-mobility model, parameter fitting, and plots |
| [`dataset_cities.csv`](./dataset_cities.csv) | Observed city-level epidemic time series used by the fitting functions |
| [`data EI.db`](./data%20EI.db) | SQLite database containing citizen and patient snapshots |
| [`data.sql`](./data.sql) | Exploratory SQL queries and aggregation examples |
| [`Dengue Epidemic Study.pdf`](./Dengue%20Epidemic%20Study.pdf) | Supporting study and project context |
| [`case-study.html`](./case-study.html) | Portfolio-facing product case study |

## Model overview

The simulation represents:

- Human population compartments by city and movement relationship
- Susceptible, infected, recovered, and severe/outcome states
- Susceptible and infected mosquito populations
- Human-to-mosquito and mosquito-to-human transmission
- Different transmission probabilities between cities
- Population movement between three fictional cities:
  - Noltrame
  - Sorya
  - Neamrolt

The model is solved as a system of ordinary differential equations using `scipy.integrate.odeint`.

The fitting functions use `scipy.optimize.least_squares` to compare model output with observed city data. The current implementation is exploratory and should be treated as a model prototype rather than a validated forecasting system.

## Requirements

- Python 3.9 or newer
- NumPy
- pandas
- Matplotlib
- SciPy

Install the Python dependencies with:

```bash
python -m pip install -r requirements.txt
```

For a reproducible project setup, create a virtual environment first:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run the simulation

From the project directory:

```bash
python Simulation.py
```

The script runs the fitting workflow for Noltrame, Sorya, and Neamrolt in
sequence, prints the fitted parameter vector for each city, and displays a
Matplotlib chart for each result. Close the current chart to continue to the
next city.

The CSV is loaded using a relative path, so run the command from the project directory.

## Launch the web interface

Install the dependencies, then run:

```bash
streamlit run app.py
```

The interface lets you select a city, run the fitting workflow with a reliable
optimizer limit, and compare observed data with the fitted trajectory.

## Run the automated tests

From the project directory:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

The tests cover the model's initial state, population aggregation, trajectory
shape and numerical values, conservation of the human compartments, and the
parameter-fitting pipeline. The fitting implementation is organized in
[`fitting.py`](./fitting.py), while [`Simulation.py`](./Simulation.py) keeps
the public `fitting_s`, `fitting_no`, and `fitting_ne` wrappers.

The fitting workflow only optimizes the parameters used by the original
city-specific workflows: `c` for Noltrame, `c`, `rho`, `p_h`, and `p_m` for
Sorya, and `c`, `p_21`, and `p_12` for Neamrolt. The other parameters remain
fixed at their documented initial values. A default limit of 100 optimizer
evaluations prevents an accidental unbounded run; callers can override it with
`max_nfev`.

Predictions are integrated from day 0 and plotted against the same `Date`
axis as the observations, so the fitted curves and observed points use a
consistent timeline.

## Explore the database

The SQLite database can be opened with any SQLite client. Its main tables include:

- `citizens`
- `patients_April_1`
- `patients_April_10`
- `patients_April_20`
- `patients_May_1`
- `patients_May_10`
- `patients_May_19`
- `patients_June_1`
- `patients_June_10`
- `data_utile`

The queries in [`data.sql`](./data.sql) show examples of aggregating patient states by date, city, and current state.

## Product workflow

The intended end-to-end workflow is:

```text
Patient snapshots
        ↓
City-level aggregation
        ↓
Observed epidemic time series
        ↓
Transmission model
        ↓
Parameter fitting
        ↓
Baseline vs intervention scenarios
        ↓
Decision support for public-health teams
```

## Important assumptions and limitations

This prototype has several limitations that should be understood before interpreting its output:

1. The cities and population data are fictional or simplified for the project.
2. The model parameters are not a substitute for epidemiological validation.
3. The current fitting workflow is exploratory and does not provide confidence intervals.
4. The observed dataset contains fields such as `Hospitalized`, while some internal variables use `D` naming. These concepts should be aligned before presenting results as mortality estimates.
5. Missing observations must be handled carefully during model fitting.
6. The model does not currently provide a production API, dashboard, user authentication, or automated data refresh.
7. Results should not be used to guide real-world medical or public-health action.

## Portfolio framing

This project is best presented as a **decision-support prototype**, not only as a mathematical simulation.

The product question is:

> How might a public-health team compare intervention timing and location when dengue risk moves between connected cities?

The next product increment would be a small dashboard that allows a user to:

- Select a city
- Choose an intervention type
- Set an intervention start date
- Compare baseline and intervention scenarios
- See peak infections, peak hospitalizations, and reduction versus baseline
- Review assumptions and uncertainty before making a recommendation

See [`case-study.html`](./case-study.html) for the portfolio presentation.

## Recommended technical next steps

- Separate model, fitting, plotting, and application code into modules.
- Add a `requirements.txt` or `pyproject.toml`.
- Add input validation and population-conservation checks.
- Resolve the naming distinction between hospitalization, severe cases, and deaths.
- Make the fitting loss function handle missing values explicitly.
- Add automated tests for the model equations and aggregation logic.
- Add a Streamlit dashboard for scenario comparison.
- Add uncertainty ranges and out-of-sample validation.

## License and data note

No license or public-data provenance is currently included in this prototype. Add an explicit license and document the origin, permitted use, and synthetic/real status of each dataset before publishing it publicly.
