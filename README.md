# LaTeX Report Composer

A PyQt5-based application that allows you to compose custom LaTeX reports by selecting components from existing LaTeX files.

![LaTeX Report Composer](https://example.com/placeholder-image.png)

## Features

- Load and parse existing LaTeX files (.tex)
- Extract document components (sections, subsections, environments)
- Create custom reports by selecting components from multiple files
- Live preview of selected components
- Export combined report as Tex file
- Search functionality to filter components
- Multi-file support through tabbed interface
- Document statistics for selected components

## Requirements

- Python 3.6+
- PyQt5
- pylatex
- markdown2
- LaTeX installation (for Tex export)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/latex-report-composer.git
cd latex-report-composer
```

2. Install required Python packages:
```bash
pip install PyQt5 pylatex markdown2
```

3. Make sure you have a working LaTeX installation (such as MiKTeX or TeX Live)

## Usage

1. Run the application:
```bash
python pyGUI.py
```

2. Click "Add LaTeX File" to load an existing .tex file
3. Select components from the file that you want to include in your report
4. Use the search box to filter components if needed
5. View the live preview of your custom report
6. Click "Export Report" to generate a LaTex file

## Interface Guide

### Main Window
- **Add LaTeX File**: Open a file browser to select a .tex file to load
- **Export Report**: Generate a PDF from selected components
- **Tab Interface**: Each loaded file appears in its own tab

### File Tab
- **Left Panel**: Shows document components that can be selected
- **Search Box**: Filter components by name
- **Right Panel**: 
  - **Live Preview**: Shows Markdown preview of selected components
  - **Report Statistics**: Displays information about the selected components

## How It Works

1. The application parses LaTeX files and extracts structural components
2. Components are displayed in a hierarchical list with color coding:
   - Blue: Title page and preamble components
   - Bold: Section headings
   - Gray & Indented: Subsections
3. Selected components are combined to create a new LaTeX document
4. The pylatex library is used to generate the final LaTex output

## Component Types

LaTeX Report Composer recognizes these component types:
- Title Page (from document preamble)
- Sections
- Subsections
- Abstract environments
- Figures
- Tables
- Equations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- PyQt5 for the GUI framework
- pylatex for LaTeX document generation
- markdown2 for preview rendering
