import os
from pathlib import Path

import numpy as np
import pytest

from floris.core.turbine.operation_models import POWER_SETPOINT_DEFAULT
from floris.core.turbine.tum_operation_model import TUMLossTurbine
from floris.utilities import cosd
from tests.conftest import SampleInputs, WIND_SPEEDS


def test_submodel_attributes():

    assert hasattr(TUMLossTurbine, "power")
    assert hasattr(TUMLossTurbine, "thrust_coefficient")
    assert hasattr(TUMLossTurbine, "axial_induction")

def test_TUMLossTurbine():

    # NOTE: These tests should be updated to reflect actual expected behavior
    # of the TUMLossTurbine model. Currently, match the CosineLossTurbine model.

    n_turbines = 1
    wind_speed = 10.0
    turbine_data = SampleInputs().turbine
    turbine_data["power_thrust_table"] = SampleInputs().tum_loss_turbine_power_thrust_table
    data_file_path = Path(__file__).resolve().parents[1] / "floris" / "turbine_library"
    turbine_data["power_thrust_table"]["cp_ct_data"] = np.load(
        data_file_path / turbine_data["power_thrust_table"]["cp_ct_data_file"]
    )

    yaw_angles_nom = 0 * np.ones((1, n_turbines))
    tilt_angles_nom = turbine_data["power_thrust_table"]["ref_tilt"] * np.ones((1, n_turbines))
    power_setpoints_nom = POWER_SETPOINT_DEFAULT * np.ones((1, n_turbines))
    yaw_angles_test = 20 * np.ones((1, n_turbines))
    tilt_angles_test = 0 * np.ones((1, n_turbines))


    # Check that power works as expected
    TUMLossTurbine.power(
        power_thrust_table=turbine_data["power_thrust_table"],
        velocities=wind_speed * np.ones((1, n_turbines, 3, 3)), # 1 findex, 1 turbine, 3x3 grid
        air_density=turbine_data["power_thrust_table"]["ref_air_density"], # Matches ref_air_density
        yaw_angles=yaw_angles_nom,
        power_setpoints=power_setpoints_nom,
        tilt_angles=tilt_angles_nom,
        tilt_interp=None
    )
    # truth_index = turbine_data["power_thrust_table"]["wind_speed"].index(wind_speed)
    # baseline_power = turbine_data["power_thrust_table"]["power"][truth_index] * 1000
    # assert np.allclose(baseline_power, test_power)

    # Check that yaw and tilt angle have an effect
    TUMLossTurbine.power(
        power_thrust_table=turbine_data["power_thrust_table"],
        velocities=wind_speed * np.ones((1, n_turbines, 3, 3)), # 1 findex, 1 turbine, 3x3 grid
        air_density=turbine_data["power_thrust_table"]["ref_air_density"], # Matches ref_air_density
        yaw_angles=yaw_angles_test,
        power_setpoints=power_setpoints_nom,
        tilt_angles=tilt_angles_test,
        tilt_interp=None
    )
    #assert test_power < baseline_power

    # Check that a lower air density decreases power appropriately
    TUMLossTurbine.power(
        power_thrust_table=turbine_data["power_thrust_table"],
        velocities=wind_speed * np.ones((1, n_turbines, 3, 3)), # 1 findex, 1 turbine, 3x3 grid
        air_density=1.1,
        yaw_angles=yaw_angles_nom,
        power_setpoints=power_setpoints_nom,
        tilt_angles=tilt_angles_nom,
        tilt_interp=None
    )
    #assert test_power < baseline_power


    # Check that thrust coefficient works as expected
    TUMLossTurbine.thrust_coefficient(
        power_thrust_table=turbine_data["power_thrust_table"],
        velocities=wind_speed * np.ones((1, n_turbines, 3, 3)), # 1 findex, 1 turbine, 3x3 grid
        air_density=1.1, # Unused
        yaw_angles=yaw_angles_nom,
        power_setpoints=power_setpoints_nom,
        tilt_angles=tilt_angles_nom,
        tilt_interp=None
    )
    #baseline_Ct = turbine_data["power_thrust_table"]["thrust_coefficient"][truth_index]
    #assert np.allclose(baseline_Ct, test_Ct)

    # Check that yaw and tilt angle have the expected effect
    TUMLossTurbine.thrust_coefficient(
        power_thrust_table=turbine_data["power_thrust_table"],
        velocities=wind_speed * np.ones((1, n_turbines, 3, 3)), # 1 findex, 1 turbine, 3x3 grid
        air_density=1.1, # Unused
        yaw_angles=yaw_angles_test,
        power_setpoints=power_setpoints_nom,
        tilt_angles=tilt_angles_test,
        tilt_interp=None
    )
    #absolute_tilt = tilt_angles_test - turbine_data["power_thrust_table"]["ref_tilt"]
    #assert test_Ct == baseline_Ct * cosd(yaw_angles_test) * cosd(absolute_tilt)


    # Check that thrust coefficient works as expected
    TUMLossTurbine.axial_induction(
        power_thrust_table=turbine_data["power_thrust_table"],
        velocities=wind_speed * np.ones((1, n_turbines, 3, 3)), # 1 findex, 1 turbine, 3x3 grid
        air_density=1.1, # Unused
        yaw_angles=yaw_angles_nom,
        power_setpoints=power_setpoints_nom,
        tilt_angles=tilt_angles_nom,
        tilt_interp=None
    )
    (
        cosd(yaw_angles_nom)
        * cosd(tilt_angles_nom - turbine_data["power_thrust_table"]["ref_tilt"])
    )
    # baseline_ai = (
    #     1 - np.sqrt(1 - turbine_data["power_thrust_table"]["thrust_coefficient"][truth_index])
    # ) / 2 / baseline_misalignment_loss
    # assert np.allclose(baseline_ai, test_ai)

    # Check that yaw and tilt angle have the expected effect
    TUMLossTurbine.axial_induction(
        power_thrust_table=turbine_data["power_thrust_table"],
        velocities=wind_speed * np.ones((1, n_turbines, 3, 3)), # 1 findex, 1 turbine, 3x3 grid
        air_density=1.1, # Unused
        yaw_angles=yaw_angles_test,
        power_setpoints=power_setpoints_nom,
        tilt_angles=tilt_angles_test,
        tilt_interp=None
    )
    tilt_angles_test - turbine_data["power_thrust_table"]["ref_tilt"]
    #assert test_Ct == baseline_Ct * cosd(yaw_angles_test) * cosd(absolute_tilt)

def test_TUMLossTurbine_regression():
    """
    Adding a regression test so that we can work with the model and stay confident that results
    are not changing.
    """

    n_turbines = 1
    wind_speed = 10.0
    turbine_data = SampleInputs().turbine
    turbine_data["power_thrust_table"] = SampleInputs().tum_loss_turbine_power_thrust_table
    data_file_path = Path(__file__).resolve().parents[1] / "floris" / "turbine_library"
    turbine_data["power_thrust_table"]["cp_ct_data"] = np.load(
        data_file_path / turbine_data["power_thrust_table"]["cp_ct_data_file"]
    )

    N_test = 20
    tilt_angles_nom = turbine_data["power_thrust_table"]["ref_tilt"] * np.ones((N_test, n_turbines))
    power_setpoints_nom = POWER_SETPOINT_DEFAULT * np.ones((N_test, n_turbines))

    yaw_max = 30 # Maximum yaw to test
    yaw_angles_test = np.linspace(-yaw_max, yaw_max, N_test).reshape(-1,1)

    power_base = np.array([
        2395927.92868139,
        2527726.50920564,
        2644989.24683195,
        2748134.16149699,
        2837129.46422222,
        2911510.74331788,
        2971011.54743479,
        3015566.03081713,
        3045213.16926206,
        3060014.98468406,
        3060014.98468406,
        3045213.16926206,
        3015566.03081713,
        2971011.54743479,
        2911510.74331788,
        2837129.46422222,
        2748134.16149699,
        2644989.24683195,
        2527726.50920564,
        2395927.92868139,
    ])

    thrust_coefficient_base = np.array([
        0.65966861,
        0.68401903,
        0.70532378,
        0.72373957,
        0.73936337,
        0.75223810,
        0.76241954,
        0.76997771,
        0.77497954,
        0.77746593,
        0.77746593,
        0.77497954,
        0.76997771,
        0.76241954,
        0.75223810,
        0.73936337,
        0.72373957,
        0.70532378,
        0.68401903,
        0.65966861,
    ])

    axial_induction_base = np.array([
        0.20864674,
        0.21929141,
        0.22894655,
        0.23757787,
        0.24512918,
        0.25152384,
        0.25669950,
        0.26061385,
        0.26323979,
        0.26455600,
        0.26455600,
        0.26323979,
        0.26061385,
        0.25669950,
        0.25152384,
        0.24512918,
        0.23757787,
        0.22894655,
        0.21929141,
        0.20864674,
    ])

    power = TUMLossTurbine.power(
        power_thrust_table=turbine_data["power_thrust_table"],
        velocities=wind_speed * np.ones((N_test, n_turbines, 3, 3)), # 1 findex, 1 turbine, 3x3 grid
        air_density=1.1,
        yaw_angles=yaw_angles_test,
        power_setpoints=power_setpoints_nom,
        tilt_angles=tilt_angles_nom,
        tilt_interp=None
    ).squeeze()

    thrust_coefficient = TUMLossTurbine.thrust_coefficient(
        power_thrust_table=turbine_data["power_thrust_table"],
        velocities=wind_speed * np.ones((N_test, n_turbines, 3, 3)), # 1 findex, 1 turbine, 3x3 grid
        air_density=1.1,
        yaw_angles=yaw_angles_test,
        power_setpoints=power_setpoints_nom,
        tilt_angles=tilt_angles_nom,
        tilt_interp=None
    ).squeeze()

    axial_induction = TUMLossTurbine.axial_induction(
        power_thrust_table=turbine_data["power_thrust_table"],
        velocities=wind_speed * np.ones((N_test, n_turbines, 3, 3)), # 1 findex, 1 turbine, 3x3 grid
        air_density=1.1,
        yaw_angles=yaw_angles_test,
        power_setpoints=power_setpoints_nom,
        tilt_angles=tilt_angles_nom,
        tilt_interp=None
    ).squeeze()

    # print(power)
    # print(thrust_coefficient)
    # print(axial_induction)

    assert np.allclose(power, power_base)
    assert np.allclose(thrust_coefficient, thrust_coefficient_base)
    assert np.allclose(axial_induction, axial_induction_base)

def test_TUMLossTurbine_integration():
    """
    Test the TUMLossTurbine model with a range of wind speeds, and then
    whether it works regardless of number of grid points.
    """

    n_turbines = 1
    turbine_data = SampleInputs().turbine
    turbine_data["power_thrust_table"] = SampleInputs().tum_loss_turbine_power_thrust_table
    data_file_path = Path(__file__).resolve().parents[1] / "floris" / "turbine_library"
    turbine_data["power_thrust_table"]["cp_ct_data"] = np.load(
        data_file_path / turbine_data["power_thrust_table"]["cp_ct_data_file"]
    )

    N_test = 20
    tilt_angles_nom = turbine_data["power_thrust_table"]["ref_tilt"] * np.ones((N_test, n_turbines))
    power_setpoints_nom = POWER_SETPOINT_DEFAULT * np.ones((N_test, n_turbines))

    # Check runs over a range of wind speeds
    wind_speeds = np.linspace(1, 30, N_test)
    wind_speeds = np.tile(wind_speeds[:,None,None,None], (1, 1, 3, 3))

    power0 = TUMLossTurbine.power(
        power_thrust_table=turbine_data["power_thrust_table"],
        velocities=wind_speeds,
        air_density=1.1,
        yaw_angles=0 * np.ones((N_test, n_turbines)),
        power_setpoints=power_setpoints_nom,
        tilt_angles=tilt_angles_nom,
        tilt_interp=None
    ).squeeze()

    power20 = TUMLossTurbine.power(
        power_thrust_table=turbine_data["power_thrust_table"],
        velocities=wind_speeds,
        air_density=1.1,
        yaw_angles=20 * np.ones((N_test, n_turbines)),
        power_setpoints=power_setpoints_nom,
        tilt_angles=tilt_angles_nom,
        tilt_interp=None
    ).squeeze()

    assert (power0 - power20 >= -1e6).all()

    # Won't compare; just checking runs as expected
    TUMLossTurbine.thrust_coefficient(
        power_thrust_table=turbine_data["power_thrust_table"],
        velocities=wind_speeds,
        air_density=1.1,
        yaw_angles=0 * np.ones((N_test, n_turbines)),
        power_setpoints=power_setpoints_nom,
        tilt_angles=tilt_angles_nom,
        tilt_interp=None
    ).squeeze()

    TUMLossTurbine.thrust_coefficient(
        power_thrust_table=turbine_data["power_thrust_table"],
        velocities=wind_speeds,
        air_density=1.1,
        yaw_angles=20 * np.ones((N_test, n_turbines)),
        power_setpoints=power_setpoints_nom,
        tilt_angles=tilt_angles_nom,
        tilt_interp=None
    ).squeeze()

    # Try a set of wind speeds for 5 grid points; then 2; then a single grid point
    # without any shear
    N_test = 1
    n_turbines = 1
    tilt_angles_nom = turbine_data["power_thrust_table"]["ref_tilt"] * np.ones((N_test, n_turbines))
    power_setpoints_nom = POWER_SETPOINT_DEFAULT * np.ones((N_test, n_turbines))


    wind_speeds = 10.0 * np.ones((N_test, n_turbines, 5, 5))
    power5gp = TUMLossTurbine.power(
        power_thrust_table=turbine_data["power_thrust_table"],
        velocities=wind_speeds,
        air_density=1.1,
        yaw_angles=0 * np.ones((N_test, n_turbines)),
        power_setpoints=power_setpoints_nom,
        tilt_angles=tilt_angles_nom,
        tilt_interp=None
    ).squeeze()

    wind_speeds = 10.0 * np.ones((N_test, n_turbines, 2, 2))
    power2gp = TUMLossTurbine.power(
        power_thrust_table=turbine_data["power_thrust_table"],
        velocities=wind_speeds,
        air_density=1.1,
        yaw_angles=0 * np.ones((N_test, n_turbines)),
        power_setpoints=power_setpoints_nom,
        tilt_angles=tilt_angles_nom,
        tilt_interp=None
    ).squeeze()

    assert np.allclose(power5gp, power2gp)

    # No shear information for the TUM model to use
    wind_speeds = 10.0 * np.ones((N_test, n_turbines, 1, 1))
    with pytest.raises(ValueError):
        TUMLossTurbine.power(
            power_thrust_table=turbine_data["power_thrust_table"],
            velocities=wind_speeds,
            air_density=1.1,
            yaw_angles=0 * np.ones((N_test, n_turbines)),
            power_setpoints=power_setpoints_nom,
            tilt_angles=tilt_angles_nom,
            tilt_interp=None
        )
