import json
from typing import Optional, List

# Data classes for aircraft performance
class CruisePoint:
    def __init__(self, altitude_ft: float, speed_ktas: float, fuelFlow_pph: float):
        self.altitude_ft = altitude_ft
        self.speed_ktas = speed_ktas
        self.fuelFlow_pph = fuelFlow_pph

class TemperatureData:
    def __init__(self, disa_c: float, cruise_points: List[CruisePoint]):
        self.disa_c = disa_c
        self.cruise_points = cruise_points

class WeightData:
    def __init__(self, weight_lbs: float, temperatures: List[TemperatureData]):
        self.weight_lbs = weight_lbs
        self.temperatures = temperatures

class AircraftPerformanceModel:
    def __init__(self, model: str, weights: List[WeightData]):
        self.model = model
        self.weights = weights

class AircraftPerformanceData:
    def __init__(self, cruise: List[AircraftPerformanceModel]):
        self.cruise = cruise

# Function to parse JSON data
def parse_json_to_objects(json_data: dict) -> AircraftPerformanceData:
    temp = json_data['cruise']
    cruise = []
    for model in temp:
        weights = []
        for weight in model['weights']:
            temperatures = []
            for temp_data in weight['temperatures']:
                cruise_points = [CruisePoint(**cp) for cp in temp_data['cruisePoints']]
                temperatures.append(TemperatureData(temp_data['disa_c'], cruise_points))
            weights.append(WeightData(weight['weight_lbs'], temperatures))
        cruise.append(AircraftPerformanceModel(model['modelName'], weights))
    return AircraftPerformanceData(cruise)

# Function to find the nearest value
def find_nearest_value(available_values: List[float], target: float) -> float:
    return min(available_values, key=lambda x: abs(x - target))

# Function to get fuel flow based on user input and nearest available data
def get_fuel_flow(data: AircraftPerformanceData, weight: float, altitude: float, temperature: float) -> Optional[float]:
    for model in data.cruise:
        # Find the closest weight
        available_weights = [weight_data.weight_lbs for weight_data in model.weights]
        closest_weight = find_nearest_value(available_weights, weight)

        for weight_data in model.weights:
            if weight_data.weight_lbs == closest_weight:
                # Find the closest temperature
                available_temperatures = [temp_data.disa_c for temp_data in weight_data.temperatures]
                closest_temperature = find_nearest_value(available_temperatures, temperature)

                for temp_data in weight_data.temperatures:
                    if temp_data.disa_c == closest_temperature:
                        # Find the closest altitude
                        available_altitudes = [cp.altitude_ft for cp in temp_data.cruise_points]
                        closest_altitude = find_nearest_value(available_altitudes, altitude)

                        for cruise_point in temp_data.cruise_points:
                            if cruise_point.altitude_ft == closest_altitude:
                                return cruise_point.fuelFlow_pph, cruise_point.speed_ktas

    return None


    

# Main function to run the program
def main():
    # Load the JSON data
    with open('Cirrus SR22 G1.json') as f:
        json_data = json.load(f)
    # Parse the JSON data into objects
    aircraft_data = parse_json_to_objects(json_data)

    # Get user input
    weight = float(input("Enter weight (lbs): "))
    altitude = float(input("Enter altitude (ft): "))
    temperature = float(input("Enter temperature (°C): "))
    distance = float(input("Enter the total distance (nautical miles): "))
    # Get the fuel flow based on user input
    fuel_flow, speed = get_fuel_flow(aircraft_data, weight, altitude, temperature)
    
    flight_time_hours = distance / speed
    print(f"with weight: {weight}, altitude: {altitude}, temperature: {temperature} and distance: {distance}")
    print(f"Closest Fuel Flow (pph): {fuel_flow}")
    print(f"Closest True Airspeed (knots): {speed}")
    print(f"Estimated Flight Time (hours): {flight_time_hours:.2f}")

if __name__ == "__main__":
    main()
