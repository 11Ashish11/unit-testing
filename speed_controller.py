class SpeedController:
    """
    Controls the speed of an autonomous vehicle based on a set
    of input parameters.
    """
    
    def __init__(self, speed_limit=60):
        self.speed_limit = speed_limit
        self.current_speed = 0
        self.weather_factor = 1.0
        self.safety_mode = False

    def set_safety_mode(self, enabled: bool):
        """Enable or disable safety mode. Safety mode enforces stricter limits."""
        self.safety_mode = enabled

    def update_speed(self, road_condition:str, traffic_density:int, slope_angle:int=0) -> float:
        """
        Adjusts speed based on:
          - road_condition: str ('clear', 'wet', 'icy')
          - traffic_density: int (0–100)
          - slope_angle: int (-10 to +10, downhill/uphill)
        Returns the new target speed.
        """

        base_speed = self.speed_limit

        # Adjust for road condition (Bug 1: incorrect multiplier for 'wet')
        if road_condition == 'wet':
            self.weather_factor = 0.80  # should be 0.80
        elif road_condition == 'icy':
            self.weather_factor = 0.6
        elif road_condition == 'clear':
            self.weather_factor = 1.0
        else:
            raise ValueError("Invalid road condition")

        base_speed *= self.weather_factor

        # Adjust for traffic (Bug 2: wrong boundary check at 50)
        if traffic_density > 50:  # should be > 50
            if traffic_density > 80:
                base_speed -= 20
            else:
                base_speed -= 10

        # Adjust for slope (Bug 3: inverted slope adjustment)
        if slope_angle > 0:  # uphill
            base_speed += slope_angle  # should *increase* slightly to compensate
        elif slope_angle < 0:  # downhill
            base_speed -= abs(slope_angle)  # should *decrease* to maintain safety

        # Safety mode (Bug 4: wrong clamping)
        if self.safety_mode:
            base_speed = min(base_speed, self.speed_limit - 10)
        else:
            base_speed = max(0, min(base_speed, self.speed_limit))  # should clamp both min and max

        self.current_speed = base_speed
        return round(self.current_speed, 2)