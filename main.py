import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from login_ui import LoginPage

def main():
    # Enable High DPI Scaling
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "RoundPreferFloor"

    app = QApplication(sys.argv)
    
    # OS-Safe Icon Loading
    if os.path.exists("assets/Hollow_icon.png"):
        app.setWindowIcon(QIcon("assets/Hollow_icon.png"))
        
    # Windows-specific App ID for Taskbar Grouping (Prevents crashes on Mac/Linux)
    if sys.platform == "win32":
        try:
            import ctypes
            myappid = u"com.hollowtech.auth_template.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass
    
    login_window = LoginPage()
    
    def on_login_success(username):
        QMessageBox.information(
            login_window, 
            "Login Successful", 
            f"Welcome back, {username}!\n\nThis is where your main application logic would start."
        )
        # login_window.close() 

    login_window.login_successful.connect(on_login_success)
    
    login_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()