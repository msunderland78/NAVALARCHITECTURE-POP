from .models import PopInput


KNOT_TO_MPS = 0.514444
GRAVITY_MPS2 = 9.80665
ATMOSPHERIC_PRESSURE_PA = 101325.0
PI = 3.141592653589793


def advance_speed_mps(case: PopInput) -> float:
    return case.shipSpeedKnots * KNOT_TO_MPS * (1.0 - case.wakeFraction)


def required_thrust_newtons(case: PopInput) -> float:
    return case.requiredThrustKn * 1000.0


def pitch_meters(diameter_meters: float, pitch_diameter_ratio: float) -> float:
    return diameter_meters * pitch_diameter_ratio


def revolutions_per_second(rpm: float) -> float:
    return rpm / 60.0


def advance_coefficient(advance_speed: float, revolutions_per_second_value: float, diameter_meters: float) -> float:
    return advance_speed / (revolutions_per_second_value * diameter_meters)


def thrust_coefficient(thrust_newtons: float, density_kg_m3: float, revolutions_per_second_value: float, diameter_meters: float) -> float:
    return thrust_newtons / (density_kg_m3 * revolutions_per_second_value ** 2 * diameter_meters ** 4)


def open_water_efficiency(advance_coefficient_value: float, thrust_coefficient_value: float, torque_coefficient_value: float) -> float:
    return advance_coefficient_value * thrust_coefficient_value / (2.0 * PI * torque_coefficient_value)


def pitch_type_efficiency_factor(case: PopInput) -> float:
    # 0.98 matches the legacy POP-1.5 string "Eta 0 Reduced by 2% When Controllable Pitch".
    # It is an empirical hub-loss allowance, not a physical CPP model. Real CPP losses depend on hub ratio.
    return 0.98 if case.pitchType == "controllable" else 1.0


def propeller_open_water_efficiency(case: PopInput, advance_coefficient_value: float, thrust_coefficient_value: float, torque_coefficient_value: float) -> float:
    return open_water_efficiency(advance_coefficient_value, thrust_coefficient_value, torque_coefficient_value) * pitch_type_efficiency_factor(case)


def cavitation_number(density_kg_m3: float, shaft_depth_meters: float, advance_speed: float, revolutions_per_second_value: float, diameter_meters: float) -> float:
    pressure = ATMOSPHERIC_PRESSURE_PA + density_kg_m3 * GRAVITY_MPS2 * shaft_depth_meters
    tangential_speed_07r = 0.7 * PI * revolutions_per_second_value * diameter_meters
    reference_speed_squared = advance_speed ** 2 + tangential_speed_07r ** 2
    return pressure / (0.5 * density_kg_m3 * reference_speed_squared)
