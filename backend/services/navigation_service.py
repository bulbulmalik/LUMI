import logging
import math
from datetime import datetime

logger = logging.getLogger(__name__)


def start_navigation(user_id, command):
    """
    Start navigation session for user
    """
    logger.info(f"Starting navigation for user {user_id} with command: {command}")
    return "Navigation started. Please provide vision data for guidance."


class NavigationService:
    """
    Provides real-time navigation guidance:
    - Obstacle detection and avoidance instructions
    - Path analysis (clear / blocked / stairs / ramp)
    - Indoor navigation (room identification, door detection)
    - Outdoor navigation (sidewalk, crosswalk, traffic)
    - Distance estimation
    """

    # Obstacle severity levels
    SEVERITY_LOW = 'low'           # e.g. a small object on the side
    SEVERITY_MEDIUM = 'medium'     # e.g. a person walking towards you
    SEVERITY_HIGH = 'high'         # e.g. stairs directly ahead
    SEVERITY_CRITICAL = 'critical' # e.g. open manhole, moving vehicle

    def __init__(self):
        self.previous_frame_data = None
        self.navigation_history = []

    def analyze_path(self, vision_result: dict) -> dict:
        """
        Takes vision analysis result and provides navigation instructions.

        Returns:
            dict with 'instruction', 'obstacles', 'path_status', 'urgency'
        """
        description = vision_result.get('description', '')
        objects = vision_result.get('objects', [])
        warnings = vision_result.get('warnings', [])

        obstacles = self._identify_obstacles(description, objects, warnings)
        path_status = self._assess_path(description, obstacles)
        instruction = self._generate_instruction(path_status, obstacles)
        urgency = self._determine_urgency(obstacles)

        result = {
            'instruction': instruction,
            'audio_message': instruction,
            'obstacles': obstacles,
            'path_status': path_status,
            'urgency': urgency,  # 'normal', 'caution', 'warning', 'stop'
            'timestamp': datetime.utcnow().isoformat()
        }

        # Keep history for context
        self.navigation_history.append(result)
        if len(self.navigation_history) > 50:
            self.navigation_history = self.navigation_history[-50:]

        return result

    def _identify_obstacles(self, description: str, objects: list, warnings: list) -> list:
        """Identify and classify obstacles."""
        obstacles = []
        desc_lower = description.lower()

        obstacle_map = {
            'stairs': {'type': 'stairs', 'severity': self.SEVERITY_HIGH,
                       'action': 'There are stairs ahead. Please proceed carefully.'},
            'step': {'type': 'step', 'severity': self.SEVERITY_MEDIUM,
                     'action': 'There is a step ahead. Lift your foot.'},
            'curb': {'type': 'curb', 'severity': self.SEVERITY_MEDIUM,
                     'action': 'There is a curb ahead.'},
            'vehicle': {'type': 'vehicle', 'severity': self.SEVERITY_HIGH,
                        'action': 'Vehicle detected nearby. Stay on the sidewalk.'},
            'car': {'type': 'vehicle', 'severity': self.SEVERITY_HIGH,
                    'action': 'Car detected. Be cautious.'},
            'bicycle': {'type': 'bicycle', 'severity': self.SEVERITY_MEDIUM,
                        'action': 'Bicycle nearby. Stay to the side.'},
            'pole': {'type': 'pole', 'severity': self.SEVERITY_MEDIUM,
                     'action': 'There is a pole ahead. Step around it.'},
            'construction': {'type': 'construction', 'severity': self.SEVERITY_CRITICAL,
                             'action': 'Construction zone ahead. Please find an alternate path.'},
            'hole': {'type': 'hole', 'severity': self.SEVERITY_CRITICAL,
                     'action': 'Warning! There appears to be a hole in the path. Stop and go around it.'},
            'wet': {'type': 'wet_surface', 'severity': self.SEVERITY_MEDIUM,
                    'action': 'The floor appears wet. Walk carefully.'},
            'door': {'type': 'door', 'severity': self.SEVERITY_LOW,
                     'action': 'There is a door ahead.'},
            'person': {'type': 'person', 'severity': self.SEVERITY_LOW,
                       'action': 'Person nearby.'},
            'people': {'type': 'crowd', 'severity': self.SEVERITY_MEDIUM,
                       'action': 'Multiple people ahead. Navigate carefully.'},
            'dog': {'type': 'animal', 'severity': self.SEVERITY_MEDIUM,
                    'action': 'There is a dog nearby. Proceed with caution.'},
        }

        for keyword, info in obstacle_map.items():
            if keyword in desc_lower:
                obstacles.append({
                    'type': info['type'],
                    'severity': info['severity'],
                    'action': info['action'],
                    'keyword': keyword
                })

        return obstacles

    def _assess_path(self, description: str, obstacles: list) -> str:
        """Assess overall path status."""
        if not obstacles:
            return 'clear'

        severities = [o['severity'] for o in obstacles]

        if self.SEVERITY_CRITICAL in severities:
            return 'blocked'
        elif self.SEVERITY_HIGH in severities:
            return 'caution'
        elif self.SEVERITY_MEDIUM in severities:
            return 'minor_obstacles'
        else:
            return 'mostly_clear'

    def _generate_instruction(self, path_status: str, obstacles: list) -> str:
        """Generate a natural language navigation instruction."""
        if path_status == 'clear':
            return "Path is clear ahead. You can walk safely."

        if path_status == 'blocked':
            critical = [o for o in obstacles if o['severity'] == self.SEVERITY_CRITICAL]
            if critical:
                return f"Stop! {critical[0]['action']}"

        if path_status == 'caution':
            high = [o for o in obstacles if o['severity'] == self.SEVERITY_HIGH]
            if high:
                return f"Caution. {high[0]['action']}"

        # Combine actions for minor obstacles
        actions = [o['action'] for o in obstacles[:2]]  # max 2 to keep audio short
        return " ".join(actions)

    def _determine_urgency(self, obstacles: list) -> str:
        """Determine urgency level for audio feedback."""
        if not obstacles:
            return 'normal'

        severities = [o['severity'] for o in obstacles]

        if self.SEVERITY_CRITICAL in severities:
            return 'stop'
        elif self.SEVERITY_HIGH in severities:
            return 'warning'
        elif self.SEVERITY_MEDIUM in severities:
            return 'caution'
        return 'normal'

    def get_direction_guidance(self, current_location: dict, destination: dict) -> dict:
        """
        Provide turn-by-turn like guidance.

        Args:
            current_location: {'lat': float, 'lng': float}
            destination: {'lat': float, 'lng': float, 'name': str}
        """
        try:
            distance = self._calculate_distance(
                current_location['lat'], current_location['lng'],
                destination['lat'], destination['lng']
            )

            bearing = self._calculate_bearing(
                current_location['lat'], current_location['lng'],
                destination['lat'], destination['lng']
            )

            direction = self._bearing_to_direction(bearing)

            if distance < 5:
                message = f"You have arrived at {destination.get('name', 'your destination')}."
            elif distance < 20:
                message = f"You are very close to {destination.get('name', 'your destination')}. About {int(distance)} meters, keep going {direction}."
            else:
                message = f"{destination.get('name', 'Your destination')} is about {int(distance)} meters to the {direction}."

            return {
                'distance_meters': round(distance, 1),
                'direction': direction,
                'bearing': round(bearing, 1),
                'instruction': message,
                'audio_message': message,
                'arrived': distance < 5
            }
        except Exception as e:
            logger.error(f"Direction guidance error: {e}")
            return {
                'instruction': 'Unable to calculate direction at this time.',
                'audio_message': 'Sorry, I cannot determine the direction right now.'
            }

    def _calculate_distance(self, lat1, lon1, lat2, lon2) -> float:
        """Haversine formula for distance in meters."""
        R = 6371000  # Earth's radius in meters
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lon2 - lon1)

        a = (math.sin(d_phi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def _calculate_bearing(self, lat1, lon1, lat2, lon2) -> float:
        """Calculate bearing between two points."""
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        d_lambda = math.radians(lon2 - lon1)

        x = math.sin(d_lambda) * math.cos(phi2)
        y = (math.cos(phi1) * math.sin(phi2) -
             math.sin(phi1) * math.cos(phi2) * math.cos(d_lambda))

        bearing = math.degrees(math.atan2(x, y))
        return (bearing + 360) % 360

    def _bearing_to_direction(self, bearing: float) -> str:
        """Convert bearing to compass direction."""
        directions = [
            'north', 'north-east', 'east', 'south-east',
            'south', 'south-west', 'west', 'north-west'
        ]
        index = round(bearing / 45) % 8
        return directions[index]