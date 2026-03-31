import customtkinter as ctk
from PIL import Image, ImageDraw
import pyautogui
from typing import Callable, Tuple, Optional
import threading


class CoordinatePicker:
    def __init__(self, callback: Callable[[Tuple[int, int]], None]):
        self.callback = callback
        self.picking = False
        self.root = None
        self.canvas = None

    def start_picking(self):
        """Start picking mode - captures mouse position on click"""
        self.root = ctk.CTkToplevel()
        self.root.title("Coordinate Picker")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # Instructions
        instruction = ctk.CTkLabel(
            self.root,
            text="1. Click anywhere on the screen to pick coordinates\n2. Move your cursor to see current position\n3. Close window when done",
            text_color=("#222222", "#eeeeee"),
            font=("Arial", 12),
            justify="left"
        )
        instruction.pack(pady=20, padx=20)

        # Position display
        self.position_label = ctk.CTkLabel(
            self.root,
            text="Position: Moving cursor...",
            text_color=("#222222", "#eeeeee"),
            font=("Arial", 14, "bold")
        )
        self.position_label.pack(pady=10)

        # Screenshot preview
        self.canvas = ctk.CTkCanvas(
            self.root,
            width=350,
            height=150,
            bg_color=("#f0f0f0", "#333333"),
            fg_color=("#f0f0f0", "#333333")
        )
        self.canvas.pack(pady=10, padx=20)

        # Button
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(pady=10)

        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.root.destroy,
            width=100
        )
        close_btn.pack(side="left", padx=5)

        # Start tracking mouse
        self.picking = True
        self._update_position()
        self.root.mainloop()

    def _update_position(self):
        """Update position display"""
        if self.picking and self.root:
            try:
                x, y = pyautogui.position()
                self.position_label.configure(text=f"Position: X={x}, Y={y}")

                # Update preview screenshot with crosshair
                self._update_preview(x, y)

                self.root.after(50, self._update_position)
            except:
                pass

    def _update_preview(self, x: int, y: int):
        """Update preview with crosshair at position"""
        try:
            # Capture small region around cursor
            region_size = 150
            left = max(0, x - region_size // 2)
            top = max(0, y - region_size // 2)
            right = min(pyautogui.size()[0], x + region_size // 2)
            bottom = min(pyautogui.size()[1], y + region_size // 2)

            screenshot = pyautogui.screenshot(region=(left, top, right - left, bottom - top))

            # Draw crosshair
            draw = ImageDraw.Draw(screenshot)
            center_x = x - left
            center_y = y - top
            crosshair_size = 10

            # Draw crosshair lines
            draw.line([(center_x - crosshair_size, center_y), (center_x + crosshair_size, center_y)], fill=(255, 0, 0), width=2)
            draw.line([(center_x, center_y - crosshair_size), (center_x, center_y + crosshair_size)], fill=(255, 0, 0), width=2)

            # Convert to CTk PhotoImage
            photo = ctk.CTkImage(screenshot, size=(350, 150))
            self.canvas.create_image(175, 75, image=photo)
            self.canvas.image = photo
        except Exception as e:
            print(f"Preview update error: {str(e)}")

    def stop_picking(self):
        """Stop picking mode"""
        self.picking = False
        if self.root:
            self.root.destroy()


class PickerDialog(ctk.CTkToplevel):
    """Dialog for picking coordinates"""

    def __init__(self, parent, on_pick: Callable[[Tuple[int, int]], None]):
        super().__init__(parent)
        self.title("Pick Coordinates")
        self.geometry("500x400")
        self.resizable(False, False)
        self.on_pick = on_pick

        # Instructions
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill="both", expand=False, padx=20, pady=20)

        title = ctk.CTkLabel(
            info_frame,
            text="Coordinate Picker",
            font=("Arial", 16, "bold")
        )
        title.pack()

        instruction = ctk.CTkLabel(
            info_frame,
            text="Click 'Start Picking' then click anywhere on your screen to capture coordinates.",
            text_color=("gray40", "gray60"),
            font=("Arial", 11),
            wraplength=450,
            justify="center"
        )
        instruction.pack(pady=10)

        # Display area
        display_frame = ctk.CTkFrame(self)
        display_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.display_label = ctk.CTkLabel(
            display_frame,
            text="Click 'Start Picking' to begin",
            text_color=("gray40", "gray60"),
            font=("Arial", 12)
        )
        self.display_label.pack(expand=True)

        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=20)

        self.pick_btn = ctk.CTkButton(
            button_frame,
            text="Start Picking",
            command=self._start_picking,
            fg_color=("#3498db", "#3498db"),
            hover_color=("#2980b9", "#2980b9"),
            text_color="white"
        )
        self.pick_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color=("#95a5a6", "#95a5a6"),
            hover_color=("#7f8c8d", "#7f8c8d"),
            text_color="white"
        )
        cancel_btn.pack(side="left", padx=5)

        self.picked_coords = None

    def _start_picking(self):
        """Start coordinate picker"""
        self.pick_btn.configure(state="disabled", text="Picking... (click to capture)")

        # Create picker window
        self.picker = CoordinatePicker(self._on_coordinates_picked)
        self.picker.root = ctk.CTkToplevel(self)
        self.picker.root.title("Click to Capture")
        self.picker.root.geometry("1", "1")
        self.picker.root.attributes("-alpha", 0.0)

        # Bind click event globally
        self._setup_global_click()

    def _setup_global_click(self):
        """Setup global mouse click listener"""
        try:
            from pynput import mouse

            def on_click(x, y, button, pressed):
                if pressed:
                    self.after(0, lambda: self._on_coordinates_picked((x, y)))
                    return False # Stop listener

            listener = mouse.Listener(on_click=on_click)
            listener.start()
        except ImportError:
            self.display_label.configure(text="Error: pynput not installed")
            self.pick_btn.configure(state="normal", text="Start Picking")

    def _on_coordinates_picked(self, coords: Tuple[int, int]):
        """Handle coordinates picked"""
        self.picked_coords = coords
        self.display_label.configure(text=f"Picked: X={coords[0]}, Y={coords[1]}")
        self.pick_btn.configure(state="normal", text="Start Picking")

        # Call callback
        self.on_pick(coords)
