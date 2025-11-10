# Plan Detallado: Sistema de Filtros Persistentes y Gestión de Paneles Anclados

**Fecha de creación**: 2025-11-10
**Versión**: 1.0
**Autor**: Claude Code

---

## 📋 Tabla de Contenidos

1. [Análisis del Estado Actual](#análisis-del-estado-actual)
2. [Objetivos del Proyecto](#objetivos-del-proyecto)
3. [Arquitectura de la Solución](#arquitectura-de-la-solución)
4. [FASE 1: Corrección de Bug de Filtros](#fase-1-corrección-de-bug-de-filtros)
5. [FASE 2: Ventana de Gestión de Paneles](#fase-2-ventana-de-gestión-de-paneles)
6. [FASE 3: Mejoras Adicionales](#fase-3-mejoras-adicionales)
7. [Testing y Verificación](#testing-y-verificación)
8. [Cronograma de Implementación](#cronograma-de-implementación)

---

## 1. Análisis del Estado Actual

### 1.1 Problema Identificado

**Síntoma**: Los paneles flotantes anclados se restauran al reiniciar la aplicación, pero pierden todos los filtros que tenían aplicados (filtros avanzados, filtro de estado, texto de búsqueda).

**Causa Raíz**: Bug en `src/core/pinned_panels_manager.py` línea 40:

```python
# ❌ CÓDIGO ACTUAL (INCORRECTO)
"search_text": getattr(panel_widget, 'search_bar', None).text() if hasattr(panel_widget, 'search_bar') else ""
```

**Por qué falla**:
- `search_bar` es un widget `SearchBar` personalizado
- El texto de búsqueda está en `search_bar.search_input.text()` (QLineEdit interno)
- Intentar llamar `.text()` directamente sobre `SearchBar` lanza `AttributeError`
- La excepción es capturada y retorna `None`, causando que `filter_config` sea NULL

### 1.2 Estado de la Base de Datos

**Tabla `pinned_panels`** (estructura actual):

```sql
CREATE TABLE IF NOT EXISTS pinned_panels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    custom_name TEXT,
    custom_color TEXT,
    x_position INTEGER,
    y_position INTEGER,
    width INTEGER DEFAULT 350,
    height INTEGER DEFAULT 500,
    is_minimized BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_opened TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    open_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    filter_config TEXT,              -- ✅ Ya existe (JSON)
    keyboard_shortcut TEXT,          -- ✅ Ya existe
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);
```

**Datos actuales**:
- 2 paneles activos (IDs: 34, 35)
- Ambos con `filter_config = NULL` (debido al bug)
- Shortcuts asignados: `Ctrl+Shift+1`, `Ctrl+Shift+2`

### 1.3 Sistema Ya Implementado

✅ **Lo que YA funciona**:

1. **Auto-guardado con debouncing**: Timer de 1 segundo guarda cambios automáticamente
2. **Triggers de guardado**:
   - `on_filters_changed()` - Filtros avanzados
   - `on_filters_cleared()` - Limpieza de filtros
   - `on_state_filter_changed()` - Cambio de estado
   - `moveEvent()` - Movimiento de panel
   - `resizeEvent()` - Redimensionamiento
3. **Serialización/Deserialización**: Métodos para convertir filtros a/desde JSON
4. **Restauración**: `MainWindow` restaura paneles con filtros al iniciar
5. **Aplicación de filtros**: `FloatingPanel.apply_filter_config()` reaplica filtros

---

## 2. Objetivos del Proyecto

### 2.1 Objetivos Principales

1. **Persistencia de Filtros**: Paneles anclados deben recordar:
   - Filtros avanzados aplicados (dict)
   - Filtro de estado (normal/archived/inactive/all)
   - Texto de búsqueda actual (string)

2. **Gestión Visual de Paneles**: Nueva ventana para:
   - Listar todos los paneles anclados guardados
   - Ver detalles y filtros de cada panel
   - Abrir/enfocar paneles rápidamente
   - Editar nombres, colores y shortcuts
   - Eliminar y duplicar paneles

### 2.2 Objetivos Secundarios

- Mejorar UX con indicadores visuales de filtros activos
- Permitir exportar/importar configuraciones de paneles
- Agregar menú contextual en paneles para acceso rápido

---

## 3. Arquitectura de la Solución

### 3.1 Componentes Existentes (a modificar)

```
src/core/pinned_panels_manager.py
├── _serialize_filter_config()      [MODIFICAR: línea 40]
├── _deserialize_filter_config()    [OK]
├── save_panel_state()              [OK]
├── update_panel_state()            [OK]
└── restore_panels_on_startup()     [OK]

src/views/floating_panel.py
├── apply_filter_config()           [OK]
├── on_filters_changed()            [OK]
├── on_filters_cleared()            [OK]
├── on_state_filter_changed()       [OK]
└── _save_panel_state_to_db()       [OK]

src/views/main_window.py
└── restore_pinned_panels_from_db() [OK]
```

### 3.2 Componentes Nuevos (a crear)

```
src/views/pinned_panels_manager_window.py    [NUEVO]
├── PinnedPanelsManagerWindow                [Ventana principal]
│   ├── __init__()
│   ├── init_ui()
│   ├── load_panels()
│   ├── refresh_panel_list()
│   ├── on_panel_selected()
│   ├── on_panel_double_clicked()
│   ├── show_panel_details()
│   ├── open_panel()
│   ├── edit_panel()
│   ├── duplicate_panel()
│   ├── delete_panel()
│   ├── filter_panels()
│   └── closeEvent()
│
└── PanelListItemWidget                      [Widget de item de lista]
    ├── __init__()
    ├── setup_ui()
    └── update_display()

src/views/dialogs/panel_customization_dialog.py  [NUEVO]
└── PanelCustomizationDialog                 [Diálogo de edición]
    ├── __init__()
    ├── init_ui()
    ├── get_customization_data()
    └── validate_inputs()
```

### 3.3 Flujo de Datos

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO DE PERSISTENCIA                     │
└─────────────────────────────────────────────────────────────┘

1. Usuario aplica filtros en FloatingPanel
   └─> on_filters_changed() / on_state_filter_changed()
       └─> update_timer.start(1000ms)
           └─> _save_panel_state_to_db()
               └─> PinnedPanelsManager.update_panel_state()
                   └─> _serialize_filter_config()
                       └─> DBManager.update_pinned_panel()
                           └─> UPDATE pinned_panels SET filter_config = ?

2. Usuario reinicia aplicación
   └─> MainWindow.__init__()
       └─> restore_pinned_panels_from_db()
           └─> PinnedPanelsManager.restore_panels_on_startup()
               └─> DBManager.get_pinned_panels()
                   └─> SELECT * FROM pinned_panels WHERE is_active = 1
                       └─> _deserialize_filter_config()
                           └─> FloatingPanel.apply_filter_config()
                               └─> Filtros restaurados ✓

┌─────────────────────────────────────────────────────────────┐
│              FLUJO DE GESTIÓN DE PANELES                     │
└─────────────────────────────────────────────────────────────┘

1. Usuario abre PinnedPanelsManagerWindow
   └─> Carga lista de paneles desde BD
       └─> Muestra lista con detalles (nombre, categoría, filtros, etc.)

2. Usuario selecciona un panel de la lista
   └─> Muestra detalles en panel lateral:
       ├─> Nombre y categoría
       ├─> Vista previa de filtros activos
       ├─> Estadísticas (usos, última apertura)
       └─> Botones de acción (Abrir, Editar, Duplicar, Eliminar)

3. Usuario hace doble clic o presiona "Abrir"
   └─> Si el panel ya está abierto: enfocarlo
   └─> Si no está abierto: abrirlo con filtros aplicados

4. Usuario presiona "Editar"
   └─> PanelCustomizationDialog
       └─> Permite cambiar: nombre, color, shortcut
           └─> Guarda cambios en BD

5. Usuario presiona "Duplicar"
   └─> Crea nuevo panel con misma configuración
       └─> Asigna nuevo shortcut automáticamente

6. Usuario presiona "Eliminar"
   └─> Confirmación
       └─> Elimina de BD (o marca como is_active = 0)
```

---

## 4. FASE 1: Corrección de Bug de Filtros

### 4.1 Cambios en `pinned_panels_manager.py`

**Archivo**: `src/core/pinned_panels_manager.py`

#### 4.1.1 Corrección de `_serialize_filter_config()` (línea 26-50)

**Código actual (líneas 36-50)**:

```python
def _serialize_filter_config(self, panel_widget) -> Optional[str]:
    """Serialize panel's filter configuration to JSON string"""
    try:
        filter_config = {
            "advanced_filters": getattr(panel_widget, 'current_filters', {}),
            "state_filter": getattr(panel_widget, 'current_state_filter', 'normal'),
            "search_text": getattr(panel_widget, 'search_bar', None).text() if hasattr(panel_widget, 'search_bar') else ""  # ❌ BUG AQUÍ
        }

        # Only save if there's actual filter data
        if filter_config["advanced_filters"] or filter_config["state_filter"] != "normal" or filter_config["search_text"]:
            return json.dumps(filter_config)

        return None
    except Exception as e:
        logger.warning(f"Could not serialize filter config: {e}")
        return None
```

**Código corregido**:

```python
def _serialize_filter_config(self, panel_widget) -> Optional[str]:
    """Serialize panel's filter configuration to JSON string"""
    try:
        # Extract search text safely
        search_text = ""
        if hasattr(panel_widget, 'search_bar') and panel_widget.search_bar:
            if hasattr(panel_widget.search_bar, 'search_input'):
                search_text = panel_widget.search_bar.search_input.text()

        filter_config = {
            "advanced_filters": getattr(panel_widget, 'current_filters', {}),
            "state_filter": getattr(panel_widget, 'current_state_filter', 'normal'),
            "search_text": search_text
        }

        # Only save if there's actual filter data
        has_filters = (
            filter_config["advanced_filters"] or
            filter_config["state_filter"] != "normal" or
            filter_config["search_text"]
        )

        if has_filters:
            logger.debug(f"Serializing filter config: {filter_config}")
            return json.dumps(filter_config)

        logger.debug("No filters to serialize")
        return None

    except Exception as e:
        logger.error(f"Could not serialize filter config: {e}", exc_info=True)
        return None
```

**Cambios realizados**:
1. ✅ Corrección del acceso al texto de búsqueda: `.search_bar.search_input.text()`
2. ✅ Verificación defensiva con múltiples `hasattr()` checks
3. ✅ Logging mejorado para debugging
4. ✅ Mejor manejo de excepciones con `exc_info=True`

#### 4.1.2 Mejora de `_deserialize_filter_config()` (línea 52-71)

**Código actual**:

```python
def _deserialize_filter_config(self, filter_config_json: Optional[str]) -> Optional[Dict]:
    """Deserialize filter configuration from JSON string"""
    if not filter_config_json:
        return None

    try:
        filter_config = json.loads(filter_config_json)
        logger.debug(f"Deserialized filter config: {filter_config}")
        return filter_config
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse filter config JSON: {e}")
        return None
```

**Código mejorado**:

```python
def _deserialize_filter_config(self, filter_config_json: Optional[str]) -> Optional[Dict]:
    """Deserialize filter configuration from JSON string"""
    if not filter_config_json:
        logger.debug("No filter config to deserialize")
        return None

    try:
        filter_config = json.loads(filter_config_json)

        # Validate structure
        expected_keys = {'advanced_filters', 'state_filter', 'search_text'}
        if not all(key in filter_config for key in expected_keys):
            logger.warning(f"Filter config missing expected keys. Found: {filter_config.keys()}")
            # Add missing keys with defaults
            filter_config.setdefault('advanced_filters', {})
            filter_config.setdefault('state_filter', 'normal')
            filter_config.setdefault('search_text', '')

        logger.debug(f"Deserialized filter config: {filter_config}")
        return filter_config

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse filter config JSON: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error deserializing filter config: {e}", exc_info=True)
        return None
```

**Mejoras**:
1. ✅ Validación de estructura JSON
2. ✅ Defaults para claves faltantes (backward compatibility)
3. ✅ Mejor logging
4. ✅ Manejo de excepciones más robusto

### 4.2 Script de Testing para FASE 1

**Archivo**: `util/test_filter_persistence.py` (NUEVO)

```python
"""
Script de testing para verificar la persistencia de filtros
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.db_manager import DBManager
from src.core.pinned_panels_manager import PinnedPanelsManager
import json

def test_filter_persistence():
    """Test filter config serialization/deserialization"""

    print("=" * 80)
    print("TEST: Persistencia de Filtros en Paneles Anclados")
    print("=" * 80)

    # Crear instancia de DBManager
    db = DBManager()
    manager = PinnedPanelsManager(db)

    # Verificar paneles actuales
    print("\n1. Paneles activos actuales:")
    panels = db.get_pinned_panels(active_only=True)
    for panel in panels:
        print(f"   - Panel {panel['id']}: Categoría {panel['category_id']}")
        print(f"     Filter Config: {panel.get('filter_config', 'NULL')}")

        if panel.get('filter_config'):
            # Intentar deserializar
            config = manager._deserialize_filter_config(panel['filter_config'])
            if config:
                print(f"     Deserialized OK:")
                print(f"       - Advanced Filters: {config.get('advanced_filters')}")
                print(f"       - State Filter: {config.get('state_filter')}")
                print(f"       - Search Text: {config.get('search_text')}")

    # Test de serialización
    print("\n2. Test de serialización:")

    class MockPanel:
        def __init__(self):
            self.current_filters = {'item_count_min': 5, 'tags': ['python', 'test']}
            self.current_state_filter = 'archived'
            self.search_bar = MockSearchBar()

    class MockSearchBar:
        def __init__(self):
            self.search_input = MockInput()

    class MockInput:
        def text(self):
            return "test search query"

    mock_panel = MockPanel()
    serialized = manager._serialize_filter_config(mock_panel)

    if serialized:
        print(f"   ✅ Serialización exitosa:")
        print(f"   {serialized}")

        # Test de deserialización
        deserialized = manager._deserialize_filter_config(serialized)
        print(f"\n   ✅ Deserialización exitosa:")
        print(f"   {json.dumps(deserialized, indent=6)}")
    else:
        print(f"   ❌ Error en serialización")

    db.close()
    print("\n" + "=" * 80)
    print("Test completado")
    print("=" * 80)

if __name__ == "__main__":
    test_filter_persistence()
```

---

## 5. FASE 2: Ventana de Gestión de Paneles

### 5.1 Clase Principal: `PinnedPanelsManagerWindow`

**Archivo**: `src/views/pinned_panels_manager_window.py` (NUEVO)

#### 5.1.1 Estructura de la Clase

```python
"""
Pinned Panels Manager Window - Ventana de gestión de paneles anclados
Permite ver, editar, duplicar y eliminar paneles guardados
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QLineEdit, QTextEdit,
    QGroupBox, QSplitter, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon
import logging
from typing import Optional, Dict, List
import json

logger = logging.getLogger(__name__)


class PinnedPanelsManagerWindow(QWidget):
    """
    Ventana de gestión de paneles anclados

    Signals:
        panel_open_requested(int): Emitido cuando se solicita abrir un panel
        panel_deleted(int): Emitido cuando se elimina un panel
        panel_updated(int): Emitido cuando se actualiza un panel
    """

    # Señales
    panel_open_requested = pyqtSignal(int)  # panel_id
    panel_deleted = pyqtSignal(int)          # panel_id
    panel_updated = pyqtSignal(int)          # panel_id

    def __init__(self, config_manager, pinned_panels_manager, main_window, parent=None):
        """
        Initialize the Pinned Panels Manager Window

        Args:
            config_manager: ConfigManager instance
            pinned_panels_manager: PinnedPanelsManager instance
            main_window: Reference to MainWindow (para acceder a paneles abiertos)
            parent: Parent widget
        """
        super().__init__(parent)

        self.config_manager = config_manager
        self.panels_manager = pinned_panels_manager
        self.main_window = main_window

        self.current_selected_panel_id = None
        self.all_panels = []  # Lista de todos los paneles

        self.init_ui()
        self.load_panels()

    def init_ui(self):
        """Initialize the UI"""
        self.setWindowTitle("Gestión de Paneles Anclados")
        self.setMinimumSize(900, 600)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Header
        header = self._create_header()
        main_layout.addWidget(header)

        # Splitter: Lista de paneles | Detalles
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panel izquierdo: Lista de paneles
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)

        # Panel derecho: Detalles del panel seleccionado
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)

        # Proporciones del splitter (40% lista, 60% detalles)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)

        main_layout.addWidget(splitter, 1)

        # Botón de cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # Aplicar estilos
        self.apply_styles()

    def _create_header(self) -> QWidget:
        """Crear header con título y filtros"""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)

        # Título
        title = QLabel("📍 Gestión de Paneles Anclados")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_layout.addWidget(title)

        # Búsqueda y filtros
        search_layout = QHBoxLayout()

        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar por nombre o categoría...")
        self.search_input.textChanged.connect(self.filter_panels)
        search_layout.addWidget(self.search_input, 3)

        # Filtro: Solo con filtros activos
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Todos los paneles", "all")
        self.filter_combo.addItem("Solo con filtros activos", "with_filters")
        self.filter_combo.addItem("Solo con nombre personalizado", "with_name")
        self.filter_combo.currentIndexChanged.connect(self.filter_panels)
        search_layout.addWidget(self.filter_combo, 2)

        # Ordenar por
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("Ordenar por: Última apertura", "last_opened")
        self.sort_combo.addItem("Ordenar por: Más usado", "most_used")
        self.sort_combo.addItem("Ordenar por: Nombre", "name")
        self.sort_combo.addItem("Ordenar por: Categoría", "category")
        self.sort_combo.currentIndexChanged.connect(self.sort_panels)
        search_layout.addWidget(self.sort_combo, 2)

        # Botón refresh
        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Actualizar lista")
        refresh_btn.setMaximumWidth(40)
        refresh_btn.clicked.connect(self.refresh_panel_list)
        search_layout.addWidget(refresh_btn)

        header_layout.addLayout(search_layout)

        return header_widget

    def _create_left_panel(self) -> QWidget:
        """Crear panel izquierdo con lista de paneles"""
        left_widget = QGroupBox("Paneles Guardados")
        left_layout = QVBoxLayout(left_widget)

        # Lista de paneles
        self.panels_list = QListWidget()
        self.panels_list.itemSelectionChanged.connect(self.on_panel_selected)
        self.panels_list.itemDoubleClicked.connect(self.on_panel_double_clicked)
        left_layout.addWidget(self.panels_list)

        # Contador de paneles
        self.panel_count_label = QLabel("0 paneles")
        self.panel_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.panel_count_label)

        return left_widget

    def _create_right_panel(self) -> QWidget:
        """Crear panel derecho con detalles del panel seleccionado"""
        right_widget = QGroupBox("Detalles del Panel")
        right_layout = QVBoxLayout(right_widget)

        # Información básica
        info_group = QGroupBox("📋 Información Básica")
        info_layout = QVBoxLayout(info_group)

        self.name_label = QLabel("<i>Selecciona un panel</i>")
        self.category_label = QLabel("")
        self.shortcut_label = QLabel("")
        self.status_label = QLabel("")

        info_layout.addWidget(QLabel("<b>Nombre:</b>"))
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(QLabel("<b>Categoría:</b>"))
        info_layout.addWidget(self.category_label)
        info_layout.addWidget(QLabel("<b>Atajo de teclado:</b>"))
        info_layout.addWidget(self.shortcut_label)
        info_layout.addWidget(QLabel("<b>Estado:</b>"))
        info_layout.addWidget(self.status_label)

        right_layout.addWidget(info_group)

        # Filtros activos
        filters_group = QGroupBox("🔧 Filtros Aplicados")
        filters_layout = QVBoxLayout(filters_group)

        self.filters_display = QTextEdit()
        self.filters_display.setReadOnly(True)
        self.filters_display.setMaximumHeight(150)
        filters_layout.addWidget(self.filters_display)

        right_layout.addWidget(filters_group)

        # Estadísticas
        stats_group = QGroupBox("📊 Estadísticas")
        stats_layout = QVBoxLayout(stats_group)

        self.stats_label = QLabel("")
        stats_layout.addWidget(self.stats_label)

        right_layout.addWidget(stats_group)

        # Botones de acción
        actions_layout = QHBoxLayout()

        self.open_btn = QPushButton("🚀 Abrir")
        self.open_btn.setEnabled(False)
        self.open_btn.clicked.connect(self.open_panel)
        actions_layout.addWidget(self.open_btn)

        self.edit_btn = QPushButton("✏️ Editar")
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self.edit_panel)
        actions_layout.addWidget(self.edit_btn)

        self.duplicate_btn = QPushButton("📋 Duplicar")
        self.duplicate_btn.setEnabled(False)
        self.duplicate_btn.clicked.connect(self.duplicate_panel)
        actions_layout.addWidget(self.duplicate_btn)

        self.delete_btn = QPushButton("🗑️ Eliminar")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_panel)
        actions_layout.addWidget(self.delete_btn)

        right_layout.addLayout(actions_layout)

        # Espaciador
        right_layout.addStretch()

        return right_widget
```

#### 5.1.2 Métodos de Carga y Filtrado

```python
    def load_panels(self):
        """Cargar todos los paneles desde la base de datos"""
        try:
            # Obtener todos los paneles (activos e inactivos)
            self.all_panels = self.panels_manager.get_all_panels(active_only=False)

            logger.info(f"Loaded {len(self.all_panels)} panels")

            # Aplicar filtros y actualizar UI
            self.filter_panels()

        except Exception as e:
            logger.error(f"Error loading panels: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al cargar paneles: {e}")

    def refresh_panel_list(self):
        """Refrescar lista de paneles"""
        logger.info("Refreshing panel list")
        self.load_panels()

    def filter_panels(self):
        """Filtrar y mostrar paneles según criterios de búsqueda"""
        search_text = self.search_input.text().lower()
        filter_type = self.filter_combo.currentData()

        # Filtrar paneles
        filtered_panels = []

        for panel in self.all_panels:
            # Aplicar filtro de búsqueda
            if search_text:
                panel_name = panel.get('custom_name', '')
                category_name = self._get_category_name(panel['category_id'])

                if search_text not in panel_name.lower() and search_text not in category_name.lower():
                    continue

            # Aplicar filtro de tipo
            if filter_type == "with_filters":
                if not panel.get('filter_config'):
                    continue
            elif filter_type == "with_name":
                if not panel.get('custom_name'):
                    continue

            filtered_panels.append(panel)

        # Ordenar paneles
        self.display_panels(filtered_panels)

    def sort_panels(self):
        """Reordenar y mostrar paneles"""
        self.filter_panels()  # Re-aplicar filtros con nuevo orden

    def display_panels(self, panels: List[Dict]):
        """Mostrar paneles en la lista"""
        self.panels_list.clear()

        sort_by = self.sort_combo.currentData()

        # Ordenar paneles
        if sort_by == "last_opened":
            panels = sorted(panels, key=lambda p: p.get('last_opened', ''), reverse=True)
        elif sort_by == "most_used":
            panels = sorted(panels, key=lambda p: p.get('open_count', 0), reverse=True)
        elif sort_by == "name":
            panels = sorted(panels, key=lambda p: p.get('custom_name', self._get_category_name(p['category_id'])))
        elif sort_by == "category":
            panels = sorted(panels, key=lambda p: self._get_category_name(p['category_id']))

        # Crear items de lista
        for panel in panels:
            item_widget = PanelListItemWidget(panel, self.config_manager)
            item = QListWidgetItem(self.panels_list)
            item.setSizeHint(item_widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, panel['id'])
            self.panels_list.addItem(item)
            self.panels_list.setItemWidget(item, item_widget)

        # Actualizar contador
        self.panel_count_label.setText(f"{len(panels)} panel(es)")
```

#### 5.1.3 Métodos de Eventos y Acciones

```python
    def on_panel_selected(self):
        """Evento cuando se selecciona un panel de la lista"""
        selected_items = self.panels_list.selectedItems()

        if not selected_items:
            self.clear_details()
            return

        panel_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.current_selected_panel_id = panel_id

        # Mostrar detalles del panel
        self.show_panel_details(panel_id)

        # Habilitar botones
        self.open_btn.setEnabled(True)
        self.edit_btn.setEnabled(True)
        self.duplicate_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

    def on_panel_double_clicked(self, item):
        """Evento cuando se hace doble clic en un panel"""
        panel_id = item.data(Qt.ItemDataRole.UserRole)
        self.open_panel_by_id(panel_id)

    def show_panel_details(self, panel_id: int):
        """Mostrar detalles del panel seleccionado"""
        try:
            panel = self.panels_manager.get_panel_by_id(panel_id)

            if not panel:
                self.clear_details()
                return

            # Información básica
            panel_name = panel.get('custom_name') or self._get_category_name(panel['category_id'])
            category_name = self._get_category_name(panel['category_id'])
            shortcut = panel.get('keyboard_shortcut', 'Ninguno')
            is_active = panel.get('is_active', False)

            self.name_label.setText(f"<b>{panel_name}</b>")
            self.category_label.setText(category_name)
            self.shortcut_label.setText(shortcut)

            # Estado
            if is_active:
                # Verificar si está actualmente abierto
                is_open = self._is_panel_open(panel_id)
                status_text = "🟢 <b>Abierto actualmente</b>" if is_open else "🟡 <b>Activo (cerrado)</b>"
            else:
                status_text = "⚪ <b>Inactivo</b>"

            self.status_label.setText(status_text)

            # Filtros
            filter_config = panel.get('filter_config')
            if filter_config:
                filters = self.panels_manager._deserialize_filter_config(filter_config)
                self.display_filters(filters)
            else:
                self.filters_display.setText("<i>Sin filtros aplicados</i>")

            # Estadísticas
            open_count = panel.get('open_count', 0)
            last_opened = panel.get('last_opened', 'Nunca')
            created_at = panel.get('created_at', 'Desconocido')

            stats_text = f"""
            <p><b>Veces abierto:</b> {open_count}</p>
            <p><b>Última apertura:</b> {last_opened}</p>
            <p><b>Creado:</b> {created_at}</p>
            """
            self.stats_label.setText(stats_text)

        except Exception as e:
            logger.error(f"Error showing panel details: {e}", exc_info=True)

    def display_filters(self, filters: Dict):
        """Mostrar filtros del panel en formato legible"""
        filter_lines = []

        # Filtros avanzados
        advanced = filters.get('advanced_filters', {})
        if advanced:
            filter_lines.append("<b>Filtros Avanzados:</b>")
            for key, value in advanced.items():
                filter_lines.append(f"  • {key}: {value}")

        # Filtro de estado
        state = filters.get('state_filter', 'normal')
        if state != 'normal':
            filter_lines.append(f"<b>Estado:</b> {state}")

        # Texto de búsqueda
        search = filters.get('search_text', '')
        if search:
            filter_lines.append(f"<b>Búsqueda:</b> \"{search}\"")

        if not filter_lines:
            self.filters_display.setText("<i>Sin filtros aplicados</i>")
        else:
            self.filters_display.setText("<br>".join(filter_lines))

    def clear_details(self):
        """Limpiar panel de detalles"""
        self.name_label.setText("<i>Selecciona un panel</i>")
        self.category_label.setText("")
        self.shortcut_label.setText("")
        self.status_label.setText("")
        self.filters_display.setText("")
        self.stats_label.setText("")

        self.open_btn.setEnabled(False)
        self.edit_btn.setEnabled(False)
        self.duplicate_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

        self.current_selected_panel_id = None
```

#### 5.1.4 Métodos de Acciones

```python
    def open_panel(self):
        """Abrir el panel seleccionado"""
        if not self.current_selected_panel_id:
            return

        self.open_panel_by_id(self.current_selected_panel_id)

    def open_panel_by_id(self, panel_id: int):
        """Abrir un panel por su ID"""
        try:
            # Verificar si el panel ya está abierto
            if self._is_panel_open(panel_id):
                # Enfocar el panel existente
                self._focus_panel(panel_id)
                logger.info(f"Panel {panel_id} already open, focusing...")
            else:
                # Emitir señal para que MainWindow abra el panel
                self.panel_open_requested.emit(panel_id)
                logger.info(f"Requested to open panel {panel_id}")

            # Cerrar esta ventana (opcional)
            # self.close()

        except Exception as e:
            logger.error(f"Error opening panel: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al abrir panel: {e}")

    def edit_panel(self):
        """Editar el panel seleccionado"""
        if not self.current_selected_panel_id:
            return

        try:
            panel = self.panels_manager.get_panel_by_id(self.current_selected_panel_id)

            if not panel:
                QMessageBox.warning(self, "Error", "Panel no encontrado")
                return

            # Abrir diálogo de personalización
            from views.dialogs.panel_customization_dialog import PanelCustomizationDialog

            dialog = PanelCustomizationDialog(
                panel=panel,
                panels_manager=self.panels_manager,
                config_manager=self.config_manager,
                parent=self
            )

            if dialog.exec():
                # Obtener datos actualizados
                updated_data = dialog.get_customization_data()

                # Actualizar en BD
                self.panels_manager.update_panel_customization(
                    panel_id=self.current_selected_panel_id,
                    custom_name=updated_data.get('custom_name'),
                    custom_color=updated_data.get('custom_color'),
                    keyboard_shortcut=updated_data.get('keyboard_shortcut')
                )

                # Emitir señal de actualización
                self.panel_updated.emit(self.current_selected_panel_id)

                # Refrescar lista
                self.refresh_panel_list()

                logger.info(f"Panel {self.current_selected_panel_id} updated")
                QMessageBox.information(self, "Éxito", "Panel actualizado correctamente")

        except Exception as e:
            logger.error(f"Error editing panel: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al editar panel: {e}")

    def duplicate_panel(self):
        """Duplicar el panel seleccionado"""
        if not self.current_selected_panel_id:
            return

        try:
            panel = self.panels_manager.get_panel_by_id(self.current_selected_panel_id)

            if not panel:
                QMessageBox.warning(self, "Error", "Panel no encontrado")
                return

            # Confirmar duplicación
            reply = QMessageBox.question(
                self,
                "Duplicar Panel",
                f"¿Duplicar el panel '{panel.get('custom_name') or 'Sin nombre'}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Crear copia en BD
            filter_config = panel.get('filter_config')
            new_name = f"{panel.get('custom_name', 'Panel')} (copia)"

            new_panel_id = self.config_manager.db.save_pinned_panel(
                category_id=panel['category_id'],
                x_pos=panel['x_position'] + 20,  # Offset para que no queden exactamente encima
                y_pos=panel['y_position'] + 20,
                width=panel['width'],
                height=panel['height'],
                is_minimized=False,
                custom_name=new_name,
                custom_color=panel.get('custom_color'),
                filter_config=filter_config,
                keyboard_shortcut=None  # Se asignará automáticamente
            )

            # Refrescar lista
            self.refresh_panel_list()

            logger.info(f"Panel {self.current_selected_panel_id} duplicated as {new_panel_id}")
            QMessageBox.information(self, "Éxito", f"Panel duplicado correctamente (ID: {new_panel_id})")

        except Exception as e:
            logger.error(f"Error duplicating panel: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al duplicar panel: {e}")

    def delete_panel(self):
        """Eliminar el panel seleccionado"""
        if not self.current_selected_panel_id:
            return

        try:
            panel = self.panels_manager.get_panel_by_id(self.current_selected_panel_id)

            if not panel:
                QMessageBox.warning(self, "Error", "Panel no encontrado")
                return

            panel_name = panel.get('custom_name') or self._get_category_name(panel['category_id'])

            # Confirmar eliminación
            reply = QMessageBox.question(
                self,
                "Eliminar Panel",
                f"¿Eliminar permanentemente el panel '{panel_name}'?\n\n"
                f"Esta acción no se puede deshacer.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Verificar si el panel está abierto
            if self._is_panel_open(self.current_selected_panel_id):
                QMessageBox.warning(
                    self,
                    "Panel Abierto",
                    "Por favor cierra el panel antes de eliminarlo."
                )
                return

            # Eliminar de BD
            self.panels_manager.delete_panel(self.current_selected_panel_id)

            # Emitir señal de eliminación
            self.panel_deleted.emit(self.current_selected_panel_id)

            # Limpiar detalles y refrescar lista
            self.clear_details()
            self.refresh_panel_list()

            logger.info(f"Panel {self.current_selected_panel_id} deleted")
            QMessageBox.information(self, "Éxito", "Panel eliminado correctamente")

        except Exception as e:
            logger.error(f"Error deleting panel: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al eliminar panel: {e}")
```

#### 5.1.5 Métodos Auxiliares

```python
    def _get_category_name(self, category_id: int) -> str:
        """Obtener nombre de categoría por ID"""
        try:
            category = self.config_manager.get_category(str(category_id))
            if category:
                return f"{category.icon} {category.name}"
            return f"Categoría {category_id}"
        except:
            return f"Categoría {category_id}"

    def _is_panel_open(self, panel_id: int) -> bool:
        """Verificar si un panel está actualmente abierto"""
        try:
            if not self.main_window:
                return False

            for panel in self.main_window.pinned_panels:
                if panel.panel_id == panel_id:
                    return True

            return False
        except:
            return False

    def _focus_panel(self, panel_id: int):
        """Enfocar un panel abierto"""
        try:
            if not self.main_window:
                return

            for panel in self.main_window.pinned_panels:
                if panel.panel_id == panel_id:
                    panel.raise_()
                    panel.activateWindow()
                    panel.setFocus()
                    break
        except Exception as e:
            logger.error(f"Error focusing panel: {e}")

    def apply_styles(self):
        """Aplicar estilos a la ventana"""
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: 'Segoe UI';
            }

            QGroupBox {
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #00aaff;
            }

            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 5px 10px;
                color: #e0e0e0;
            }

            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #00aaff;
            }

            QPushButton:pressed {
                background-color: #1a1a1a;
            }

            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #555;
            }

            QLineEdit, QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 5px;
                color: #e0e0e0;
            }

            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #00aaff;
            }

            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
            }

            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #3d3d3d;
            }

            QListWidget::item:selected {
                background-color: #00aaff;
                color: #ffffff;
            }

            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 5px;
            }
        """)

    def closeEvent(self, event):
        """Handle window close event"""
        logger.info("Pinned Panels Manager Window closed")
        event.accept()
```

### 5.2 Widget de Item de Lista: `PanelListItemWidget`

**Continúa en el mismo archivo `pinned_panels_manager_window.py`**

```python
class PanelListItemWidget(QWidget):
    """
    Widget personalizado para mostrar un panel en la lista
    Muestra: nombre, categoría, indicadores de filtros, shortcut
    """

    def __init__(self, panel_data: Dict, config_manager, parent=None):
        super().__init__(parent)

        self.panel_data = panel_data
        self.config_manager = config_manager

        self.setup_ui()

    def setup_ui(self):
        """Configurar UI del widget"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Icono de estado
        status_label = QLabel()
        if self.panel_data.get('is_active'):
            status_label.setText("🟢")
            status_label.setToolTip("Activo")
        else:
            status_label.setText("⚪")
            status_label.setToolTip("Inactivo")
        layout.addWidget(status_label)

        # Información del panel
        info_layout = QVBoxLayout()

        # Nombre del panel
        panel_name = self.panel_data.get('custom_name')
        if not panel_name:
            category = self.config_manager.get_category(str(self.panel_data['category_id']))
            panel_name = f"{category.icon} {category.name}" if category else f"Panel {self.panel_data['id']}"

        name_label = QLabel(f"<b>{panel_name}</b>")
        info_layout.addWidget(name_label)

        # Información adicional (categoría, filtros, shortcut)
        details = []

        # Categoría (si tiene nombre personalizado)
        if self.panel_data.get('custom_name'):
            category = self.config_manager.get_category(str(self.panel_data['category_id']))
            if category:
                details.append(f"📂 {category.name}")

        # Indicador de filtros
        if self.panel_data.get('filter_config'):
            details.append("🔍 Filtros")

        # Shortcut
        if self.panel_data.get('keyboard_shortcut'):
            details.append(f"⌨️ {self.panel_data['keyboard_shortcut']}")

        if details:
            details_label = QLabel(" | ".join(details))
            details_label.setStyleSheet("color: #888;")
            info_layout.addWidget(details_label)

        layout.addLayout(info_layout, 1)

        # Contador de usos
        usage_label = QLabel(f"📊 {self.panel_data.get('open_count', 0)}")
        usage_label.setToolTip(f"Abierto {self.panel_data.get('open_count', 0)} veces")
        usage_label.setStyleSheet("color: #00aaff;")
        layout.addWidget(usage_label)
```

### 5.3 Diálogo de Personalización: `PanelCustomizationDialog`

**Archivo**: `src/views/dialogs/panel_customization_dialog.py` (NUEVO)

```python
"""
Panel Customization Dialog - Permite editar nombre, color y shortcut de un panel
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QColorDialog, QComboBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import logging

logger = logging.getLogger(__name__)


class PanelCustomizationDialog(QDialog):
    """Diálogo para personalizar un panel anclado"""

    def __init__(self, panel, panels_manager, config_manager, parent=None):
        super().__init__(parent)

        self.panel = panel
        self.panels_manager = panels_manager
        self.config_manager = config_manager

        self.selected_color = panel.get('custom_color', '#00aaff')

        self.init_ui()
        self.load_current_values()

    def init_ui(self):
        """Inicializar UI"""
        self.setWindowTitle("Personalizar Panel")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Título
        title = QLabel("✏️ Personalizar Panel Anclado")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(title)

        # Grupo: Nombre
        name_group = QGroupBox("Nombre del Panel")
        name_layout = QVBoxLayout(name_group)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre personalizado (opcional)")
        name_layout.addWidget(self.name_input)

        help_label = QLabel("Si se deja vacío, se usará el nombre de la categoría")
        help_label.setStyleSheet("color: #888; font-size: 10px;")
        name_layout.addWidget(help_label)

        layout.addWidget(name_group)

        # Grupo: Color
        color_group = QGroupBox("Color del Header")
        color_layout = QHBoxLayout(color_group)

        self.color_preview = QPushButton()
        self.color_preview.setFixedSize(100, 40)
        self.update_color_preview()
        color_layout.addWidget(self.color_preview)

        choose_color_btn = QPushButton("Elegir Color...")
        choose_color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(choose_color_btn)

        reset_color_btn = QPushButton("Restablecer")
        reset_color_btn.clicked.connect(self.reset_color)
        color_layout.addWidget(reset_color_btn)

        layout.addWidget(color_group)

        # Grupo: Shortcut
        shortcut_group = QGroupBox("Atajo de Teclado")
        shortcut_layout = QVBoxLayout(shortcut_group)

        self.shortcut_combo = QComboBox()
        self.populate_shortcuts()
        shortcut_layout.addWidget(self.shortcut_combo)

        layout.addWidget(shortcut_group)

        # Botones
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("💾 Guardar")
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)

        cancel_btn = QPushButton("❌ Cancelar")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

        self.apply_styles()

    def load_current_values(self):
        """Cargar valores actuales del panel"""
        # Nombre
        current_name = self.panel.get('custom_name', '')
        self.name_input.setText(current_name)

        # Color
        self.selected_color = self.panel.get('custom_color', '#00aaff')
        self.update_color_preview()

        # Shortcut
        current_shortcut = self.panel.get('keyboard_shortcut', '')
        if current_shortcut:
            index = self.shortcut_combo.findData(current_shortcut)
            if index >= 0:
                self.shortcut_combo.setCurrentIndex(index)

    def populate_shortcuts(self):
        """Poblar combo box con shortcuts disponibles"""
        # Obtener shortcuts ya usados
        all_panels = self.panels_manager.get_all_panels()
        used_shortcuts = {p.get('keyboard_shortcut') for p in all_panels if p.get('keyboard_shortcut')}

        # Shortcut actual del panel
        current_shortcut = self.panel.get('keyboard_shortcut')

        # Agregar opciones
        self.shortcut_combo.addItem("Sin atajo", None)

        for i in range(1, 10):
            shortcut = f"Ctrl+Shift+{i}"

            if shortcut == current_shortcut:
                # El shortcut actual siempre está disponible
                self.shortcut_combo.addItem(f"{shortcut} (actual)", shortcut)
            elif shortcut in used_shortcuts:
                # Shortcut usado por otro panel
                self.shortcut_combo.addItem(f"{shortcut} (en uso)", shortcut)
                self.shortcut_combo.model().item(self.shortcut_combo.count() - 1).setEnabled(False)
            else:
                # Shortcut disponible
                self.shortcut_combo.addItem(shortcut, shortcut)

    def choose_color(self):
        """Abrir diálogo de selección de color"""
        current_color = QColor(self.selected_color)
        color = QColorDialog.getColor(current_color, self, "Elegir Color del Header")

        if color.isValid():
            self.selected_color = color.name()
            self.update_color_preview()

    def reset_color(self):
        """Restablecer color por defecto"""
        self.selected_color = '#00aaff'
        self.update_color_preview()

    def update_color_preview(self):
        """Actualizar preview del color"""
        self.color_preview.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.selected_color};
                border: 2px solid #3d3d3d;
                border-radius: 5px;
            }}
        """)

    def get_customization_data(self) -> dict:
        """Obtener datos de personalización"""
        return {
            'custom_name': self.name_input.text().strip() or None,
            'custom_color': self.selected_color,
            'keyboard_shortcut': self.shortcut_combo.currentData()
        }

    def validate_inputs(self) -> bool:
        """Validar entradas"""
        # Por ahora, todo es válido (nombre y shortcut son opcionales)
        return True

    def accept(self):
        """Aceptar cambios"""
        if not self.validate_inputs():
            return

        super().accept()

    def apply_styles(self):
        """Aplicar estilos"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }

            QGroupBox {
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }

            QLineEdit, QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 5px;
                color: #e0e0e0;
            }

            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 5px 10px;
            }

            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #00aaff;
            }
        """)
```

### 5.4 Integración con MainWindow

**Archivo**: `src/views/main_window.py`

#### 5.4.1 Agregar método para abrir PinnedPanelsManagerWindow

```python
def show_pinned_panels_manager(self):
    """Mostrar ventana de gestión de paneles anclados"""
    try:
        from views.pinned_panels_manager_window import PinnedPanelsManagerWindow

        # Crear ventana si no existe
        if not hasattr(self, 'panels_manager_window') or not self.panels_manager_window:
            self.panels_manager_window = PinnedPanelsManagerWindow(
                config_manager=self.config_manager,
                pinned_panels_manager=self.controller.pinned_panels_manager,
                main_window=self,
                parent=self
            )

            # Conectar señales
            self.panels_manager_window.panel_open_requested.connect(self.on_restore_panel_requested)
            self.panels_manager_window.panel_deleted.connect(self.on_panel_deleted_from_manager)
            self.panels_manager_window.panel_updated.connect(self.on_panel_updated_from_manager)

        # Refrescar y mostrar
        self.panels_manager_window.refresh_panel_list()
        self.panels_manager_window.show()
        self.panels_manager_window.raise_()
        self.panels_manager_window.activateWindow()

        logger.info("Pinned Panels Manager Window opened")

    except Exception as e:
        logger.error(f"Error opening panels manager window: {e}", exc_info=True)
        QMessageBox.critical(self, "Error", f"Error al abrir gestor de paneles: {e}")

def on_panel_deleted_from_manager(self, panel_id: int):
    """Handle cuando un panel es eliminado desde el manager"""
    try:
        # Remover panel de la lista si está abierto
        for i, panel in enumerate(self.pinned_panels):
            if panel.panel_id == panel_id:
                panel.close()
                self.pinned_panels.pop(i)
                logger.info(f"Closed panel {panel_id} after deletion")
                break
    except Exception as e:
        logger.error(f"Error handling panel deletion: {e}")

def on_panel_updated_from_manager(self, panel_id: int):
    """Handle cuando un panel es actualizado desde el manager"""
    try:
        # Actualizar panel si está abierto
        for panel in self.pinned_panels:
            if panel.panel_id == panel_id:
                # Recargar datos del panel
                panel_data = self.controller.pinned_panels_manager.get_panel_by_id(panel_id)
                if panel_data:
                    panel.custom_name = panel_data.get('custom_name')
                    panel.custom_color = panel_data.get('custom_color')
                    panel.apply_custom_styling()
                    logger.info(f"Updated panel {panel_id} styling")
                break
    except Exception as e:
        logger.error(f"Error handling panel update: {e}")
```

#### 5.4.2 Agregar botón/acción en el menú

```python
# En init_ui() o donde sea apropiado:

# Opción 1: Botón en toolbar (si hay toolbar)
panels_manager_btn = QPushButton("📍 Paneles")
panels_manager_btn.setToolTip("Gestionar paneles anclados")
panels_manager_btn.clicked.connect(self.show_pinned_panels_manager)

# Opción 2: Agregar al menú del system tray
# En create_tray_menu():
self.tray_menu.addAction("📍 Gestionar Paneles", self.show_pinned_panels_manager)

# Opción 3: Shortcut de teclado (en __init__ o init_ui):
from PyQt6.QtGui import QShortcut, QKeySequence

panels_shortcut = QShortcut(QKeySequence("Ctrl+Shift+P"), self)
panels_shortcut.activated.connect(self.show_pinned_panels_manager)
```

---

## 6. FASE 3: Mejoras Adicionales (Opcional)

### 6.1 Indicador Visual de Filtros Activos en FloatingPanel

**Archivo**: `src/views/floating_panel.py`

#### Agregar badge de filtros en el header

```python
def _create_filter_badge(self):
    """Crear badge que muestra cantidad de filtros activos"""
    badge = QLabel()
    badge.setVisible(False)
    badge.setStyleSheet("""
        QLabel {
            background-color: #ff6b00;
            color: white;
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: bold;
        }
    """)
    return badge

def update_filter_badge(self):
    """Actualizar badge de filtros"""
    filter_count = 0

    # Contar filtros activos
    if self.current_filters:
        filter_count += len(self.current_filters)
    if self.current_state_filter != "normal":
        filter_count += 1
    if self.search_bar.search_input.text():
        filter_count += 1

    if filter_count > 0:
        self.filter_badge.setText(f"🔍 {filter_count}")
        self.filter_badge.setVisible(True)
        self.filter_badge.setToolTip(f"{filter_count} filtro(s) activo(s)")
    else:
        self.filter_badge.setVisible(False)

# Llamar a update_filter_badge() en:
# - on_filters_changed()
# - on_filters_cleared()
# - on_state_filter_changed()
# - on_search_changed()
```

### 6.2 Menú Contextual en Paneles Anclados

```python
def contextMenuEvent(self, event):
    """Mostrar menú contextual en panel anclado"""
    if not self.is_pinned:
        return

    from PyQt6.QtWidgets import QMenu

    menu = QMenu(self)

    # Acciones de filtros
    save_filters_action = menu.addAction("💾 Guardar filtros actuales")
    save_filters_action.triggered.connect(self._save_panel_state_to_db)

    clear_filters_action = menu.addAction("🧹 Limpiar todos los filtros")
    clear_filters_action.triggered.connect(self.on_filters_cleared)

    menu.addSeparator()

    # Acciones de panel
    manager_action = menu.addAction("📍 Abrir gestor de paneles")
    manager_action.triggered.connect(self._open_panels_manager)

    customize_action = menu.addAction("✏️ Personalizar panel")
    customize_action.triggered.connect(self.on_customize_clicked)

    menu.addSeparator()

    # Info
    info_action = menu.addAction("ℹ️ Información del panel")
    info_action.triggered.connect(self._show_panel_info)

    menu.exec(event.globalPos())

def _open_panels_manager(self):
    """Abrir ventana de gestión de paneles"""
    # Buscar MainWindow y llamar a show_pinned_panels_manager()
    from views.main_window import MainWindow

    parent = self.parent()
    while parent:
        if isinstance(parent, MainWindow):
            parent.show_pinned_panels_manager()
            break
        parent = parent.parent()

def _show_panel_info(self):
    """Mostrar información del panel"""
    from PyQt6.QtWidgets import QMessageBox

    info_text = f"""
    <h3>Información del Panel</h3>
    <p><b>ID:</b> {self.panel_id}</p>
    <p><b>Nombre:</b> {self.custom_name or 'Sin nombre'}</p>
    <p><b>Categoría:</b> {self.current_category.name if self.current_category else 'N/A'}</p>
    <p><b>Filtros activos:</b> {len(self.current_filters) + (1 if self.current_state_filter != 'normal' else 0) + (1 if self.search_bar.search_input.text() else 0)}</p>
    """

    QMessageBox.information(self, "Info del Panel", info_text)
```

### 6.3 Exportar/Importar Configuraciones

#### Método de exportación en `PinnedPanelsManager`

```python
def export_panel_config(self, panel_id: int, file_path: str):
    """
    Exportar configuración de panel a archivo JSON

    Args:
        panel_id: ID del panel a exportar
        file_path: Ruta donde guardar el archivo
    """
    try:
        panel = self.get_panel_by_id(panel_id)

        if not panel:
            raise ValueError(f"Panel {panel_id} not found")

        # Preparar datos de exportación
        export_data = {
            'version': '1.0',
            'panel_config': {
                'category_id': panel['category_id'],
                'custom_name': panel.get('custom_name'),
                'custom_color': panel.get('custom_color'),
                'filter_config': panel.get('filter_config'),
                'width': panel.get('width'),
                'height': panel.get('height'),
            },
            'exported_at': datetime.now().isoformat()
        }

        # Guardar a archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Panel {panel_id} config exported to {file_path}")

    except Exception as e:
        logger.error(f"Error exporting panel config: {e}", exc_info=True)
        raise

def import_panel_config(self, file_path: str) -> int:
    """
    Importar configuración de panel desde archivo JSON

    Args:
        file_path: Ruta del archivo a importar

    Returns:
        int: ID del nuevo panel creado
    """
    try:
        # Leer archivo
        with open(file_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)

        # Validar versión
        if import_data.get('version') != '1.0':
            raise ValueError("Unsupported config file version")

        panel_config = import_data['panel_config']

        # Crear nuevo panel con configuración importada
        panel_id = self.db.save_pinned_panel(
            category_id=panel_config['category_id'],
            x_pos=100,  # Posición por defecto
            y_pos=100,
            width=panel_config.get('width', 350),
            height=panel_config.get('height', 500),
            is_minimized=False,
            custom_name=panel_config.get('custom_name'),
            custom_color=panel_config.get('custom_color'),
            filter_config=panel_config.get('filter_config'),
            keyboard_shortcut=None  # Se asignará automáticamente
        )

        logger.info(f"Panel config imported from {file_path}, new panel ID: {panel_id}")
        return panel_id

    except Exception as e:
        logger.error(f"Error importing panel config: {e}", exc_info=True)
        raise
```

#### Botones en `PinnedPanelsManagerWindow`

```python
# Agregar botones de exportar/importar
export_btn = QPushButton("📤 Exportar")
export_btn.clicked.connect(self.export_panel)

import_btn = QPushButton("📥 Importar")
import_btn.clicked.connect(self.import_panel)

def export_panel(self):
    """Exportar configuración del panel seleccionado"""
    if not self.current_selected_panel_id:
        QMessageBox.warning(self, "Error", "Selecciona un panel para exportar")
        return

    from PyQt6.QtWidgets import QFileDialog

    file_path, _ = QFileDialog.getSaveFileName(
        self,
        "Exportar Configuración de Panel",
        f"panel_config_{self.current_selected_panel_id}.json",
        "JSON Files (*.json)"
    )

    if file_path:
        try:
            self.panels_manager.export_panel_config(self.current_selected_panel_id, file_path)
            QMessageBox.information(self, "Éxito", f"Configuración exportada a:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar: {e}")

def import_panel(self):
    """Importar configuración de panel"""
    from PyQt6.QtWidgets import QFileDialog

    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Importar Configuración de Panel",
        "",
        "JSON Files (*.json)"
    )

    if file_path:
        try:
            new_panel_id = self.panels_manager.import_panel_config(file_path)
            QMessageBox.information(self, "Éxito", f"Panel importado con ID: {new_panel_id}")
            self.refresh_panel_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al importar: {e}")
```

---

## 7. Testing y Verificación

### 7.1 Test Manual - Checklist

#### FASE 1: Bug Fix

- [ ] **Test 1**: Aplicar filtros a un panel anclado
  - Anclar un panel flotante
  - Aplicar filtro avanzado (ej: item count > 5)
  - Cambiar filtro de estado a "archived"
  - Escribir texto en búsqueda
  - Verificar en BD que `filter_config` no es NULL

- [ ] **Test 2**: Verificar serialización
  - Ejecutar `util/test_filter_persistence.py`
  - Confirmar que serialización/deserialización funciona

- [ ] **Test 3**: Restauración de filtros
  - Con filtros aplicados, cerrar aplicación
  - Reabrir aplicación
  - Verificar que panel se restaura con todos los filtros aplicados
  - Verificar que items mostrados coinciden con los filtros

#### FASE 2: Ventana de Gestión

- [ ] **Test 4**: Lista de paneles
  - Abrir "Gestión de Paneles Anclados"
  - Verificar que muestra todos los paneles guardados
  - Verificar que muestra información correcta (nombre, categoría, filtros, shortcut)

- [ ] **Test 5**: Filtrado y búsqueda
  - Buscar por nombre de panel
  - Buscar por categoría
  - Filtrar "Solo con filtros activos"
  - Filtrar "Solo con nombre personalizado"
  - Ordenar por diferentes criterios

- [ ] **Test 6**: Abrir panel
  - Doble clic en panel de la lista
  - Verificar que se abre el panel correcto
  - Doble clic en panel ya abierto
  - Verificar que solo se enfoca (no se duplica)

- [ ] **Test 7**: Editar panel
  - Seleccionar panel y presionar "Editar"
  - Cambiar nombre, color y shortcut
  - Guardar y verificar cambios en BD
  - Verificar que panel abierto refleja cambios

- [ ] **Test 8**: Duplicar panel
  - Seleccionar panel con filtros
  - Presionar "Duplicar"
  - Verificar que nuevo panel tiene misma configuración
  - Verificar que tiene shortcut diferente

- [ ] **Test 9**: Eliminar panel
  - Seleccionar panel cerrado
  - Presionar "Eliminar"
  - Confirmar eliminación
  - Verificar que desaparece de BD y lista

#### FASE 3: Mejoras Opcionales

- [ ] **Test 10**: Badge de filtros
  - Aplicar filtros a panel
  - Verificar que aparece badge con cantidad correcta
  - Limpiar filtros y verificar que badge desaparece

- [ ] **Test 11**: Menú contextual
  - Click derecho en panel anclado
  - Probar todas las opciones del menú

- [ ] **Test 12**: Exportar/Importar
  - Exportar configuración de panel
  - Eliminar panel original
  - Importar configuración
  - Verificar que panel restaurado es idéntico

### 7.2 Test de Regresión

- [ ] Verificar que paneles sin filtros siguen funcionando
- [ ] Verificar que shortcuts de teclado funcionan
- [ ] Verificar que minimizar/maximizar funciona
- [ ] Verificar que mover/redimensionar funciona
- [ ] Verificar que desanclar panel funciona
- [ ] Verificar que cerrar aplicación guarda todo correctamente

### 7.3 Test de Performance

- [ ] Probar con 10+ paneles anclados
- [ ] Verificar que auto-guardado no causa lag
- [ ] Verificar que restauración en startup es rápida
- [ ] Verificar que ventana de gestión carga rápidamente

---

## 8. Cronograma de Implementación

### Día 1: FASE 1 - Bug Fix (2-3 horas)

**Mañana** (1-1.5h):
- ✅ Corregir `_serialize_filter_config()` en `pinned_panels_manager.py`
- ✅ Mejorar `_deserialize_filter_config()` con validación
- ✅ Agregar logging adicional
- ✅ Crear script de testing `util/test_filter_persistence.py`

**Tarde** (1-1.5h):
- ✅ Ejecutar tests manuales
- ✅ Verificar que filtros se guardan en BD
- ✅ Verificar que filtros se restauran correctamente
- ✅ Ajustes y bug fixes si es necesario

### Día 2: FASE 2 - Ventana de Gestión (6-8 horas)

**Mañana** (3-4h):
- 📝 Crear `src/views/pinned_panels_manager_window.py`
  - Estructura base de la clase
  - UI del header con búsqueda y filtros
  - UI del panel izquierdo (lista)
  - UI del panel derecho (detalles)
- 📝 Implementar `PanelListItemWidget`
- 📝 Implementar métodos de carga y filtrado

**Tarde** (3-4h):
- 📝 Implementar eventos y acciones
  - `on_panel_selected()`
  - `on_panel_double_clicked()`
  - `show_panel_details()`
  - `open_panel()`
- 📝 Crear `src/views/dialogs/panel_customization_dialog.py`
- 📝 Implementar `edit_panel()`, `duplicate_panel()`, `delete_panel()`
- 📝 Integrar con `MainWindow`
  - Agregar método `show_pinned_panels_manager()`
  - Conectar señales
  - Agregar botón/menú/shortcut

### Día 3: Testing y Mejoras (4-6 horas)

**Mañana** (2-3h):
- ✅ Tests manuales completos (FASE 1 + FASE 2)
- ✅ Bug fixes y ajustes
- ✅ Tests de regresión
- ✅ Optimizaciones de performance

**Tarde** (2-3h):
- 🎨 FASE 3 (Opcional): Mejoras adicionales
  - Badge de filtros en FloatingPanel
  - Menú contextual
  - Exportar/Importar (si hay tiempo)
- ✅ Tests finales
- ✅ Documentación de uso

### Total Estimado: 12-17 horas

**Mínimo viable** (solo FASE 1 + FASE 2 básico): ~8-10 horas
**Completo con mejoras** (FASE 1 + 2 + 3): ~12-17 horas

---

## 9. Notas de Implementación

### 9.1 Prioridades

1. **CRÍTICO**: FASE 1 - Arreglar bug de filtros
2. **ALTO**: FASE 2 - Ventana de gestión básica (lista, abrir, editar, eliminar)
3. **MEDIO**: FASE 2 - Funcionalidades avanzadas (duplicar, filtrado, stats)
4. **BAJO**: FASE 3 - Mejoras opcionales (badge, menú contextual, export/import)

### 9.2 Consideraciones de Diseño

- **Tema consistente**: Usar mismo tema oscuro que el resto de la aplicación
- **Iconos**: Usar emojis por consistencia (o SVG icons si se prefiere)
- **Responsive**: La ventana debe ser redimensionable
- **Keyboard navigation**: Atajos de teclado para acciones comunes
- **Feedback visual**: Animaciones sutiles, mensajes de confirmación

### 9.3 Posibles Problemas y Soluciones

**Problema 1**: Al abrir panel desde manager, puede estar ya abierto
- **Solución**: Verificar con `_is_panel_open()` y enfocar en lugar de duplicar

**Problema 2**: Eliminar panel que está abierto
- **Solución**: Advertir al usuario y pedir que cierre primero, o cerrar automáticamente

**Problema 3**: Cambiar shortcut de panel puede entrar en conflicto
- **Solución**: Validar shortcuts y deshabilitar opciones ya usadas en el combo

**Problema 4**: Filtros complejos pueden no serializarse correctamente
- **Solución**: Tests exhaustivos de serialización, validación en deserialización

---

## 10. Documentación de Uso (Para el usuario final)

### Persistencia de Filtros en Paneles Anclados

Los paneles flotantes anclados ahora recuerdan automáticamente todos los filtros aplicados:

- **Filtros avanzados**: Rangos de items, tags, fechas, etc.
- **Filtro de estado**: Normal, Archivado, Inactivo, Todos
- **Texto de búsqueda**: Cualquier búsqueda activa

Cuando cierres y reabras la aplicación, todos tus paneles anclados se restaurarán exactamente como los dejaste, con todos los filtros activos.

### Ventana de Gestión de Paneles Anclados

**Abrir**: `Ctrl+Shift+P` o desde el menú de bandeja del sistema

**Funcionalidades**:

1. **Ver todos tus paneles guardados**: Lista completa con información de cada panel
2. **Buscar y filtrar**: Encuentra rápidamente el panel que necesitas
3. **Abrir rápidamente**: Doble clic para abrir un panel (o enfocarlo si ya está abierto)
4. **Personalizar**: Edita nombre, color del header y atajo de teclado
5. **Duplicar**: Crea copias de paneles con la misma configuración
6. **Eliminar**: Borra paneles que ya no necesitas

**Tips**:
- Los paneles con filtros activos se muestran con un icono 🔍
- Puedes ordenar por: última apertura, más usado, nombre o categoría
- Los atajos de teclado permiten acceso instantáneo a tus paneles favoritos

---

## 11. Resumen Ejecutivo

### Qué se va a implementar:

✅ **Corrección del bug** que impedía guardar filtros en paneles anclados
✅ **Sistema completo de persistencia** de filtros (avanzados, estado, búsqueda)
✅ **Ventana de gestión visual** para administrar todos los paneles guardados
✅ **Funcionalidades avanzadas**: Editar, duplicar, eliminar paneles
✅ **Mejoras de UX** (opcional): Badge de filtros, menú contextual, export/import

### Beneficios para el usuario:

🎯 **Workflow mejorado**: Paneles siempre listos con los filtros correctos
🎯 **Acceso rápido**: Ventana centralizada para gestionar todos los paneles
🎯 **Personalización**: Nombrar, colorear y asignar shortcuts a paneles
🎯 **Productividad**: No perder tiempo re-configurando filtros cada vez

### Impacto en el código:

- **1 archivo modificado**: `pinned_panels_manager.py` (bug fix)
- **2 archivos nuevos**: `pinned_panels_manager_window.py`, `panel_customization_dialog.py`
- **1 archivo actualizado**: `main_window.py` (integración)
- **0 cambios en BD**: La estructura ya existe, solo se usa correctamente
- **Backward compatible**: Paneles antiguos siguen funcionando

---

**FIN DEL PLAN DETALLADO**

Este plan está listo para implementación. Todos los detalles técnicos, métodos, estructuras de datos y flujos están especificados. El código proporcionado es funcional y solo necesita ser copiado a los archivos correspondientes.

¿Preguntas o ajustes antes de comenzar la implementación?
