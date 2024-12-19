from PyQt5.QtWidgets import QAction, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QVariant
from qgis.core import (QgsField, QgsFieldConstraints, 
                       QgsDataSourceUri, QgsFields, QgsVectorLayer)
import psycopg2
import os

class GhostPoints:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.ghosted_features = set()

    def initGui(self):
        # Add "Ghost" button
        iconpath1 = os.path.join(self.plugin_dir, 'ghost_icon.png')
        self.action_ghost = QAction(
            QIcon(iconpath1), 'Summon Ghost', self.iface.mainWindow()
        )
        self.action_ghost.triggered.connect(self.hide_selected_points)
        self.iface.addToolBarIcon(self.action_ghost)

        # Add "No Ghost" button
        iconpath2 = os.path.join(self.plugin_dir, 'no_ghost_icon.png')
        self.action_no_ghost = QAction(
            QIcon(iconpath2), 'Banish Ghost', self.iface.mainWindow()
        )
        self.action_no_ghost.triggered.connect(self.reveal_all_points)
        self.iface.addToolBarIcon(self.action_no_ghost)

    def unload(self):
        self.iface.removeToolBarIcon(self.action_ghost)
        self.iface.removeToolBarIcon(self.action_no_ghost)

    def get_postgis_connection_params(self, layer):
        """
        Extract PostgreSQL connection parameters from the layer
        """
        uri = QgsDataSourceUri(layer.dataProvider().dataSourceUri())
        return {
            'host': uri.host(),
            'port': uri.port(),
            'database': uri.database(),
            'user': uri.username(),
            'password': uri.password(),
            'schema': uri.schema() or 'public',
            'table': uri.table()
        }

    def ensure_hidden_field(self, layer):
        """
        Ensure the '_hidden' field exists in the layer.
        If the layer is a PostGIS layer, it checks/adds the field.
        """
        # Check if the field already exists
        if '_hidden' in [field.name() for field in layer.fields()]:
            return

        # Check if it's a PostGIS layer
        if not isinstance(layer, QgsVectorLayer):
            QMessageBox.warning(
                self.iface.mainWindow(),
                'Ghost Points',
                'Layer must be a vector layer.'
            )
            return

        try:
            # Start editing mode
            layer.startEditing()

            # Create field using standard QgsField constructor
            hidden_field = QgsField(
                name='_hidden', 
                type=QVariant.Int, 
                len=1, 
                prec=0, 
                comment='Ghost points hidden status'
            )
            
            # Add the field to the layer
            layer.dataProvider().addAttributes([hidden_field])
            
            # Commit changes
            layer.commitChanges()

            # Refresh layer
            layer.updateFields()

        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                'Ghost Points Error',
                f'Error adding "_hidden" field:\n{e}'
            )
            if layer.isEditing():
                layer.rollBack()

    def apply_visibility(self, layer, hide):
        """
        Update the visibility of features by modifying the '_hidden' attribute
        and applying a filter to the layer.
        """
        try:
            # Start editing
            layer.startEditing()

            # Update hidden status for specified features
            hidden_field_index = layer.fields().lookupField('_hidden')
            for feature_id in self.ghosted_features:
                layer.changeAttributeValue(
                    feature_id,
                    hidden_field_index,
                    1 if hide else 0
                )

            # Commit changes
            layer.commitChanges()

            # Apply filter
            if hide:
                layer.setSubsetString("_hidden = 0 OR _hidden IS NULL")
            else:
                layer.setSubsetString("")

            # Trigger repaint
            layer.triggerRepaint()

        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                'Ghost Points Error',
                f'Error applying visibility:\n{e}'
            )
            if layer.isEditing():
                layer.rollBack()

    def hide_selected_points(self):
        """
        Hide selected points by setting their '_hidden' attribute to 1
        and applying a filter to the layer.
        """
        layer = self.iface.activeLayer()
        if not layer or layer.type() != layer.VectorLayer or layer.geometryType() != 0:
            QMessageBox.warning(
                self.iface.mainWindow(),
                'Ghost Points',
                'Please select a valid point layer.'
            )
            return

        # Ensure '_hidden' field exists
        self.ensure_hidden_field(layer)

        # Get selected features
        features = layer.selectedFeatures()
        if not features:
            QMessageBox.information(self.iface.mainWindow(), 'Ghost Points', 'No features selected.')
            return

        # Add selected feature IDs to the ghosted set
        for feature in features:
            self.ghosted_features.add(feature.id())

        # Apply visibility changes
        self.apply_visibility(layer, hide=True)

    def reveal_all_points(self):
        """
        Reveal all hidden points by resetting the '_hidden' attribute to 0
        and clearing the filter.
        """
        layer = self.iface.activeLayer()
        if not layer or layer.type() != layer.VectorLayer or layer.geometryType() != 0:
            QMessageBox.warning(
                self.iface.mainWindow(),
                'Ghost Points',
                'Please select a valid point layer.'
            )
            return

        # Confirm reveal
        reply = QMessageBox.question(
            self.iface.mainWindow(),
            'Confirm Reveal',
            'Are you sure you want to reveal all hidden points?',
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.No:
            return

        # Start editing
        layer.startEditing()

        # Reset '_hidden' attribute for all features
        hidden_field_index = layer.fields().lookupField('_hidden')
        for feature_id in self.ghosted_features:
            layer.changeAttributeValue(
                feature_id,
                hidden_field_index,
                0
            )

        # Commit changes
        layer.commitChanges()

        # Clear the ghosted features set
        self.ghosted_features.clear()

        # Clear the filter
        self.apply_visibility(layer, hide=False)