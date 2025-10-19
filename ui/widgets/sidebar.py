"""
Sidebar Navigation Widget - Collapsible navigation menu
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont


class NavButton(QPushButton):
    """Custom navigation button with icon and text"""
    
    def __init__(self, icon: str, text: str):
        super().__init__()
        self.icon = icon
        self.text = text
        self.is_active = False
        
        self.setText(f"{icon}  {text}")
        self.setFixedHeight(50)
        self.update_style()
        
    def update_style(self):
        """Update button style based on active state"""
        if self.is_active:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #00bcd4;
                    color: #0d0d0d;
                    border: none;
                    border-left: 4px solid #00e5ff;
                    text-align: left;
                    padding-left: 20px;
                    font-size: 11pt;
                    font-weight: bold;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #e0e0e0;
                    border: none;
                    border-left: 4px solid transparent;
                    text-align: left;
                    padding-left: 20px;
                    font-size: 11pt;
                }
                QPushButton:hover {
                    background-color: #2d2d2d;
                    border-left-color: #00bcd4;
                }
            """)
            
    def set_active(self, active: bool):
        """Set button active state"""
        self.is_active = active
        self.update_style()


class Sidebar(QWidget):
    """Collapsible sidebar navigation"""
    
    page_requested = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.is_collapsed = False
        self.expanded_width = 250
        self.collapsed_width = 70
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        self.setFixedWidth(self.expanded_width)
        self.setStyleSheet("""
            QWidget {
                background-color: #0d0d0d;
                border-right: 2px solid #00bcd4;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(0)
        
        # Toggle button
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setFixedHeight(40)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #00bcd4;
                border: none;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2d2d2d;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        layout.addWidget(self.toggle_btn)
        
        # Navigation buttons
        nav_items = [
            ("📊", "Dashboard"),
            ("📡", "Live Data"),
            ("🗺", "Map View"),
            ("🤖", "ML Predictions"),
            ("📋", "Logs"),
            ("⚙", "Settings")
        ]
        
        self.nav_buttons = []
        
        for icon, text in nav_items:
            btn = NavButton(icon, text)
            btn.clicked.connect(lambda checked, t=text: self.on_nav_clicked(t))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
        # Set Dashboard as active by default
        self.nav_buttons[0].set_active(True)
        
        layout.addStretch()
        
        # Version label
        version_label = QLabel("v1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #666666; font-size: 9pt; border: none;")
        layout.addWidget(version_label)
        
    def on_nav_clicked(self, page_name: str):
        """Handle navigation button click"""
        # Update active state
        for btn in self.nav_buttons:
            btn.set_active(btn.text == page_name)
            
        # Emit page change signal
        self.page_requested.emit(page_name)
        
    def toggle_sidebar(self):
        """Toggle sidebar collapsed state"""
        self.is_collapsed = not self.is_collapsed
        
        # Animate width change
        target_width = self.collapsed_width if self.is_collapsed else self.expanded_width
        
        animation = QPropertyAnimation(self, b"minimumWidth")
        animation.setDuration(300)
        animation.setStartValue(self.width())
        animation.setEndValue(target_width)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.start()
        
        # Update button text visibility
        for btn in self.nav_buttons:
            if self.is_collapsed:
                btn.setText(btn.icon)
            else:
                btn.setText(f"{btn.icon}  {btn.text}")