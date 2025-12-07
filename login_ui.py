import sys
import os
from PySide6.QtCore import Signal, QSize, Qt, QTimer
from PySide6.QtGui import QIcon, QCursor, QPixmap, QAction
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QVBoxLayout,
    QLineEdit, QWidgetAction, QStackedWidget, QHBoxLayout, 
    QFrame, QDialog, QScrollArea, QSizePolicy
)

# --- Style Constants ---
STYLE_CONSTANTS = {
    "background_color": "#1E1E1E",
    "form_container_color": "#1F2937",
    "input_field_color": "#374151",
    "input_border_color": "#4B5563",
    "input_error_color": "#EF4444",  # Red for errors
    "success_color": "#10B981",      # Green for success
    "error_bg_color": "rgba(239, 68, 68, 0.1)",
    "success_bg_color": "rgba(16, 185, 129, 0.1)",
    "primary_button_color": "#6366F1",
    "primary_button_hover_color": "#4F46E5",
    "secondary_button_color": "#374151",
    "secondary_button_hover_color": "#4B5563",
    "text_color": "#E5E7EB",
    "text_secondary_color": "#9CA3AF",
    "link_color": "#6366F1",
    "separator_color": "#6B7280",
    "font_family": "Inter, sans-serif",
}

# --- Custom Widgets ---

class HoverIconButton(QPushButton):
    """
    A custom button that recolors its SVG icon on hover.
    Includes caching for performance.
    """
    def __init__(self, icon_path, parent=None):
        super().__init__(parent)
        self.icon_path = icon_path
        self.default_color = STYLE_CONSTANTS["text_secondary_color"]
        self.hover_color = "#FFFFFF"
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("border: none; background: transparent;")
        self.setFixedSize(24, 24)
        
        # Cache pixmaps to prevent lag
        self._default_pixmap = self._create_pixmap(self.default_color)
        self._hover_pixmap = self._create_pixmap(self.hover_color)
        
        # Set initial state
        self.setIcon(QIcon(self._default_pixmap))

    def _create_pixmap(self, color_hex):
        if not os.path.exists(self.icon_path):
            return QPixmap()
        try:
            with open(self.icon_path, 'r') as f:
                svg_data = f.read()
            colored_svg = svg_data.replace('currentColor', color_hex)
            pixmap = QPixmap()
            pixmap.loadFromData(colored_svg.encode('utf-8'))
            return pixmap
        except Exception as e:
            print(f"Error loading icon: {e}")
            return QPixmap()

    def enterEvent(self, event):
        if self._hover_pixmap:
            self.setIcon(QIcon(self._hover_pixmap))
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._default_pixmap:
            self.setIcon(QIcon(self._default_pixmap))
        super().leaveEvent(event)
    
    def set_icon_path(self, new_path):
        self.icon_path = new_path
        self._default_pixmap = self._create_pixmap(self.default_color)
        self._hover_pixmap = self._create_pixmap(self.hover_color)
        if self.underMouse():
            self.setIcon(QIcon(self._hover_pixmap))
        else:
            self.setIcon(QIcon(self._default_pixmap))

# --- Main Page Class ---

class LoginPage(QWidget):
    login_successful = Signal(str)

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("HollowTech | Login")
        self.resize(1440, 720)
        self.setMinimumSize(1280, 720)
        self.setStyleSheet(f"background-color: {STYLE_CONSTANTS['background_color']};")
        self.center_window()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        central_widget = self._create_central_widget()
        
        main_layout.addStretch()
        main_layout.addWidget(central_widget)
        main_layout.addStretch()

    def _create_central_widget(self):
        central_widget = QWidget(self)
        central_layout = QVBoxLayout(central_widget)
        central_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        central_layout.setSpacing(20)

        logo = QLabel(self)
        if os.path.exists("assets/logo.png"):
            pixmap = QPixmap("assets/logo.png").scaled(
                160, 160, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            logo.setPixmap(pixmap)
        else:
            logo.setText("LOGO")
            logo.setStyleSheet("color: white; font-weight: bold; font-size: 24px;")
            
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        central_layout.addWidget(logo)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setFixedSize(400, 560) # Increased height for error message
        
        self.stacked_widget.addWidget(self._create_login_view())
        self.stacked_widget.addWidget(self._create_signup_view())
        self.stacked_widget.addWidget(self._create_forgot_password_view())
        self.stacked_widget.addWidget(self._create_info_view())
        
        central_layout.addWidget(self.stacked_widget)
        return central_widget
    
    def _create_login_view(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Error Message Label
        self.login_error_label = self._create_message_label()

        email_label = QLabel("Email")
        self.login_email_input = self._create_line_edit("Enter email")
        
        password_label = QLabel("Password")
        self.login_password_input = self._create_line_edit("Enter password", is_password=True)
        
        # Connect "Enter" key logic
        # 1. Enter in Email -> Focus Password
        self.login_email_input.returnPressed.connect(self.login_password_input.setFocus)
        # 2. Enter in Password -> Click Login
        self.login_password_input.returnPressed.connect(self.handle_login)
        
        forgot_password_link = QLabel(f'<a href="#" style="color:{STYLE_CONSTANTS["link_color"]}; text-decoration:none;">Forgot password?</a>')
        forgot_password_link.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        forgot_password_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        forgot_password_link.linkActivated.connect(self._switch_to_forgot_password)

        login_button = self._create_action_button("Login")
        login_button.clicked.connect(self.handle_login)

        separator = self._create_separator("OR")

        social_buttons_layout = QHBoxLayout()
        social_buttons_layout.setSpacing(20)
        google_button = self._create_social_icon_button("Google", "assets/Google.svg")
        phantom_button = self._create_social_icon_button("Phantom", "assets/Phantom.svg")
        
        social_buttons_layout.addStretch()
        social_buttons_layout.addWidget(google_button)
        social_buttons_layout.addWidget(phantom_button)
        social_buttons_layout.addStretch()

        signup_prompt_layout = QHBoxLayout()
        signup_prompt_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        signup_prompt_label = QLabel("Don't have an account?")
        signup_link = QLabel(f'<a href="#" style="color:{STYLE_CONSTANTS["link_color"]}; text-decoration:none; font-weight:600;">Sign up</a>')
        signup_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        signup_link.linkActivated.connect(self._switch_to_signup)
        signup_prompt_layout.addWidget(signup_prompt_label)
        signup_prompt_layout.addWidget(signup_link)

        # Add to Layout
        layout.addWidget(self.login_error_label)
        layout.addWidget(email_label)
        layout.addWidget(self.login_email_input)
        layout.addWidget(password_label)
        layout.addWidget(self.login_password_input)
        layout.addWidget(forgot_password_link)
        layout.addSpacing(10)
        layout.addWidget(login_button)
        layout.addWidget(separator)
        layout.addLayout(social_buttons_layout)
        layout.addStretch()
        layout.addLayout(signup_prompt_layout)

        for label in [email_label, password_label, signup_prompt_label]:
            label.setStyleSheet(f"color: {STYLE_CONSTANTS['text_secondary_color']}; font-size: 14px;")

        return container

    def _create_signup_view(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.signup_error_label = self._create_message_label()

        email_label = QLabel("Email")
        self.signup_email_input = self._create_line_edit("Enter email")
        
        invite_code_label = QLabel("Invite code (optional)")
        self.invite_code_input = self._create_line_edit("Invite code")
        
        # Enter key navigation for Signup
        self.signup_email_input.returnPressed.connect(self.invite_code_input.setFocus)
        self.invite_code_input.returnPressed.connect(self.handle_register)

        signup_button = self._create_action_button("Sign Up")
        signup_button.clicked.connect(self.handle_register)

        separator = self._create_separator("Or Sign Up")

        social_buttons_layout = QHBoxLayout()
        social_buttons_layout.setSpacing(20)
        google_button = self._create_social_icon_button("Google", "assets/Google.svg")
        phantom_button = self._create_social_icon_button("Phantom", "assets/Phantom.svg")
        
        social_buttons_layout.addStretch()
        social_buttons_layout.addWidget(google_button)
        social_buttons_layout.addWidget(phantom_button)
        social_buttons_layout.addStretch()

        login_prompt_layout = QHBoxLayout()
        login_prompt_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_prompt_label = QLabel("Already have an account?")
        login_link = QLabel(f'<a href="#" style="color:{STYLE_CONSTANTS["link_color"]}; text-decoration:none; font-weight:600;">Login</a>')
        login_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        login_link.linkActivated.connect(self._switch_to_login)
        login_prompt_layout.addWidget(login_prompt_label)
        login_prompt_layout.addWidget(login_link)
        
        terms_label = QLabel(
            'By creating an account, you agree to our '
            f'<a href="privacy" style="color:{STYLE_CONSTANTS["link_color"]}; text-decoration:none;">Privacy Policy</a> and '
            f'<a href="terms" style="color:{STYLE_CONSTANTS["link_color"]}; text-decoration:none;">Terms of Service</a>'
        )
        terms_label.setWordWrap(True)
        terms_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        terms_label.setStyleSheet(f"color: {STYLE_CONSTANTS['text_secondary_color']}; font-size: 12px;")
        terms_label.linkActivated.connect(self.handle_terms_click)

        layout.addWidget(self.signup_error_label)
        layout.addWidget(email_label)
        layout.addWidget(self.signup_email_input)
        layout.addWidget(invite_code_label)
        layout.addWidget(self.invite_code_input)
        layout.addSpacing(10)
        layout.addWidget(signup_button)
        layout.addWidget(separator)
        layout.addLayout(social_buttons_layout)
        layout.addStretch()
        layout.addLayout(login_prompt_layout)
        layout.addWidget(terms_label)

        for label in [email_label, invite_code_label, login_prompt_label]:
            label.setStyleSheet(f"color: {STYLE_CONSTANTS['text_secondary_color']}; font-size: 14px;")
            
        return container

    def _create_forgot_password_view(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        
        self.forgot_msg_label = self._create_message_label()

        header_label = QLabel("Reset Password")
        header_label.setStyleSheet(f"color: {STYLE_CONSTANTS['text_color']}; font-size: 20px; font-weight: bold;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc_label = QLabel("Enter your email address and we'll send you a link to reset your password.")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet(f"color: {STYLE_CONSTANTS['text_secondary_color']}; font-size: 13px;")

        email_label = QLabel("Email")
        email_label.setStyleSheet(f"color: {STYLE_CONSTANTS['text_secondary_color']}; font-size: 14px;")
        self.forgot_email_input = self._create_line_edit("Enter email")
        
        # Enter -> Submit
        self.forgot_email_input.returnPressed.connect(self.handle_reset_password)

        reset_button = self._create_action_button("Send Reset Link")
        reset_button.clicked.connect(self.handle_reset_password)

        back_link = QLabel(f'<a href="#" style="color:{STYLE_CONSTANTS["link_color"]}; text-decoration:none; font-weight:600;">Back to Login</a>')
        back_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        back_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back_link.linkActivated.connect(self._switch_to_login)

        layout.addSpacing(20)
        layout.addWidget(header_label)
        layout.addWidget(desc_label)
        layout.addWidget(self.forgot_msg_label)
        layout.addSpacing(20)
        layout.addWidget(email_label)
        layout.addWidget(self.forgot_email_input)
        layout.addSpacing(10)
        layout.addWidget(reset_button)
        layout.addStretch()
        layout.addWidget(back_link)

        return container

    def _create_info_view(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 20, 20, 10)
        
        back_btn = QPushButton("Back")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet(f"color: {STYLE_CONSTANTS['link_color']}; font-weight: 600; border: none; background: transparent; text-align: left;")
        back_btn.clicked.connect(self._switch_to_signup)
        
        self.info_title = QLabel("Terms of Service")
        self.info_title.setStyleSheet(f"color: {STYLE_CONSTANTS['text_color']}; font-size: 18px; font-weight: bold;")
        
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        header_layout.addWidget(self.info_title)
        header_layout.addStretch()
        dummy = QWidget()
        dummy.setFixedWidth(back_btn.sizeHint().width())
        header_layout.addWidget(dummy)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {STYLE_CONSTANTS['input_border_color']};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {STYLE_CONSTANTS['separator_color']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; background: none; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 0, 20, 20)
        
        self.info_text = QLabel()
        self.info_text.setWordWrap(True)
        self.info_text.setStyleSheet(f"color: {STYLE_CONSTANTS['text_secondary_color']}; font-size: 13px; line-height: 1.5;")
        self.info_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        content_layout.addWidget(self.info_text)
        scroll.setWidget(content_widget)

        layout.addWidget(header_frame)
        layout.addWidget(scroll)
        
        return container

    # --- Logic & Handlers ---

    def handle_terms_click(self, link):
        if link == "privacy":
            self.info_title.setText("Privacy Policy")
            self.info_text.setText(
                "<b>1. Data Collection</b><br><br>"
                "We collect minimal data to provide our services. This includes email addresses and wallet public keys.<br><br>"
                "<b>2. Security</b><br><br>"
                "We use industry-standard encryption. Your private keys are never stored on our servers.<br><br>"
                "<b>3. Updates</b><br><br>"
                "We may update this policy from time to time." + ("<br><br>" * 10)
            )
        else:
            self.info_title.setText("Terms of Service")
            self.info_text.setText(
                "<b>1. Acceptance</b><br><br>By using this app, you agree to these terms.<br><br>"
                "<b>2. Liability</b><br><br>HollowTech is not responsible for financial losses.<br><br>"
                "<b>3. Risk</b><br><br>Cryptocurrency involves significant risk." + ("<br><br>" * 10)
            )
        self.stacked_widget.setCurrentIndex(3)

    def _create_line_edit(self, placeholder, is_password=False):
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setFixedHeight(40)
        self.default_input_style = f"""
            QLineEdit {{
                background-color: {STYLE_CONSTANTS['input_field_color']};
                color: {STYLE_CONSTANTS['text_color']};
                font-size: 14px;
                padding-left: 15px;
                padding-right: 15px;
                border-radius: 8px;
                border: 1px solid {STYLE_CONSTANTS['input_border_color']};
            }}
            QLineEdit:focus {{
                border: 1px solid {STYLE_CONSTANTS['primary_button_color']};
            }}
        """
        line_edit.setStyleSheet(self.default_input_style)
        
        # Clear error on type
        line_edit.textChanged.connect(lambda: self._set_input_error(line_edit, False))
        
        if is_password:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self._add_password_toggle_button(line_edit)
        return line_edit
    
    def _set_input_error(self, widget, is_error):
        if is_error:
            widget.setStyleSheet(f"""
                QLineEdit {{
                    border: 1px solid {STYLE_CONSTANTS['input_error_color']};
                    background-color: {STYLE_CONSTANTS['input_field_color']};
                    color: {STYLE_CONSTANTS['text_color']};
                    font-size: 14px;
                    padding-left: 15px;
                    padding-right: 15px;
                    border-radius: 8px;
                }}
            """)
        else:
            widget.setStyleSheet(self.default_input_style)
            # Hide errors if visible
            if self.login_error_label.isVisible():
                self.login_error_label.setVisible(False)
            if self.signup_error_label.isVisible():
                self.signup_error_label.setVisible(False)

    def _create_message_label(self):
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setVisible(False)
        label.setFixedHeight(40)
        # Default to error style, can be overridden for success
        return label

    def _show_message(self, label, text, is_error=True):
        bg_color = STYLE_CONSTANTS['error_bg_color'] if is_error else STYLE_CONSTANTS['success_bg_color']
        text_color = STYLE_CONSTANTS['input_error_color'] if is_error else STYLE_CONSTANTS['success_color']
        border_color = STYLE_CONSTANTS['input_error_color'] if is_error else STYLE_CONSTANTS['success_color']
        
        label.setText(text)
        label.setStyleSheet(f"""
            background-color: {bg_color};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
        """)
        label.setVisible(True)

    def _create_action_button(self, text):
        button = QPushButton(text)
        button.setFixedHeight(40)
        button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {STYLE_CONSTANTS['primary_button_color']};
                color: white;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {STYLE_CONSTANTS['primary_button_hover_color']};
            }}
        """)
        return button
        
    def _create_social_icon_button(self, text, icon_path):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button = QPushButton()
        button.setFixedSize(56, 56)
        button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {STYLE_CONSTANTS['secondary_button_color']};
                border: none;
                border-radius: 28px;
            }}
            QPushButton:hover {{
                background-color: {STYLE_CONSTANTS['secondary_button_hover_color']};
            }}
        """)

        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(32, 32))

        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"color: {STYLE_CONSTANTS['text_secondary_color']}; font-size: 12px;")

        layout.addWidget(button)
        layout.addWidget(label)
        return container

    def _create_separator(self, text):
        separator_widget = QWidget()
        layout = QHBoxLayout(separator_widget)
        layout.setContentsMargins(0, 15, 0, 15)
        layout.setSpacing(10)

        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFixedHeight(1)
        line1.setStyleSheet(f"background-color: {STYLE_CONSTANTS['separator_color']};")

        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"color: {STYLE_CONSTANTS['separator_color']}; font-size: 12px;")

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFixedHeight(1)
        line2.setStyleSheet(f"background-color: {STYLE_CONSTANTS['separator_color']};")

        layout.addWidget(line1, 1)
        layout.addWidget(label, 0)
        layout.addWidget(line2, 1)

        return separator_widget

    def _add_password_toggle_button(self, line_edit):
        self.toggle_button = HoverIconButton("assets/HiddenEye.svg")
        self.toggle_button.clicked.connect(lambda: self._toggle_password_visibility(line_edit))
        action = QWidgetAction(line_edit)
        action.setDefaultWidget(self.toggle_button)
        line_edit.addAction(action, QLineEdit.ActionPosition.TrailingPosition)

    def _toggle_password_visibility(self, line_edit):
        if line_edit.echoMode() == QLineEdit.EchoMode.Password:
            line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_button.set_icon_path("assets/Eye.svg")
        else:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_button.set_icon_path("assets/HiddenEye.svg")

    def _switch_to_signup(self):
        self.stacked_widget.setCurrentIndex(1)
        self._clear_messages()

    def _switch_to_login(self):
        self.stacked_widget.setCurrentIndex(0)
        self._clear_messages()
    
    def _switch_to_forgot_password(self):
        self.stacked_widget.setCurrentIndex(2)
        self._clear_messages()

    def _clear_messages(self):
        self.login_error_label.setVisible(False)
        self.signup_error_label.setVisible(False)
        self.forgot_msg_label.setVisible(False)

    def handle_login(self):
        username = self.login_email_input.text().strip()
        password = self.login_password_input.text().strip()
        
        has_error = False
        if not username:
            self._set_input_error(self.login_email_input, True)
            has_error = True
        
        if not password:
            self._set_input_error(self.login_password_input, True)
            has_error = True
            
        if has_error:
            self._show_message(self.login_error_label, "Please fill in all required fields.")
            return

        # TODO: Replace with your actual backend logic
        # For demo purposes, we treat "Test" as the only valid user
        if username.lower() == "test" and password == "password":
            self.login_successful.emit(username)
        else:
            self._show_message(self.login_error_label, "Invalid email or password.")

    def handle_register(self):
        email = self.signup_email_input.text().strip()
        
        if not email:
            self._set_input_error(self.signup_email_input, True)
            self._show_message(self.signup_error_label, "Email is required.")
            return
            
        # TODO: Backend call here
        print(f"Registered: {email}")
        self._switch_to_login()

    def handle_register(self):
        email = self.signup_email_input.text().strip()
        
        if not email:
            self._set_input_error(self.signup_email_input, True)
            self._show_message(self.signup_error_label, "Email is required.")
            return
            
        # TODO: Backend call here
        print(f"Registered: {email}")
        self._switch_to_login()

    def handle_reset_password(self):
        email = self.forgot_email_input.text().strip()
        if not email:
            self._set_input_error(self.forgot_email_input, True)
            self._show_message(self.forgot_msg_label, "Please enter your email.")
            return

        # TODO: Backend call here
        self._show_message(self.forgot_msg_label, f"Reset link sent to {email}", is_error=False)
        self._set_input_error(self.forgot_email_input, False)
        # Optional: Switch back after a delay or let user click back

    def center_window(self):
        screen = self.screen().availableGeometry()
        self.move(
            int((screen.width() - self.width()) / 2),
            int((screen.height() - self.height()) / 2)
        )