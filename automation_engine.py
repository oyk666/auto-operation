import pyautogui
import time
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1


class ActionType(Enum):
    CLICK = "click"
    TYPE = "type"
    KEY = "key"
    WAIT = "wait"
    SCREENSHOT = "screenshot"


@dataclass
class Action:
    action_type: ActionType
    config: Dict[str, Any]
    order: int


class AutomationEngine:
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.execution_callbacks: Dict[str, Callable] = {}
        self.current_action_index = 0
        self.actions: List[Action] = []

    def register_callback(self, event: str, callback: Callable):
        """Register callback for events: action_start, action_complete, action_error, execution_complete"""
        self.execution_callbacks[event] = callback

    def _emit_event(self, event: str, data: Any = None):
        """Emit event to registered callbacks"""
        if event in self.execution_callbacks:
            self.execution_callbacks[event](data)

    def load_actions(self, actions: List[Dict[str, Any]]):
        """Load actions from list of dictionaries"""
        self.actions = []
        sorted_actions = sorted(actions, key=lambda x: x.get('order', 0))
        for action_data in sorted_actions:
            action = Action(
                action_type=ActionType(action_data['action_type']),
                config=action_data['config'],
                order=action_data.get('order', 0)
            )
            self.actions.append(action)

    def _execute_click(self, config: Dict[str, Any]):
        """Execute click action"""
        x = config.get('x')
        y = config.get('y')
        button = config.get('button', 'left')
        if x is None or y is None:
            raise ValueError("Click action requires 'x' and 'y' coordinates")

        # Use mouseDown and mouseUp for more explicit click action
        pyautogui.moveTo(x, y)
        time.sleep(0.1) # Add a small delay before mouse down
        pyautogui.mouseDown(button=button)
        time.sleep(0.05) # Small delay to simulate press duration
        pyautogui.mouseUp(button=button)
        logger.info(f"Clicked at ({x}, {y}) with button {button}")

    def _execute_type(self, config: Dict[str, Any], context: Dict[str, str]):
        """Execute type action with variable substitution"""
        text = config.get('text', '')

        # Replace placeholders with context values
        for key, value in context.items():
            text = text.replace(f"{{{key}}}", str(value))

        interval = config.get('interval', 0.05)
        pyautogui.typewrite(text, interval=interval)
        logger.info(f"Typed: {text}")

    def _execute_wait(self, config: Dict[str, Any]):
        """Execute wait action"""
        duration = config.get('duration', 1)
        if duration < 0:
            raise ValueError("Wait duration must be positive")

        time.sleep(duration)
        logger.info(f"Waited {duration} seconds")

    def _execute_key(self, config: Dict[str, Any], context: Dict[str, str]):
        """Execute keyboard key/shortcut action"""
        key_text = str(config.get('key', '')).strip()
        if not key_text:
            raise ValueError("Key action requires 'key' value")

        # Support placeholders like {key_name} from batch context
        for key, value in context.items():
            key_text = key_text.replace(f"{{{key}}}", str(value))

        press_count = int(config.get('presses', 1))
        interval = float(config.get('interval', 0.05))
        if press_count < 1:
            raise ValueError("Key action presses must be >= 1")

        keys = [k.strip().lower() for k in key_text.split("+") if k.strip()]
        if not keys:
            raise ValueError("Key action has invalid key string")

        if len(keys) > 1:
            for _ in range(press_count):
                pyautogui.hotkey(*keys, interval=interval)
            logger.info(f"Pressed hotkey: {' + '.join(keys)} x{press_count}")
        else:
            pyautogui.press(keys[0], presses=press_count, interval=interval)
            logger.info(f"Pressed key: {keys[0]} x{press_count}")

    def _execute_screenshot(self, config: Dict[str, Any]):
        """Execute screenshot action"""
        filename = config.get('filename', f"screenshot_{int(time.time())}.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        logger.info(f"Screenshot saved to {filename}")

    def execute_action(self, action: Action, context: Dict[str, str] = None):
        """Execute single action"""
        context = context or {}

        try:
            if action.action_type == ActionType.CLICK:
                self._execute_click(action.config)
            elif action.action_type == ActionType.TYPE:
                self._execute_type(action.config, context)
            elif action.action_type == ActionType.KEY:
                self._execute_key(action.config, context)
            elif action.action_type == ActionType.WAIT:
                self._execute_wait(action.config)
            elif action.action_type == ActionType.SCREENSHOT:
                self._execute_screenshot(action.config)
            else:
                raise ValueError(f"Unknown action type: {action.action_type}")

            return True
        except Exception as e:
            logger.error(f"Action execution failed: {str(e)}")
            raise

    def execute_workflow(self, context: Dict[str, str] = None,
                        on_action_start: Callable = None,
                        on_action_complete: Callable = None,
                        on_error: Callable = None) -> bool:
        """Execute full workflow with all actions"""
        context = context or {}

        try:
            for idx, action in enumerate(self.actions):
                if not self.is_running:
                    break

                while self.is_paused:
                    time.sleep(0.1)

                self.current_action_index = idx

                if on_action_start:
                    on_action_start(action)

                self.execute_action(action, context)

                if on_action_complete:
                    on_action_complete(action)

            return True
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            if on_error:
                on_error(str(e))
            return False

    def pause(self):
        """Pause execution"""
        self.is_paused = True

    def resume(self):
        """Resume execution"""
        self.is_paused = False

    def stop(self):
        """Stop execution"""
        self.is_running = False
