import os
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, 
                            QVBoxLayout, QWidget, QLabel, QFileDialog, QHBoxLayout,
                            QSplitter, QTextEdit, QGroupBox, QScrollArea, QCheckBox,
                            QTabWidget, QMenu, QAction)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette
from pylatex import Document, Command, NoEscape
import markdown2  # For preview rendering

class FileTab(QWidget):
    """Widget to represent a single file tab"""
    def __init__(self, file_path=""):
        super().__init__()
        self.file_path = file_path
        self.latex_components = {}
        self.component_list = QListWidget()
        self.preview_area = QTextEdit()
        self.stats_label = QLabel("No components selected")
        
        self.initUI()
        
        if file_path:
            self.load_tex_file(file_path)
    
    def initUI(self):
        layout = QHBoxLayout()
        
        # Left panel - Components
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Component selection
        component_group = QGroupBox("Document Components")
        component_layout = QVBoxLayout()
        
        self.search_label = QLabel("Search Components:")
        self.search_box = QTextEdit()
        self.search_box.setMaximumHeight(30)
        self.search_box.textChanged.connect(self.filter_components)
        
        self.component_list.setSelectionMode(QListWidget.MultiSelection)
        self.component_list.itemSelectionChanged.connect(self.update_report)
        
        component_scroll = QScrollArea()
        component_scroll.setWidgetResizable(True)
        component_scroll.setWidget(self.component_list)
        
        component_layout.addWidget(self.search_label)
        component_layout.addWidget(self.search_box)
        component_layout.addWidget(component_scroll)
        component_group.setLayout(component_layout)
        left_layout.addWidget(component_group)
        
        left_panel.setLayout(left_layout)
        
        # Right panel - Preview and stats
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Preview pane
        preview_group = QGroupBox("Live Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_area.setReadOnly(True)
        self.preview_area.setStyleSheet("background-color: #f8f9fa;")
        
        preview_layout.addWidget(self.preview_area)
        preview_group.setLayout(preview_layout)
        right_layout.addWidget(preview_group)
        
        # Statistics
        stats_group = QGroupBox("Report Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_label.setStyleSheet("color: #7f8c8d;")
        
        stats_layout.addWidget(self.stats_label)
        stats_group.setLayout(stats_layout)
        right_layout.addWidget(stats_group)
        
        right_panel.setLayout(right_layout)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def load_tex_file(self, file_path):
        self.file_path = file_path
        self.parse_tex_file(file_path)
        self.populate_component_list()
    
    def parse_tex_file(self, filepath):
        self.latex_components = {}
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse document structure
        doc_parts = content.split(r'\begin{document}')
        if len(doc_parts) > 1:
            preamble = doc_parts[0]
            body = doc_parts[1].split(r'\end{document}')[0]
            
            # Title page components
            title_match = re.search(r'\\title\{(.*?)\}', preamble)
            author_match = re.search(r'\\author\{(.*?)\}', preamble)
            if title_match or author_match:
                self.latex_components["Title Page"] = {
                    'content': preamble + r'\maketitle',
                    'type': 'preamble'
                }
            
            # Extract sections and special environments
            self.extract_sections(body)
            self.extract_environments(body)
    
    def extract_sections(self, body):
        # Extract all sections and subsections
        sections = re.finditer(
            r'\\(section|subsection|subsubsection)\*?\{(.*?)\}(.*?)(?=\\section|\\subsection|\\subsubsection|\\end|$)',
            body, re.DOTALL)
        
        current_section = ""
        for match in sections:
            level = match.group(1)
            title = match.group(2).strip()
            content = match.group(3).strip()
            
            # Create hierarchical titles
            if level == "section":
                current_section = title
                self.latex_components[title] = {
                    'content': match.group(0),
                    'type': 'section'
                }
            elif level == "subsection":
                full_title = f"{current_section} > {title}"
                self.latex_components[full_title] = {
                    'content': match.group(0),
                    'type': 'subsection'
                }
    
    def extract_environments(self, body):
        # Extract common environments
        environments = {
            'abstract': r'\\begin\{abstract\}(.*?)\\end\{abstract\}',
            'figure': r'\\begin\{figure\}(.*?)\\end\{figure\}',
            'table': r'\\begin\{table\}(.*?)\\end\{table\}',
            'equation': r'\\begin\{equation\}(.*?)\\end\{equation\}'
        }
        
        for env, pattern in environments.items():
            matches = re.finditer(pattern, body, re.DOTALL)
            for i, match in enumerate(matches):
                title = f"{env.capitalize()} {i+1}"
                self.latex_components[title] = {
                    'content': match.group(0),
                    'type': env
                }
    
    def populate_component_list(self):
        self.component_list.clear()
        for component, data in self.latex_components.items():
            item = QListWidgetItem(component)
            
            # Color coding by type
            if data['type'] == 'preamble':
                item.setForeground(QColor('#3498db'))  # Blue
            elif data['type'] == 'section':
                item.setFont(QFont('Arial', 10, QFont.Bold))
            elif data['type'] == 'subsection':
                item.setForeground(QColor('#7f8c8d'))  # Gray
                item.setText(f"    {component}")  # Indent
            
            self.component_list.addItem(item)
    
    def filter_components(self):
        search_text = self.search_box.toPlainText().lower()
        for i in range(self.component_list.count()):
            item = self.component_list.item(i)
            item.setHidden(search_text not in item.text().lower())
    
    def update_report(self):
        selected_items = [self.component_list.item(i).text().strip() 
                        for i in range(self.component_list.count()) 
                        if self.component_list.item(i).isSelected()]
        
        # Update statistics
        self.stats_label.setText(
            f"Selected: {len(selected_items)} components\n"
            f"Estimated pages: {len(selected_items)//3 + 1}"
        )
        
        # Generate preview content
        preview_content = "# Custom Report Preview\n\n"
        for component in selected_items:
            data = self.latex_components.get(component, {})
            preview_content += f"## {component}\n```latex\n{data.get('content', '')}\n```\n\n"
        
        # Convert to HTML for better display
        html_content = markdown2.markdown(preview_content)
        self.preview_area.setHtml(html_content)
    
    def get_selected_components(self):
        return [self.component_list.item(i).text().strip() 
                for i in range(self.component_list.count()) 
                if self.component_list.item(i).isSelected()]

class PreviewWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Report Preview")
        self.setGeometry(300, 300, 600, 800)
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        layout = QVBoxLayout()
        layout.addWidget(self.preview)
        self.setLayout(layout)

class LatexReportGenerator(QMainWindow):
    update_preview = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LaTeX Report Composer")
        self.setGeometry(100, 100, 1200, 800)
        self.preview_window = None
        self.initUI()
        self.update_preview.connect(self.update_preview_content)
    
    def initUI(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # File control buttons
        controls_layout = QHBoxLayout()
        
        add_file_btn = QPushButton("📂 Add LaTeX File")
        add_file_btn.setStyleSheet(self.button_style())
        add_file_btn.clicked.connect(self.add_new_file)
        
        export_btn = QPushButton("💾 Export Report")
        export_btn.setStyleSheet(self.button_style())
        export_btn.clicked.connect(self.generate_report)
        
        controls_layout.addWidget(add_file_btn)
        controls_layout.addWidget(export_btn)
        controls_layout.addStretch()
        
        # Tab widget for multiple files
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self.show_tab_context_menu)
        # Enable tab reordering with drag and drop
        self.tab_widget.setMovable(True)
        # Create welcome tab
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout()
        welcome_label = QLabel("Welcome to LaTeX Report Composer!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; margin: 50px;")
        
        start_btn = QPushButton("Click to Add a LaTeX File")
        start_btn.setStyleSheet(self.button_style())
        start_btn.clicked.connect(self.add_new_file)
        start_btn.setFixedWidth(200)
        
        welcome_layout.addStretch()
        welcome_layout.addWidget(welcome_label)
        welcome_layout.addWidget(start_btn, 0, Qt.AlignCenter)
        welcome_layout.addStretch()
        welcome_widget.setLayout(welcome_layout)
        
        self.tab_widget.addTab(welcome_widget, "Welcome")
        
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.tab_widget)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def button_style(self):
        return """
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        """
    
    def add_new_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open LaTeX File", "", "TeX Files (*.tex)")
        
        if file_path:
            # Remove welcome tab if it exists
            if self.tab_widget.count() == 1 and self.tab_widget.tabText(0) == "Welcome":
                self.tab_widget.removeTab(0)
            
            # Create a new tab for the file
            file_tab = FileTab(file_path)
            tab_name = os.path.basename(file_path)
            index = self.tab_widget.addTab(file_tab, tab_name)
            
            # Switch to the new tab
            self.tab_widget.setCurrentIndex(index)
            self.statusBar().showMessage(f"Loaded: {file_path}")
    
    def close_tab(self, index):
        # Don't close the last tab, instead show welcome screen
        if self.tab_widget.count() <= 1:
            # Create welcome tab
            welcome_widget = QWidget()
            welcome_layout = QVBoxLayout()
            welcome_label = QLabel("Welcome to LaTeX Report Composer!")
            welcome_label.setAlignment(Qt.AlignCenter)
            welcome_label.setStyleSheet("font-size: 24px; margin: 50px;")
            
            start_btn = QPushButton("Click to Add a LaTeX File")
            start_btn.setStyleSheet(self.button_style())
            start_btn.clicked.connect(self.add_new_file)
            start_btn.setFixedWidth(200)
            
            welcome_layout.addStretch()
            welcome_layout.addWidget(welcome_label)
            welcome_layout.addWidget(start_btn, 0, Qt.AlignCenter)
            welcome_layout.addStretch()
            welcome_widget.setLayout(welcome_layout)
            
            self.tab_widget.removeTab(index)
            self.tab_widget.addTab(welcome_widget, "Welcome")
        else:
            self.tab_widget.removeTab(index)
    
    def show_tab_context_menu(self, position):
        # Don't show context menu for welcome tab
        if self.tab_widget.tabText(self.tab_widget.currentIndex()) == "Welcome":
            return
            
        menu = QMenu()
        close_action = QAction("Close Tab", self)
        close_action.triggered.connect(lambda: self.close_tab(self.tab_widget.currentIndex()))
        
        rename_action = QAction("Rename Tab", self)
        rename_action.triggered.connect(self.rename_current_tab)
        
        menu.addAction(close_action)
        menu.addAction(rename_action)
        menu.exec_(self.tab_widget.mapToGlobal(position))
    
    def rename_current_tab(self):
        current_index = self.tab_widget.currentIndex()
        current_name = self.tab_widget.tabText(current_index)
        # Here you could add a dialog to get a new name
        # For simplicity, we'll just add "(Modified)" to the name
        self.tab_widget.setTabText(current_index, current_name + " (Modified)")
    
    def toggle_preview(self):
        if not self.preview_window:
            self.preview_window = PreviewWindow(self)
            self.preview_window.show()
        elif self.preview_window.isVisible():
            self.preview_window.hide()
        else:
            self.preview_window.show()
    
    def update_preview_content(self, content):
        if self.preview_window:
            self.preview_window.preview.setHtml(content)
    
    def generate_report(self):
        # Don't generate report for welcome tab
        if self.tab_widget.tabText(self.tab_widget.currentIndex()) == "Welcome":
            self.statusBar().showMessage("Error: No file loaded!", 5000)
            return
        
        current_tab = self.tab_widget.currentWidget()
        selected_items = current_tab.get_selected_components()
        
        if not selected_items:
            self.statusBar().showMessage("Error: No components selected!", 5000)
            return
        
        doc = Document('custom_report', documentclass='article')
        
        # Add selected components
        for component in selected_items:
            data = current_tab.latex_components.get(component, {})
            if component == "Title Page" and data.get('type') == 'preamble':
                # Handle preamble separately
                doc.preamble.append(NoEscape(data['content'].split(r'\maketitle')[0]))
                doc.append(NoEscape(r'\maketitle'))
            else:
                doc.append(NoEscape(data.get('content', '')))
        
        # Generate PDF
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Report", "custom_report.pdf", "PDF Files (*.pdf)")
            
            if file_path:
                if not file_path.endswith('.pdf'):
                    file_path += '.pdf'
                
                doc.generate_pdf(file_path.replace('.pdf', ''), clean_tex=True)
                self.statusBar().showMessage(f"Successfully generated: {file_path}", 5000)
                
                # Offer to open the file
                open_btn = QPushButton("Open PDF")
                open_btn.clicked.connect(lambda: os.startfile(file_path))
                self.statusBar().addPermanentWidget(open_btn)
                
        except Exception as e:
            self.statusBar().showMessage(f"Error: {str(e)}", 5000)

if __name__ == '__main__':
    app = QApplication([])
    app.setStyle('Fusion')  # Modern UI style
    
    # Set palette for dark mode
    palette = app.palette()
    palette.setColor(palette.Window, QColor(240, 240, 240))
    app.setPalette(palette)
    
    window = LatexReportGenerator()
    window.show()
    app.exec_()