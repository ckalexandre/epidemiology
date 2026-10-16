import math
import unittest

import numpy as np

import Simulation
from fitting import fit_city


class SimulationTests(unittest.TestCase):
    def test_reproduction_rate_is_non_negative(self):
        rates = [Simulation.reproduction_rate(day) for day in range(0, 301)]

        self.assertTrue(all(rate >= 0 for rate in rates))
        self.assertTrue(all(math.isfinite(rate) for rate in rates))

    def test_population_present_rows_match_resident_populations(self):
        workers = Simulation.population_presente()

        for city in Simulation.choix:
            self.assertEqual(set(workers[city]), set(Simulation.choix))
            self.assertAlmostEqual(
                sum(workers[city].values()),
                Simulation.population_residente[city],
            )

    def test_initial_state_has_expected_model_size(self):
        initial_state = Simulation.creation_Y0()

        self.assertEqual(len(initial_state), 42)
        self.assertTrue(np.all(np.isfinite(initial_state)))
        np.testing.assert_array_equal(
            initial_state[9:18],
            Simulation.i0,
        )

    def test_resolution_returns_finite_non_negative_trajectory(self):
        trajectory = Simulation.resolution()

        self.assertEqual(trajectory.shape, (len(Simulation.time_values), 42))
        self.assertTrue(np.all(np.isfinite(trajectory)))
        self.assertGreaterEqual(trajectory.min(), -1e-8)

    def test_human_compartments_are_conserved_by_derivatives(self):
        initial_state = np.array(Simulation.creation_Y0(), dtype=float)
        derivatives = np.array(
            Simulation.deriv_workers(
                initial_state,
                19,
                1,
                1 / 5,
                0.03,
                1 / 27,
                Simulation.p_h,
                Simulation.p_m,
                Simulation.p_11,
                Simulation.p_21,
                Simulation.p_12,
                Simulation.t_11,
                Simulation.t_21,
                Simulation.t_12,
            )
        )

        self.assertAlmostEqual(float(derivatives[:36].sum()), 0.0, places=8)

    def test_city_fit_returns_bounded_parameters_and_predictions(self):
        result, predictions = fit_city(
            "ne",
            start_day=6,
            initial_parameters=(1, 1 / 4, 0.03, 1 / 28, 0.1, 0.5, 1, 0.5, 0.9, 1, 0.6, 0.4),
            plot=False,
            max_nfev=2,
        )

        self.assertEqual(result.x.shape, (12,))
        self.assertTrue(result.success or result.status == 0)
        self.assertTrue(np.all(result.x >= 0))
        self.assertTrue(np.all(result.x[1:] <= 1))
        self.assertEqual(predictions.shape, (201, 42))
        self.assertTrue(np.all(np.isfinite(predictions)))

    def test_city_fit_prediction_starts_at_the_requested_day(self):
        result, predictions = fit_city(
            "ne",
            start_day=6,
            initial_parameters=(1, 1 / 4, 0.03, 1 / 28, 0.1, 0.5, 1, 0.5, 0.9, 1, 0.6, 0.4),
            plot=False,
            max_nfev=1,
        )

        import scipy.integrate as integrate

        expected_full = integrate.odeint(
            Simulation.deriv_workers,
            Simulation.creation_Y0(),
            np.arange(0, 201, dtype=float),
            args=tuple(result.x),
        )
        np.testing.assert_allclose(predictions[6], expected_full[6], rtol=1e-10, atol=1e-10)

    def test_public_fitting_wrapper_returns_result_without_plotting(self):
        result, predictions = Simulation.fitting_no(plot=False, max_nfev=1)

        self.assertEqual(result.x.shape, (12,))
        self.assertEqual(predictions.shape, (201, 42))

    def test_all_cities_fit_returns_three_results(self):
        results = Simulation.fit_all_cities(plot=False, max_nfev=1)

        self.assertEqual(set(results), {"Noltrame", "Sorya", "Neamrolt"})
        for result, predictions in results.values():
            self.assertEqual(result.x.shape, (12,))
            self.assertEqual(predictions.shape[1], 42)


if __name__ == "__main__":
    unittest.main()
