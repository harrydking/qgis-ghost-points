# QGIS Ghost Points Plugin

## Overview

A QGIS plugin that allows users to temporarily hide selected point features without deleting them with a single button click.

![Plugin screenshot](screenshots\readme_sc.png)

## Features

- Hide selected point features with a single click
- Reveal all hidden points at once
- Works with both local and PostGIS layers
- Maintains data integrity by using a non-destructive hiding mechanism
- Simple and intuitive toolbar interface

## Installation

### QGIS Plugin Manager (Coming Soon)

1. Open QGIS
2. Go to Plugins > Manage and Install Plugins
3. Search for "Ghost Points"
4. Click "Install Plugin"

### Manual Installation

1. Download the latest release
2. Copy the plugin folder to:
   - Windows: `C:\Users\[USERNAME]\.qgis3\python\plugins\`
   - Mac/Linux: `~/.qgis3/python/plugins/`

## Usage

### Hiding Points

- Select the point layer you want to work with in the Layers panel
- Select one or more points using any QGIS selection tool
- Click the "Ghost" button (ghost icon) in the toolbar
- Selected points will be hidden from view but remain in the dataset

### Revealing Points

- Select the layer containing hidden points
- Click the "No Ghost" button (crossed-out ghost icon) in the toolbar
- Confirm the action in the dialog box
- All previously hidden points will be revealed

### Technical Details

#### The plugin works by:

- Adding a \_hidden field to your layer (if it doesn't exist)
- Setting \_hidden = 1 for features you want to hide
- Applying a layer filter to hide features where \_hidden = 1
- For PostGIS layers, the layer is copied locally prior to \_hidden field being added (currently broken)

## Requirements

- QGIS 3.0+
- Python 3.6+
- Internet connection

## Compatibility

- Tested on QGIS 3.22
- Tested on Windows 11
- Tested on macOS 15 Sequoia

## License

GNU General Public License v3.0

## Author

Harry King

## Issues

- Currently contains broken databse code that will be removed and replaced with copying to local layer for PostGIS layers.
