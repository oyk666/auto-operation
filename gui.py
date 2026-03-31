import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import threading
import tkinter as tk
import re
import csv
from typing import List, Dict, Any, Optional
from automation_engine import AutomationEngine, ActionType
from supabase_client import SupabaseManager
from coordinate_picker import PickerDialog
import json


class ActionListFrame(ctk.CTkFrame):
    """Frame for displaying and managing actions"""

    def __init__(self, parent, on_action_changed=None):
        super().__init__(parent)
        self.on_action_changed = on_action_changed
        self.actions: List[Dict[str, Any]] = []
        self._suspend_change_callback = False

        # Title
        title = ctk.CTkLabel(self, text="Actions", font=("Arial", 14, "bold"))
        title.pack(pady=10)

        # Actions list
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=("white", "#2b2b2b"))
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Add action button
        self.add_btn = ctk.CTkButton(
            self,
            text="+ Add Action",
            command=self._add_action,
            fg_color=("#27ae60", "#27ae60"),
            hover_color=("#229954", "#229954")
        )
        self.add_btn.pack(pady=10, padx=10, fill="x")

    def _add_action(self):
        """Open dialog to add a new action."""
        ActionBuilder(self, self)

    def add_action(self, action_type: str, config: Dict[str, Any]):
        """Add action to list"""
        action = {
            "action_type": action_type,
            "config": config,
            "order": len(self.actions)
        }
        self.actions.append(action)
        print(f"DEBUG: Added action {action_type}, total actions: {len(self.actions)}")
        self._refresh_display()
        if self.on_action_changed and not self._suspend_change_callback:
            print("DEBUG: Calling on_action_changed callback")
            self.on_action_changed()

    def remove_action(self, index: int):
        """Remove action from list"""
        if 0 <= index < len(self.actions):
            self.actions.pop(index)
            # Reorder
            for i, action in enumerate(self.actions):
                action['order'] = i
            self._refresh_display()
            if self.on_action_changed and not self._suspend_change_callback:
                self.on_action_changed()

    def _move_action(self, index: int, direction: int):
        """Move action up or down"""
        new_index = index + direction
        if 0 <= new_index < len(self.actions):
            # Swap actions
            self.actions[index], self.actions[new_index] = self.actions[new_index], self.actions[index]
            # Reorder
            for i, action in enumerate(self.actions):
                action['order'] = i
            self._refresh_display()
            if self.on_action_changed and not self._suspend_change_callback:
                self.on_action_changed()

    def _edit_action(self, index: int):
        """Edit existing action"""
        action = self.actions[index]
        ActionBuilder(self, self, edit_action=action, edit_index=index)

    def _refresh_display(self):
        """Refresh action list display"""
        # Clear existing
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        # Display actions
        for idx, action in enumerate(self.actions):
            self._create_action_widget(idx, action)

    def _create_action_widget(self, idx: int, action: Dict[str, Any]):
        """Create widget for single action"""
        frame = ctk.CTkFrame(self.list_frame, fg_color=("gray95", "#3b3b3b"), border_width=1, border_color=("gray70", "#555555"))
        frame.pack(fill="x", pady=5)

        # Content
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(fill="x", expand=True, padx=10, pady=8, side="left")

        # Type and summary
        action_type = action['action_type']
        summary = self._get_action_summary(action)

        type_label = ctk.CTkLabel(
            content_frame,
            text=f"{idx + 1}. {action_type.upper()}",
            font=("Arial", 11, "bold"),
            text_color=("#222222", "#eeeeee")
        )
        type_label.pack(anchor="w")

        summary_label = ctk.CTkLabel(
            content_frame,
            text=summary,
            font=("Arial", 10),
            text_color=("gray50", "gray70")
        )
        summary_label.pack(anchor="w")

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(padx=10, pady=8, side="right")

        # Move up button
        if idx > 0:
            up_btn = ctk.CTkButton(
                button_frame,
                text="↑",
                command=lambda: self._move_action(idx, -1),
                width=35,
                height=25,
                font=("Arial", 10, "bold"),
                fg_color=("#3498db", "#3498db"),
                hover_color=("#2980b9", "#2980b9")
            )
            up_btn.pack(side="left", padx=2)

        # Move down button
        if idx < len(self.actions) - 1:
            down_btn = ctk.CTkButton(
                button_frame,
                text="↓",
                command=lambda: self._move_action(idx, 1),
                width=35,
                height=25,
                font=("Arial", 10, "bold"),
                fg_color=("#3498db", "#3498db"),
                hover_color=("#2980b9", "#2980b9")
            )
            down_btn.pack(side="left", padx=2)

        # Edit button
        edit_btn = ctk.CTkButton(
            button_frame,
            text="Edit",
            command=lambda: self._edit_action(idx),
            width=50,
            height=25,
            font=("Arial", 9),
            fg_color=("#f39c12", "#f39c12"),
            hover_color=("#e67e22", "#e67e22")
        )
        edit_btn.pack(side="left", padx=2)

        # Delete button
        delete_btn = ctk.CTkButton(
            button_frame,
            text="Delete",
            command=lambda: self.remove_action(idx),
            width=60,
            height=25,
            font=("Arial", 9),
            fg_color=("#e74c3c", "#e74c3c"),
            hover_color=("#c0392b", "#c0392b")
        )
        delete_btn.pack(side="left", padx=2)

    def _get_action_summary(self, action: Dict[str, Any]) -> str:
        """Get human-readable summary of action"""
        config = action.get('config', {})
        action_type = action['action_type']

        if action_type == "click":
            return f"Click at ({config.get('x', '?')}, {config.get('y', '?')})"
        elif action_type == "type":
            text = config.get('text', '')[:50]
            return f"Type: {text}..."
        elif action_type == "key":
            key = config.get('key', 'enter')
            presses = config.get('presses', 1)
            return f"Press key: {key} x{presses}"
        elif action_type == "wait":
            return f"Wait {config.get('duration', 1)}s"
        elif action_type == "screenshot":
            return f"Take screenshot: {config.get('filename', 'screenshot.png')}"
        return "Unknown action"

    def get_actions(self) -> List[Dict[str, Any]]:
        """Get all actions"""
        return self.actions

    def clear_actions(self):
        """Clear all actions"""
        self.actions = []
        self._refresh_display()

    def set_actions(self, actions: List[Dict[str, Any]]):
        """Replace actions in one batch to avoid repeated full redraws."""
        normalized_actions: List[Dict[str, Any]] = []
        for i, action in enumerate(actions):
            normalized_actions.append({
                "action_type": action.get("action_type", ""),
                "config": action.get("config", {}),
                "order": i
            })

        self._suspend_change_callback = True
        self.actions = normalized_actions
        self._refresh_display()
        self._suspend_change_callback = False

        if self.on_action_changed:
            self.on_action_changed()


class ActionBuilder(ctk.CTkToplevel):
    """Dialog for building actions"""
    VALID_KEY_NAMES = {
        "enter", "tab", "esc", "escape", "space", "backspace", "delete", "del",
        "up", "down", "left", "right", "home", "end", "pageup", "pagedown",
        "insert", "shift", "ctrl", "alt", "win", "command", "option",
        "capslock", "numlock", "scrolllock", "pause", "printscreen",
        "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
    }
    ALL_KEYS = sorted(
        VALID_KEY_NAMES
        .union({chr(i) for i in range(ord("a"), ord("z") + 1)})
        .union({str(i) for i in range(10)})
    )

    def __init__(self, parent, action_list_frame: ActionListFrame, edit_action=None, edit_index=None):
        super().__init__(parent)
        self.title("Edit Action" if edit_action else "Add Action")
        self.geometry("500x400")
        self.resizable(False, False)
        self.action_list_frame = action_list_frame
        self.edit_action = edit_action
        self.edit_index = edit_index
        
        # Make window topmost
        self.attributes('-topmost', True)
        self.focus_force()
        
        # Track if dialog is being destroyed to avoid callback issues
        self._is_destroying = False

        # Action type selection
        type_frame = ctk.CTkFrame(self)
        type_frame.pack(fill="x", padx=20, pady=20)

        type_label = ctk.CTkLabel(type_frame, text="Select Action Type:", font=("Arial", 12, "bold"))
        type_label.pack(anchor="w")

        self.action_type = ctk.CTkComboBox(
            type_frame,
            values=["click", "type", "key", "wait", "screenshot"],
            command=self._on_type_changed,
            state="readonly"
        )
        self.action_type.pack(fill="x", pady=10)
        
        # Set action type if editing
        if edit_action:
            self.action_type.set(edit_action['action_type'])
        else:
            self.action_type.set("click")

        # Config frame (will be replaced based on type)
        self.config_frame = ctk.CTkFrame(self)
        self.config_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=20)

        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Changes" if edit_action else "Add Action",
            command=self._save_action,
            fg_color=("#27ae60", "#27ae60"),
            hover_color=("#229954", "#229954")
        )
        save_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=5)

        self._on_type_changed(self.action_type.get())
        
    def destroy(self):
        """Override destroy to prevent callback issues"""
        if self._is_destroying:
            return
        self._is_destroying = True
        try:
            super().destroy()
        except Exception:
            pass

    def _on_type_changed(self, value: str):
        """Handle action type change"""
        # Clear existing
        for widget in self.config_frame.winfo_children():
            widget.destroy()

        if value == "click":
            self._build_click_config()
        elif value == "type":
            self._build_type_config()
        elif value == "key":
            self._build_key_config()
        elif value == "wait":
            self._build_wait_config()
        elif value == "screenshot":
            self._build_screenshot_config()

    def _build_key_config(self):
        """Build keyboard action config"""
        label = ctk.CTkLabel(
            self.config_frame,
            text="Keyboard Key / Shortcut",
            font=("Arial", 12, "bold")
        )
        label.pack(anchor="w", pady=(0, 10))

        info = ctk.CTkLabel(
            self.config_frame,
            text="Use dropdown or input key, then click Add. Supports ctrl+c, alt+f4",
            text_color=("gray50", "gray70"),
            font=("Arial", 9)
        )
        info.pack(anchor="w", pady=(0, 8))

        key_row = ctk.CTkFrame(self.config_frame)
        key_row.pack(fill="x", pady=5)
        ctk.CTkLabel(key_row, text="Key:", width=70).pack(side="left")
        self.key_input = ctk.CTkComboBox(
            key_row,
            values=self.ALL_KEYS,
            width=220,
            state="normal"
        )
        self.key_input.pack(side="left", padx=6)
        self.key_input.set("enter")
        self.key_input.bind("<KeyRelease>", self._on_key_input_changed)
        self.key_input.bind("<Return>", self._on_key_input_enter)
        self.key_input.bind("<FocusIn>", self._on_key_input_focus_in)
        self.key_input.bind("<Escape>", self._on_key_input_escape)

        add_btn = ctk.CTkButton(key_row, text="+ Add", width=70, command=self._add_key_token)
        add_btn.pack(side="left", padx=4)
        remove_btn = ctk.CTkButton(key_row, text="← Undo", width=70, command=self._remove_last_key_token)
        remove_btn.pack(side="left", padx=4)

        # Search dropdown suggestions
        self.key_suggestion_frame = ctk.CTkFrame(self.config_frame)
        self.key_suggestion_list = tk.Listbox(self.key_suggestion_frame, height=6)
        self.key_suggestion_list.pack(fill="both", expand=True)
        self.key_suggestion_list.bind("<<ListboxSelect>>", self._on_key_suggestion_select)
        self.key_suggestion_list.bind("<Return>", self._on_key_suggestion_enter)
        self.key_suggestion_list.bind("<ButtonRelease-1>", self._on_key_suggestion_click)
        self.key_suggestion_visible = False

        preview_row = ctk.CTkFrame(self.config_frame)
        preview_row.pack(fill="x", pady=5)
        ctk.CTkLabel(preview_row, text="Combo:", width=70).pack(side="left")
        self.key_preview = ctk.CTkEntry(preview_row, width=330)
        self.key_preview.pack(side="left", padx=6)

        count_row = ctk.CTkFrame(self.config_frame)
        count_row.pack(fill="x", pady=5)
        ctk.CTkLabel(count_row, text="Presses:", width=70).pack(side="left")
        self.key_presses = ctk.CTkEntry(count_row, width=100)
        self.key_presses.pack(side="left", padx=6)
        self.key_presses.insert(0, "1")

        ctk.CTkLabel(count_row, text="Interval(s):", width=90).pack(side="left", padx=(10, 0))
        self.key_interval = ctk.CTkEntry(count_row, width=100)
        self.key_interval.pack(side="left", padx=6)
        self.key_interval.insert(0, "0.05")

        self.key_tokens: List[str] = []

        if self.edit_action and self.edit_action['action_type'] == 'key':
            existing_key = str(self.edit_action['config'].get('key', 'enter')).strip()
            if existing_key:
                self.key_tokens = [token.strip() for token in existing_key.split("+") if token.strip()]
                if not self.key_tokens:
                    self.key_tokens = [existing_key]
            self._refresh_key_preview()
            self.key_presses.delete(0, "end")
            self.key_presses.insert(0, str(self.edit_action['config'].get('presses', 1)))
            self.key_interval.delete(0, "end")
            self.key_interval.insert(0, str(self.edit_action['config'].get('interval', 0.05)))
        else:
            self._refresh_key_preview()

    def _normalize_key_token(self, raw: str) -> str:
        return raw.strip().lower()

    def _is_valid_key_token(self, token: str) -> bool:
        if not token:
            return False
        if len(token) == 1 and token.isprintable():
            return True
        return token in self.VALID_KEY_NAMES

    def _refresh_key_preview(self):
        combo = "+".join(self.key_tokens)
        self.key_preview.delete(0, "end")
        self.key_preview.insert(0, combo)

    def _on_key_input_changed(self, event=None):
        typed = self._normalize_key_token(self.key_input.get())
        if not typed:
            filtered = self.ALL_KEYS
        else:
            filtered = [key for key in self.ALL_KEYS if typed in key]
            if not filtered:
                filtered = []

        self.key_input.configure(values=(filtered[:200] if filtered else self.ALL_KEYS[:200]))
        self.key_input.set(typed)
        self._show_key_suggestions(filtered)

    def _on_key_input_focus_in(self, event=None):
        typed = self._normalize_key_token(self.key_input.get())
        filtered = [key for key in self.ALL_KEYS if typed in key] if typed else self.ALL_KEYS
        self._show_key_suggestions(filtered)

    def _on_key_input_escape(self, event=None):
        self._hide_key_suggestions()
        return "break"

    def _show_key_suggestions(self, options: List[str]):
        self.key_suggestion_list.delete(0, "end")
        for key in options[:80]:
            self.key_suggestion_list.insert("end", key)

        if options:
            if not self.key_suggestion_visible:
                self.key_suggestion_frame.pack(fill="x", padx=4, pady=(0, 6), after=self.key_input.master)
                self.key_suggestion_visible = True
            self.key_suggestion_list.selection_clear(0, "end")
            self.key_suggestion_list.selection_set(0)
        else:
            self._hide_key_suggestions()

    def _hide_key_suggestions(self):
        if self.key_suggestion_visible:
            self.key_suggestion_frame.pack_forget()
            self.key_suggestion_visible = False

    def _on_key_suggestion_select(self, event=None):
        selected = self.key_suggestion_list.curselection()
        if not selected:
            return
        value = self.key_suggestion_list.get(selected[0])
        self.key_input.set(value)

    def _on_key_suggestion_click(self, event=None):
        self._on_key_suggestion_select()
        self.key_input.focus_set()
        self._hide_key_suggestions()

    def _on_key_suggestion_enter(self, event=None):
        self._on_key_suggestion_select()
        self.key_input.focus_set()
        self._hide_key_suggestions()
        return "break"

    def _on_key_input_enter(self, event=None):
        self._add_key_token()
        return "break"

    def _add_key_token(self):
        token = self._normalize_key_token(self.key_input.get())
        if not self._is_valid_key_token(token):
            CTkMessagebox(
                title="Invalid key",
                message=f"Unsupported key: {token or '(empty)'}",
                icon="cancel"
            )
            return
        self.key_tokens.append(token)
        self._refresh_key_preview()
        self.key_input.set("")
        self._hide_key_suggestions()

    def _remove_last_key_token(self):
        if self.key_tokens:
            self.key_tokens.pop()
            self._refresh_key_preview()

    def _build_click_config(self):
        """Build click action config"""
        label = ctk.CTkLabel(
            self.config_frame,
            text="Click Position",
            font=("Arial", 12, "bold")
        )
        label.pack(anchor="w", pady=(0, 10))

        # Coordinates
        coord_frame = ctk.CTkFrame(self.config_frame)
        coord_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(coord_frame, text="X:", width=50).pack(side="left")
        self.click_x = ctk.CTkEntry(coord_frame, width=100)
        self.click_x.pack(side="left", padx=5)

        ctk.CTkLabel(coord_frame, text="Y:", width=50).pack(side="left", padx=(10, 0))
        self.click_y = ctk.CTkEntry(coord_frame, width=100)
        self.click_y.pack(side="left", padx=5)

        # Pre-fill values if editing
        if self.edit_action and self.edit_action['action_type'] == 'click':
            self.click_x.insert(0, str(self.edit_action['config'].get('x', 0)))
            self.click_y.insert(0, str(self.edit_action['config'].get('y', 0)))

        # Pick button
        pick_btn = ctk.CTkButton(
            self.config_frame,
            text="📍 Pick from Screen",
            command=self._open_picker,
            fg_color=("#3498db", "#3498db"),
            hover_color=("#2980b9", "#2980b9")
        )
        pick_btn.pack(fill="x", pady=10)

    def _build_type_config(self):
        """Build type action config"""
        label = ctk.CTkLabel(
            self.config_frame,
            text="Text to Type",
            font=("Arial", 12, "bold")
        )
        label.pack(anchor="w", pady=(0, 10))

        info = ctk.CTkLabel(
            self.config_frame,
            text="Use placeholders like {item}, {name}, {phone} from batch fields",
            text_color=("gray50", "gray70"),
            font=("Arial", 9)
        )
        info.pack(anchor="w", pady=(0, 5))

        text_container = ctk.CTkFrame(self.config_frame, fg_color=("white", "#2b2b2b"))
        text_container.pack(fill="both", expand=False, pady=10)
        self.type_text = tk.Text(
            text_container,
            height=6,
            wrap="word",
            relief="flat",
            bd=0,
            font=("Arial", 10),
            undo=False
        )
        self.type_text.pack(fill="both", expand=True, padx=6, pady=6)

        # Pre-fill value if editing
        if self.edit_action and self.edit_action['action_type'] == 'type':
            self.type_text.insert("1.0", self.edit_action['config'].get('text', ''))

    def _build_wait_config(self):
        """Build wait action config"""
        label = ctk.CTkLabel(
            self.config_frame,
            text="Wait Duration",
            font=("Arial", 12, "bold")
        )
        label.pack(anchor="w", pady=(0, 10))

        frame = ctk.CTkFrame(self.config_frame)
        frame.pack(fill="x", pady=5)

        ctk.CTkLabel(frame, text="Seconds:").pack(side="left")
        self.wait_duration = ctk.CTkEntry(frame, width=100)
        self.wait_duration.pack(side="left", padx=10)
        self.wait_duration.insert(0, "1")

        # Pre-fill value if editing
        if self.edit_action and self.edit_action['action_type'] == 'wait':
            self.wait_duration.delete(0, "end")
            self.wait_duration.insert(0, str(self.edit_action['config'].get('duration', 1)))

    def _build_screenshot_config(self):
        """Build screenshot action config"""
        label = ctk.CTkLabel(
            self.config_frame,
            text="Screenshot Settings",
            font=("Arial", 12, "bold")
        )
        label.pack(anchor="w", pady=(0, 10))

        frame = ctk.CTkFrame(self.config_frame)
        frame.pack(fill="x", pady=5)

        ctk.CTkLabel(frame, text="Filename:").pack(side="left")
        self.screenshot_file = ctk.CTkEntry(frame, width=250)
        self.screenshot_file.pack(side="left", padx=10)
        self.screenshot_file.insert(0, "screenshot.png")

        # Pre-fill value if editing
        if self.edit_action and self.edit_action['action_type'] == 'screenshot':
            self.screenshot_file.delete(0, "end")
            self.screenshot_file.insert(0, self.edit_action['config'].get('filename', 'screenshot.png'))

    def _open_picker(self):
        """Open coordinate picker"""
        try:
            from pynput import mouse
            import pyautogui
            
            # Hide the action builder temporarily
            self.withdraw()
            
            # Create a transparent overlay window
            self.picker_window = ctk.CTkToplevel(self)
            self.picker_window.title("Pick Coordinates")
            self.picker_window.geometry("300x150+100+100")
            self.picker_window.attributes('-topmost', True)
            
            # Instructions
            label = ctk.CTkLabel(
                self.picker_window,
                text="Click anywhere on your screen\nto capture coordinates",
                font=("Arial", 12),
                justify="center"
            )
            label.pack(pady=20, padx=20)
            
            # Position display
            self.pos_label = ctk.CTkLabel(
                self.picker_window,
                text="Moving cursor...",
                font=("Arial", 10, "bold")
            )
            self.pos_label.pack(pady=10)
            
            # Cancel button
            cancel_btn = ctk.CTkButton(
                self.picker_window,
                text="Cancel",
                command=self._cancel_picker,
                fg_color=("#95a5a6", "#95a5a6")
            )
            cancel_btn.pack(pady=10)
            
            # Start tracking mouse
            self.picker_active = True
            self._update_picker_position()
            
            # Setup global click listener
            def on_click(x, y, button, pressed):
                if pressed and self.picker_active:
                    self._on_coordinates_picked((int(x), int(y)))
                    return False  # Stop listener after first click
                    
            self.listener = mouse.Listener(on_click=on_click)
            self.listener.start()
            
        except ImportError:
            self.deiconify()  # Show the action builder again
            CTkMessagebox(
                title="Error", 
                message="pynput not installed. Please run: pip install pynput",
                icon="cancel"
            )
    
    def _update_picker_position(self):
        """Update position display in picker window"""
        if self.picker_active and hasattr(self, 'picker_window'):
            try:
                x, y = pyautogui.position()
                self.pos_label.configure(text=f"X: {x}, Y: {y}")
                self.picker_window.after(50, self._update_picker_position)
            except:
                pass
    
    def _on_coordinates_picked(self, coords):
        """Handle coordinates picked - ensure UI updates happen on main thread"""
        self.after(0, lambda: self._process_coordinates(coords))

    def _process_coordinates(self, coords):
        """Process coordinates and update UI on main thread"""
        self.picker_active = False
        if hasattr(self, 'listener'):
            try:
                self.listener.stop()
            except:
                pass
        
        # Close picker window first
        if hasattr(self, 'picker_window'):
            try:
                self.picker_window.destroy()
            except:
                pass
        
        # Show the action builder window again and bring to front
        try:
            self.deiconify()
            self.attributes('-topmost', True)
            self.focus_force()
            
            # Update the input fields
            if hasattr(self, 'click_x') and hasattr(self, 'click_y'):
                self.click_x.delete(0, "end")
                self.click_x.insert(0, str(coords[0]))
                self.click_y.delete(0, "end")
                self.click_y.insert(0, str(coords[1]))
        except:
            pass
    
    def _cancel_picker(self):
        """Cancel coordinate picking"""
        self.picker_active = False
        if hasattr(self, 'listener'):
            try:
                self.listener.stop()
            except:
                pass
        if hasattr(self, 'picker_window'):
            try:
                self.picker_window.destroy()
            except:
                pass
        
        # Show the action builder window again
        try:
            self.deiconify()
            self.attributes('-topmost', True)
            self.focus_force()
        except:
            pass

    def _save_action(self):
        """Save action and add to list"""
        action_type = self.action_type.get()
        config = {}

        try:
            if action_type == "click":
                config = {
                    "x": int(self.click_x.get()),
                    "y": int(self.click_y.get())
                }
            elif action_type == "type":
                config = {
                    "text": self.type_text.get("1.0", "end-1c")
                }
            elif action_type == "wait":
                config = {
                    "duration": float(self.wait_duration.get())
                }
            elif action_type == "key":
                key_combo = self.key_preview.get().strip()
                if not key_combo:
                    token = self._normalize_key_token(self.key_input.get())
                    if self._is_valid_key_token(token):
                        self.key_tokens = [token]
                        self._refresh_key_preview()
                        key_combo = self.key_preview.get().strip()
                if not key_combo:
                    raise ValueError("Please add at least one valid key")
                config = {
                    "key": key_combo,
                    "presses": int(self.key_presses.get()),
                    "interval": float(self.key_interval.get())
                }
            elif action_type == "screenshot":
                config = {
                    "filename": self.screenshot_file.get()
                }

            # Store reference before destroying
            action_list = self.action_list_frame
            on_changed = action_list.on_action_changed
            
            if self.edit_action and self.edit_index is not None:
                # Update existing action
                action_list.actions[self.edit_index] = {
                    "action_type": action_type,
                    "config": config,
                    "order": self.edit_index
                }
                # Destroy dialog first to avoid callback issues
                self.destroy()
                # Then refresh display after dialog is closed
                action_list._refresh_display()
                # Trigger on_action_changed callback
                if on_changed:
                    on_changed()
            else:
                # Add new action
                # Destroy dialog first to avoid callback issues
                self.destroy()
                # Then add to list (this will also refresh display)
                action_list.add_action(action_type, config)
        except ValueError as e:
            CTkMessagebox(title="Error", message=f"Invalid input: {str(e)}", icon="cancel")


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Automation Tool")
        self.geometry("1200x700")
        self.global_hotkeys = []

        self.supabase = SupabaseManager()
        self.engine = AutomationEngine()
        self.current_operation = None

        self._setup_ui()
        self._setup_shortcuts()
        self._check_authentication()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_ui(self):
        """Setup main UI"""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Sidebar
        sidebar = ctk.CTkFrame(main_frame, width=250, fg_color=("#f5f5f5", "#2b2b2b"))
        sidebar.pack(side="left", fill="both")
        sidebar.pack_propagate(False)

        # Sidebar title
        sidebar_title = ctk.CTkLabel(
            sidebar,
            text="Automation Tool",
            font=("Arial", 16, "bold"),
            text_color=("#222222", "#eeeeee")
        )
        sidebar_title.pack(pady=20, padx=10)

        # User info
        self.user_label = ctk.CTkLabel(
            sidebar,
            text="Local Mode",
            text_color=("gray50", "gray70"),
            font=("Arial", 10)
        )
        self.user_label.pack(pady=5, padx=10)

        local_mode_label = ctk.CTkLabel(
            sidebar,
            text="No login required. Operations are saved locally.",
            text_color=("gray50", "gray70"),
            font=("Arial", 9),
            wraplength=220,
            justify="left"
        )
        local_mode_label.pack(fill="x", padx=10, pady=(0, 10))

        # Separator
        sep = ctk.CTkFrame(sidebar, height=1, fg_color=("gray70", "#555555"))
        sep.pack(fill="x", pady=10, padx=10)

        # Operations list
        ops_label = ctk.CTkLabel(
            sidebar,
            text="Operations",
            font=("Arial", 12, "bold"),
            text_color=("#222222", "#eeeeee")
        )
        ops_label.pack(pady=10, padx=10, anchor="w")

        self.operations_frame = ctk.CTkScrollableFrame(
            sidebar,
            fg_color=("white", "#3b3b3b")
        )
        self.operations_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # New operation button
        new_op_btn = ctk.CTkButton(
            sidebar,
            text="+ New Operation",
            command=self._new_operation,
            fg_color=("#27ae60", "#27ae60"),
            hover_color=("#229954", "#229954")
        )
        new_op_btn.pack(fill="x", padx=10, pady=10)

        # Main content
        content = ctk.CTkFrame(main_frame)
        content.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        # Operation name
        name_frame = ctk.CTkFrame(content, fg_color="transparent")
        name_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(name_frame, text="Operation Name:", font=("Arial", 12, "bold")).pack(side="left")
        self.op_name = ctk.CTkEntry(name_frame, width=300)
        self.op_name.pack(side="left", padx=10)

        # Description
        desc_label = ctk.CTkLabel(content, text="Description:", font=("Arial", 11, "bold"))
        desc_label.pack(anchor="w", pady=(10, 0))

        self.op_desc = self._create_fast_textbox(content, height=3)
        self.op_desc.pack(fill="x", pady=5)

        # Split view
        split_frame = ctk.CTkFrame(content)
        split_frame.pack(fill="both", expand=True, pady=10)

        # Left side - Actions
        left_panel = ctk.CTkFrame(split_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.action_list = ActionListFrame(left_panel, on_action_changed=self._on_actions_changed)
        self.action_list.pack(fill="both", expand=True)

        # Right side - Batch execution
        right_panel = ctk.CTkFrame(split_frame)
        right_panel.pack(side="left", fill="both", expand=True)

        batch_label = ctk.CTkLabel(
            right_panel,
            text="Batch Items",
            font=("Arial", 14, "bold")
        )
        batch_label.pack(pady=10)

        batch_info = ctk.CTkLabel(
            right_panel,
            text="Formats: one value/line, CSV header + rows, or key=value pairs",
            text_color=("gray50", "gray70"),
            font=("Arial", 10)
        )
        batch_info.pack(pady=5)

        self.batch_items = self._create_fast_textbox(right_panel, height=12)
        self.batch_items.pack(fill="both", expand=True, pady=10)

        # Execution controls
        controls_frame = ctk.CTkFrame(right_panel)
        controls_frame.pack(fill="x", pady=10)

        self.execute_btn = ctk.CTkButton(
            controls_frame,
            text="▶ Execute (F5)",
            command=self._execute_batch,
            fg_color=("#27ae60", "#27ae60"),
            hover_color=("#229954", "#229954"),
            state="disabled"
        )
        self.execute_btn.pack(side="left", padx=5)

        self.pause_btn = ctk.CTkButton(
            controls_frame,
            text="⏸ Pause (F8)",
            command=self._pause_execution,
            state="disabled"
        )
        self.pause_btn.pack(side="left", padx=5)

        self.resume_btn = ctk.CTkButton(
            controls_frame,
            text="▶ Resume (F7)",
            command=self._resume_execution,
            state="disabled"
        )
        self.resume_btn.pack(side="left", padx=5)

        self.stop_btn = ctk.CTkButton(
            controls_frame,
            text="⏹ Stop (F6)",
            command=self._stop_execution,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=5)

        # Save button
        save_frame = ctk.CTkFrame(content)
        save_frame.pack(fill="x", pady=10)

        self.save_btn = ctk.CTkButton(
            save_frame,
            text="💾 Save Operation",
            command=self._save_operation,
            fg_color=("#3498db", "#3498db"),
            hover_color=("#2980b9", "#2980b9"),
            state="disabled"
        )
        self.save_btn.pack(side="left", padx=5)

        # Status
        self.status_label = ctk.CTkLabel(
            content,
            text="Ready",
            text_color=("gray50", "gray70"),
            font=("Arial", 10)
        )
        self.status_label.pack(anchor="w", pady=10)

    def _create_fast_textbox(self, parent, height: int = 6):
        """Create a native Text widget for smoother typing/IME input."""
        container = ctk.CTkFrame(parent, fg_color=("white", "#2b2b2b"))
        text_widget = tk.Text(
            container,
            height=height,
            wrap="word",
            relief="flat",
            bd=0,
            font=("Arial", 10),
            undo=False
        )
        text_widget.pack(fill="both", expand=True, padx=6, pady=6)
        container._text_widget = text_widget

        # Expose Text-like APIs so existing code can keep using self.op_desc/self.batch_items
        container.get = text_widget.get
        container.insert = text_widget.insert
        container.delete = text_widget.delete
        return container

    def _setup_shortcuts(self):
        """Register in-window and system-wide keyboard shortcuts."""
        self.bind_all("<F5>", self._on_execute_shortcut)
        self.bind_all("<F6>", self._on_stop_shortcut)
        self.bind_all("<F7>", self._on_resume_shortcut)
        self.bind_all("<F8>", self._on_pause_shortcut)
        self.bind_all("<Control-Return>", self._on_execute_shortcut)

        enabled_backends = []

        # Backend 1: pynput listener (usually most reliable for function keys)
        try:
            from pynput import keyboard as pynput_keyboard

            def on_press(key):
                if key == pynput_keyboard.Key.f5:
                    self.after(0, self._on_execute_shortcut)
                elif key == pynput_keyboard.Key.f6:
                    self.after(0, self._on_stop_shortcut)
                elif key == pynput_keyboard.Key.f7:
                    self.after(0, self._on_resume_shortcut)
                elif key == pynput_keyboard.Key.f8:
                    self.after(0, self._on_pause_shortcut)

            pynput_listener = pynput_keyboard.Listener(on_press=on_press)
            pynput_listener.start()
            self.global_hotkeys.append(pynput_listener)
            enabled_backends.append("pynput")
        except Exception as e:
            print(f"WARNING: pynput global hotkeys unavailable: {e}")

        # Backend 2: keyboard fallback (Windows)
        try:
            import keyboard as kb
            kb.add_hotkey("f5", lambda: self.after(0, self._on_execute_shortcut), suppress=False)
            kb.add_hotkey("f6", lambda: self.after(0, self._on_stop_shortcut), suppress=False)
            kb.add_hotkey("f7", lambda: self.after(0, self._on_resume_shortcut), suppress=False)
            kb.add_hotkey("f8", lambda: self.after(0, self._on_pause_shortcut), suppress=False)
            self.global_hotkeys.append("keyboard")
            enabled_backends.append("keyboard")
        except Exception as e:
            print(f"WARNING: keyboard global hotkeys unavailable: {e}")

        if enabled_backends:
            self.status_label.configure(
                text=f"Ready - Global hotkeys active: {', '.join(enabled_backends)}"
            )
        else:
            self.status_label.configure(text="Ready - Global hotkeys unavailable")

    def _on_execute_shortcut(self, event=None):
        """Trigger batch execution from keyboard shortcut."""
        if str(self.execute_btn.cget("state")) == "normal":
            self._execute_batch()

    def _on_pause_shortcut(self, event=None):
        """Trigger pause from keyboard shortcut."""
        if str(self.pause_btn.cget("state")) == "normal":
            self._pause_execution()

    def _on_resume_shortcut(self, event=None):
        """Trigger resume from keyboard shortcut."""
        if str(self.resume_btn.cget("state")) == "normal":
            self._resume_execution()

    def _on_stop_shortcut(self, event=None):
        """Trigger stop from keyboard shortcut."""
        if str(self.stop_btn.cget("state")) == "normal":
            self._stop_execution()

    def _on_close(self):
        """Stop background listeners before closing."""
        for hotkey_backend in self.global_hotkeys:
            try:
                if hotkey_backend == "keyboard":
                    import keyboard as kb
                    kb.unhook_all_hotkeys()
                else:
                    hotkey_backend.stop()
            except Exception:
                pass
        self.destroy()

    def _check_authentication(self):
        """Initialize local mode with no authentication required."""
        print("DEBUG: Guest Mode active")
        self.user_label.configure(text="Local Mode")
        self.save_btn.configure(state="normal")
        self._load_operations()

    def _show_auth_dialog(self):
        """No-op in local mode."""
        CTkMessagebox(title="Info", message="Local mode enabled. Login is not required.", icon="info")

    def _sign_out(self):
        """No-op in local mode."""
        CTkMessagebox(title="Info", message="Local mode enabled. Sign out is not applicable.", icon="info")

    def _new_operation(self):
        """Create new operation"""
        self.current_operation = None
        self.op_name.delete(0, "end")
        self.op_desc.delete("1.0", "end")
        self.action_list.clear_actions()
        self.batch_items.delete("1.0", "end")
        self.status_label.configure(text="New operation created")

    def _load_operations(self):
        """Load operations from database"""
        print("DEBUG: _load_operations called")
        self._refresh_operations_list()

    def _refresh_operations_list(self):
        """Refresh operations list in sidebar"""
        print("DEBUG: _refresh_operations_list called")
        for widget in self.operations_frame.winfo_children():
            widget.destroy()

        operations = self.supabase.get_operations()

        if not operations:
            print("DEBUG: No operations found for user.")
            empty_label = ctk.CTkLabel(
                self.operations_frame,
                text="No operations",
                text_color=("gray50", "gray70")
            )
            empty_label.pack(pady=20)
            return

        for op in operations:
            print(f"DEBUG: Found operation: {op['name']}")
            op_btn = ctk.CTkButton(
                self.operations_frame,
                text=op['name'],
                command=lambda op_id=op['id']: self._load_operation(op_id),
                anchor="w",
                width=200,
                height=30
            )
            op_btn.pack(fill="x", pady=2)

    def _load_operation(self, operation_id: str):
        """Load operation for editing"""
        print(f"DEBUG: _load_operation called for ID: {operation_id}")
        operation = self.supabase.get_operation_with_actions(operation_id)
        if not operation:
            print(f"ERROR: Failed to fetch operation {operation_id} from Supabase.")
            CTkMessagebox(title="Error", message="Failed to load operation", icon="cancel")
            return

        self.current_operation = operation
        self.op_name.delete(0, "end")
        self.op_name.insert(0, operation['name'])

        self.op_desc.delete("1.0", "end")
        self.op_desc.insert("1.0", operation.get('description', ''))

        self.action_list.set_actions(operation.get('actions', []))

        # Update execute button state based on actions
        has_actions = len(operation.get('actions', [])) > 0
        self.execute_btn.configure(state="normal" if has_actions else "disabled")
        
        self.status_label.configure(text=f"Loaded: {operation['name']}")

    def _save_operation(self):
        """Save operation to database"""
        print("DEBUG: _save_operation called")

        name = self.op_name.get().strip()
        if not name:
            CTkMessagebox(title="Error", message="Please enter operation name", icon="cancel")
            return

        description = self.op_desc.get("1.0", "end-1c")
        actions = self.action_list.get_actions()

        if not actions:
            CTkMessagebox(title="Error", message="Please add at least one action", icon="cancel")
            return

        result = None
        if self.current_operation:
            print(f"DEBUG: Updating existing operation {self.current_operation['id']}")
            result = self.supabase.update_operation(
                self.current_operation['id'],
                name,
                description,
                actions
            )
        else:
            print("DEBUG: Saving new operation")
            result = self.supabase.save_operation(name, description, actions)

        if result and result.get("success"):
            CTkMessagebox(title="Success", message="Operation saved", icon="check")
            self._load_operations()
        else:
            error_msg = result.get("error", "Save failed") if result else "Save failed (no result)"
            CTkMessagebox(title="Error", message=error_msg, icon="cancel")
        print("DEBUG: _save_operation finished")

    def _on_actions_changed(self):
        """Handle action list changed"""
        actions = self.action_list.get_actions()
        has_actions = len(actions) > 0
        print(f"DEBUG: Actions changed - {len(actions)} actions, button state: {'normal' if has_actions else 'disabled'}")
        self.execute_btn.configure(state="normal" if has_actions else "disabled")

    def _execute_batch(self):
        """Execute batch processing"""
        print("DEBUG: Execute button clicked")
        items_text = self.batch_items.get("1.0", "end-1c").strip()
        print(f"DEBUG: Batch items text: '{items_text}'")
        
        if not items_text:
            print("DEBUG: No batch items entered")
            CTkMessagebox(title="Error", message="Please enter batch items", icon="cancel")
            return

        batch_contexts = self._parse_batch_items(items_text)
        print(f"DEBUG: Parsed {len(batch_contexts)} batch items")
        
        actions = self.action_list.get_actions()
        print(f"DEBUG: Got {len(actions)} actions")

        if not actions:
            print("DEBUG: No actions configured")
            CTkMessagebox(title="Error", message="Please add actions first", icon="cancel")
            return

        print("DEBUG: Starting execution...")
        self.execute_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal")
        self.resume_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text=f"Executing {len(batch_contexts)} items...")

        # Run in thread
        thread = threading.Thread(
            target=self._batch_execution_thread,
            args=(batch_contexts, actions),
            daemon=True
        )
        thread.start()

    def _parse_batch_items(self, items_text: str) -> List[Dict[str, str]]:
        """Parse batch input into contexts for placeholder substitution."""
        lines = [line.strip() for line in items_text.splitlines() if line.strip()]
        if not lines:
            return []

        # Mode 1: key=value pairs per line, separated by comma/semicolon
        if any("=" in line for line in lines):
            contexts: List[Dict[str, str]] = []
            for line in lines:
                context: Dict[str, str] = {}
                for pair in re.split(r"[;,]+", line):
                    pair = pair.strip()
                    if "=" not in pair:
                        continue
                    key, value = pair.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if key:
                        context[key] = value
                if context:
                    if "item" not in context:
                        context["item"] = next(iter(context.values()), "")
                    contexts.append(context)
            if contexts:
                return contexts

        # Mode 2: CSV with header on first line
        try:
            rows = list(csv.reader(lines))
            if len(rows) >= 2 and len(rows[0]) >= 2:
                headers = [h.strip() for h in rows[0]]
                contexts = []
                for row in rows[1:]:
                    if not any(cell.strip() for cell in row):
                        continue
                    context = {}
                    for i, header in enumerate(headers):
                        if not header:
                            continue
                        context[header] = row[i].strip() if i < len(row) else ""
                    if context:
                        if "item" not in context:
                            context["item"] = row[0].strip() if row else ""
                        contexts.append(context)
                if contexts:
                    return contexts
        except Exception:
            pass

        # Mode 3: default single field per value
        parts = re.split(r"[\r\n,;]+", items_text)
        return [{"item": part.strip()} for part in parts if part.strip()]

    def _batch_execution_thread(self, batch_contexts: List[Dict[str, str]], actions: List[Dict[str, Any]]):
        """Execute batch in background thread"""
        print(f"DEBUG: Thread started - {len(batch_contexts)} items, {len(actions)} actions")
        try:
            self.engine.load_actions(actions)
            self.engine.is_running = True  # Set engine running state
            self.engine.is_paused = False

            success_count = 0
            error_count = 0

            for idx, context in enumerate(batch_contexts):
                item_label = context.get("item", "")
                if not item_label:
                    item_label = ", ".join([f"{k}={v}" for k, v in list(context.items())[:2]])
                print(f"DEBUG: Processing item {idx + 1}/{len(batch_contexts)}: {item_label}")
                if not self.engine.is_running:
                    print("DEBUG: Engine stopped")
                    break

                self.after(
                    0,
                    lambda i=item_label, n=idx + 1, total=len(batch_contexts): self.status_label.configure(
                        text=f"Processing: {i} ({n}/{total})"
                    )
                )

                try:
                    print(f"DEBUG: Executing workflow for '{item_label}'")
                    result = self.engine.execute_workflow(context)
                    if result:
                        success_count += 1
                        print(f"DEBUG: Success! Total successes: {success_count}")
                    else:
                        error_count += 1
                        print(f"DEBUG: Workflow returned False. Total errors: {error_count}")
                except Exception as e:
                    error_count += 1
                    print(f"ERROR: Error processing {item_label}: {str(e)}")
                    import traceback
                    traceback.print_exc()

            print(f"DEBUG: Execution completed - {success_count} successes, {error_count} errors")
        except Exception as e:
            print(f"CRITICAL ERROR in execution thread: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.engine.is_running = False
            
        self.after(0, lambda: self.execute_btn.configure(state="normal"))
        self.after(0, lambda: self.pause_btn.configure(state="disabled", text="⏸ Pause (F8)"))
        self.after(0, lambda: self.resume_btn.configure(state="disabled"))
        self.after(0, lambda: self.stop_btn.configure(state="disabled"))
        self.after(
            0,
            lambda: self.status_label.configure(
                text=f"Completed: {success_count} success, {error_count} errors"
            )
        )

    def _pause_execution(self):
        """Pause execution"""
        self.engine.pause()
        self.pause_btn.configure(state="disabled", text="⏸ Paused")
        self.resume_btn.configure(state="normal")

    def _resume_execution(self):
        """Resume execution"""
        self.engine.resume()
        self.pause_btn.configure(state="normal", text="⏸ Pause (F8)")
        self.resume_btn.configure(state="disabled")

    def _stop_execution(self):
        """Stop execution"""
        self.engine.stop()
        self.execute_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="⏸ Pause (F8)")
        self.resume_btn.configure(state="disabled")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="Execution stopped")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
