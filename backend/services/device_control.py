import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DeviceControlService:
    """
    Helps control device interface through voice commands:
    - Volume control
    - Brightness adjustment
    - App launching
    - Screen reader interaction
    - Emergency calls
    - Reading notifications
    """

    SUPPORTED_COMMANDS = {
        'volume_up': 'Increase volume',
        'volume_down': 'Decrease volume',
        'volume_max': 'Set volume to maximum',
        'volume_mute': 'Mute the device',
        'brightness_up': 'Increase brightness',
        'brightness_down': 'Decrease brightness',
        'brightness_max': 'Set brightness to maximum',
        'flashlight_on': 'Turn on flashlight',
        'flashlight_off': 'Turn off flashlight',
        'call_emergency': 'Call emergency contact',
        'call_number': 'Call a specific number',
        'open_app': 'Open an application',
        'read_notifications': 'Read out notifications',
        'read_screen': 'Read the current screen content',
        'take_photo': 'Take a photo for analysis',
        'battery_status': 'Check battery level',
        'time_check': 'Tell the current time',
        'wifi_toggle': 'Toggle WiFi',
        'bluetooth_toggle': 'Toggle Bluetooth'
    }

    def __init__(self):
        pass

    def process_voice_command(self, command_text: str) -> dict:
        """
        Parse a natural language voice command and return the action to perform.

        Args:
            command_text: User's voice command text

        Returns:
            dict with 'action', 'parameters', 'audio_response'
        """
        command_lower = command_text.lower().strip()

        # ── Volume commands ──
        if any(w in command_lower for w in ['volume up', 'louder', 'increase volume', 'turn up']):
            return self._create_action('volume_up', {}, 'Increasing the volume.')

        if any(w in command_lower for w in ['volume down', 'quieter', 'decrease volume', 'turn down']):
            return self._create_action('volume_down', {}, 'Decreasing the volume.')

        if any(w in command_lower for w in ['max volume', 'full volume', 'volume maximum']):
            return self._create_action('volume_max', {}, 'Setting volume to maximum.')

        if any(w in command_lower for w in ['mute', 'silent', 'silence']):
            return self._create_action('volume_mute', {}, 'Muting the device.')

        # ── Brightness commands ──
        if any(w in command_lower for w in ['brightness up', 'brighter', 'increase brightness']):
            return self._create_action('brightness_up', {}, 'Increasing brightness.')

        if any(w in command_lower for w in ['brightness down', 'dimmer', 'decrease brightness']):
            return self._create_action('brightness_down', {}, 'Decreasing brightness.')

        if any(w in command_lower for w in ['max brightness', 'full brightness']):
            return self._create_action('brightness_max', {}, 'Setting brightness to maximum.')

        # ── Flashlight ──
        if any(w in command_lower for w in ['flashlight on', 'torch on', 'turn on flashlight', 'turn on torch']):
            return self._create_action('flashlight_on', {}, 'Turning on the flashlight.')

        if any(w in command_lower for w in ['flashlight off', 'torch off', 'turn off flashlight', 'turn off torch']):
            return self._create_action('flashlight_off', {}, 'Turning off the flashlight.')

        # ── Emergency ──
        if any(w in command_lower for w in ['emergency', 'help me', 'call for help', 'sos']):
            return self._create_action('call_emergency', {},
                                        'Calling your emergency contact right now. Stay calm.')

        # ── Phone calls ──
        if 'call' in command_lower:
            # Extract name or number
            name = command_lower.replace('call', '').strip()
            return self._create_action('call_number', {'contact': name},
                                        f'Calling {name}.')

        # ── App launching ──
        if any(w in command_lower for w in ['open', 'launch', 'start']):
            app_name = command_lower
            for word in ['open', 'launch', 'start', 'the', 'app']:
                app_name = app_name.replace(word, '')
            app_name = app_name.strip()
            return self._create_action('open_app', {'app_name': app_name},
                                        f'Opening {app_name}.')

        # ── Reading ──
        if any(w in command_lower for w in ['read notification', 'notifications', 'what are my notifications']):
            return self._create_action('read_notifications', {},
                                        'Reading your notifications.')

        if any(w in command_lower for w in ['read screen', 'what\'s on screen', 'what do you see']):
            return self._create_action('read_screen', {},
                                        'Let me read the screen for you.')

        # ── Camera ──
        if any(w in command_lower for w in ['take photo', 'take picture', 'capture', 'take a photo']):
            return self._create_action('take_photo', {},
                                        'Taking a photo now.')

        # ── Status checks ──
        if any(w in command_lower for w in ['battery', 'charge', 'power level']):
            return self._create_action('battery_status', {},
                                        'Checking battery status.')

        if any(w in command_lower for w in ['what time', 'current time', 'time please', "what's the time"]):
            now = datetime.now()
            time_str = now.strftime('%I:%M %p')
            date_str = now.strftime('%A, %B %d')
            return self._create_action('time_check', {},
                                        f'The time is {time_str}, {date_str}.')

        # ── Connectivity ──
        if 'wifi' in command_lower:
            return self._create_action('wifi_toggle', {},
                                        'Toggling WiFi.')

        if 'bluetooth' in command_lower:
            return self._create_action('bluetooth_toggle', {},
                                        'Toggling Bluetooth.')

        # ── Unknown command ──
        return self._create_action('unknown', {'raw_command': command_text},
                                    f"I didn't understand the command: {command_text}. "
                                    f"You can ask me to adjust volume, brightness, open apps, "
                                    f"read the screen, check battery, or call someone.")

    def _create_action(self, action: str, parameters: dict, audio_response: str) -> dict:
        return {
            'action': action,
            'parameters': parameters,
            'audio_message': audio_response,
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_available_commands(self) -> dict:
        """Return list of available commands for help."""
        help_text = "Here are things I can help you with: "
        commands = [
            "Adjust volume — say 'volume up' or 'volume down'",
            "Adjust brightness — say 'brighter' or 'dimmer'",
            "Flashlight — say 'flashlight on' or 'flashlight off'",
            "Emergency — say 'emergency' or 'help me'",
            "Call someone — say 'call' followed by the name",
            "Open an app — say 'open' followed by the app name",
            "Read notifications — say 'read notifications'",
            "Read screen — say 'read screen' or 'what do you see'",
            "Take a photo — say 'take photo'",
            "Check battery — say 'battery status'",
            "Check time — say 'what time is it'"
        ]
        help_text += ". ".join(commands) + "."

        return {
            'commands': self.SUPPORTED_COMMANDS,
            'audio_message': help_text
        }