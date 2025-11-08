# Plan de Implementación: Sistema Avanzado de Gestión de Archivos (TYPE PATH)

## Descripción General

Implementación de un sistema avanzado para items de tipo PATH que permite:
- Configurar una ruta base para almacenamiento de archivos
- Organización automática por carpetas según tipo de archivo
- Almacenamiento de metadatos básicos
- Detección de duplicados
- Interface intuitiva para subir y gestionar archivos

---

## Fase 1: Diseño y Preparación de Base de Datos

### 1.1 Migración de Base de Datos
**Objetivo:** Extender tabla `items` con campos para metadatos de archivos

**Archivos a crear/modificar:**
- `src/database/migrations.py` (agregar nueva migración)
- Script temporal: `util/migrations/migrate_add_file_metadata.py`

**Campos a agregar:**
```sql
ALTER TABLE items ADD COLUMN file_size INTEGER DEFAULT NULL;
ALTER TABLE items ADD COLUMN file_type VARCHAR(50) DEFAULT NULL;
ALTER TABLE items ADD COLUMN file_extension VARCHAR(10) DEFAULT NULL;
ALTER TABLE items ADD COLUMN original_filename VARCHAR(255) DEFAULT NULL;
ALTER TABLE items ADD COLUMN file_hash VARCHAR(64) DEFAULT NULL;
```

**Descripción de campos:**
- `file_size`: Tamaño del archivo en bytes (para mostrar "2.5 MB")
- `file_type`: Categoría del archivo (IMAGEN, VIDEO, PDF, WORD, EXCEL, TEXT, OTROS)
- `file_extension`: Extensión con punto (.jpg, .mp4, .pdf)
- `original_filename`: Nombre original del archivo (por si se renombra)
- `file_hash`: Hash SHA256 para detección de duplicados

**Tareas:**
- [ ] Crear script de migración
- [ ] Ejecutar y verificar migración
- [ ] Actualizar schema en documentación
- [ ] Crear backup de BD antes de migración

---

## Fase 2: Configuración de Rutas Base

### 2.1 Actualizar Tabla Settings
**Objetivo:** Almacenar configuración de rutas y carpetas

**Campos en settings:**
```python
files_base_path: str          # Ej: "D:\ARCHIVOS_GENERAL"
files_folders_config: str     # JSON con mapping de carpetas
files_auto_create_folders: bool  # Crear carpetas automáticamente
```

**Estructura del JSON `files_folders_config`:**
```json
{
  "VIDEOS": "VIDEOS",
  "IMAGENES": "IMAGENES",
  "PDFS": "PDFS",
  "WORDS": "WORDS",
  "EXCELS": "EXCELS",
  "TEXT": "TEXT",
  "OTROS": "OTROS"
}
```

**Tareas:**
- [ ] Agregar campos a tabla settings vía migración
- [ ] Definir valores por defecto
- [ ] Actualizar `ConfigManager` para leer/escribir estos valores

---

## Fase 3: Capa de Negocio - File Manager

### 3.1 Crear FileManager
**Archivo:** `src/core/file_manager.py`

**Responsabilidades:**
1. Gestionar copia de archivos a carpetas organizadas
2. Extraer metadatos básicos
3. Calcular hash SHA256
4. Detectar duplicados
5. Validar existencia de archivos

**Métodos principales:**
```python
class FileManager:
    def __init__(self, config_manager)

    # Configuración
    def get_base_path() -> str
    def set_base_path(path: str) -> bool
    def get_folders_config() -> dict
    def update_folders_config(config: dict)

    # Detección automática
    def detect_file_type(extension: str) -> str
    def get_target_folder(extension: str) -> str

    # Gestión de archivos
    def copy_file_to_storage(source_path: str) -> dict
        # Retorna: {
        #   'full_path': 'D:\ARCHIVOS\IMAGENES\foto.jpg',
        #   'file_size': 1024000,
        #   'file_type': 'IMAGEN',
        #   'file_extension': '.jpg',
        #   'original_filename': 'foto.jpg',
        #   'file_hash': 'abc123...'
        # }

    def calculate_file_hash(file_path: str) -> str
    def check_duplicate(file_hash: str) -> Optional[Item]
    def validate_file_exists(file_path: str) -> bool
    def get_file_metadata(file_path: str) -> dict

    # Utilidades
    def format_file_size(size_bytes: int) -> str  # "2.5 MB"
    def ensure_folder_exists(folder_path: str) -> bool
    def get_file_icon_by_type(file_type: str) -> str  # Emoji
```

**Mapping de extensiones:**
```python
FOLDER_MAPPING = {
    'IMAGENES': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'],
    'VIDEOS': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
    'PDFS': ['.pdf'],
    'WORDS': ['.doc', '.docx', '.odt', '.rtf'],
    'EXCELS': ['.xls', '.xlsx', '.csv', '.ods'],
    'TEXT': ['.txt', '.md', '.log', '.json', '.xml', '.yaml', '.yml'],
    'OTROS': []  # Fallback
}

FILE_TYPE_ICONS = {
    'IMAGEN': '🖼️',
    'VIDEO': '🎬',
    'PDF': '📕',
    'WORD': '📘',
    'EXCEL': '📊',
    'TEXT': '📄',
    'OTROS': '📎'
}
```

**Tareas:**
- [ ] Crear clase FileManager
- [ ] Implementar detección de tipo por extensión
- [ ] Implementar copia de archivos con organización
- [ ] Implementar cálculo de hash SHA256
- [ ] Implementar detección de duplicados
- [ ] Crear tests unitarios

---

## Fase 4: Actualizar Modelo Item

### 4.1 Extender Modelo Item
**Archivo:** `src/models/item.py`

**Campos a agregar:**
```python
@dataclass
class Item:
    # ... campos existentes ...
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    file_extension: Optional[str] = None
    original_filename: Optional[str] = None
    file_hash: Optional[str] = None

    def get_formatted_file_size(self) -> str:
        """Retorna tamaño formateado: '2.5 MB'"""
        if not self.file_size:
            return ""
        # Implementar formato

    def get_file_type_icon(self) -> str:
        """Retorna emoji según tipo de archivo"""
        # Implementar
```

**Tareas:**
- [ ] Agregar campos al dataclass
- [ ] Agregar métodos helper
- [ ] Actualizar __init__ con valores por defecto

---

## Fase 5: Actualizar DBManager

### 5.1 Modificar Operaciones CRUD
**Archivo:** `src/database/db_manager.py`

**Métodos a actualizar:**

```python
def add_item(
    self,
    category_id: int,
    label: str,
    content: str,
    item_type: str = "TEXT",
    description: str = "",
    is_sensitive: bool = False,
    is_favorite: bool = False,
    # Nuevos parámetros
    file_size: Optional[int] = None,
    file_type: Optional[str] = None,
    file_extension: Optional[str] = None,
    original_filename: Optional[str] = None,
    file_hash: Optional[str] = None
) -> int

def update_item(
    self,
    item_id: int,
    label: Optional[str] = None,
    content: Optional[str] = None,
    description: Optional[str] = None,
    item_type: Optional[str] = None,
    is_sensitive: Optional[bool] = None,
    is_favorite: Optional[bool] = None,
    # Nuevos parámetros
    file_size: Optional[int] = None,
    file_type: Optional[str] = None,
    file_extension: Optional[str] = None,
    original_filename: Optional[str] = None,
    file_hash: Optional[str] = None
) -> bool

def get_items_by_category(self, category_id: int) -> List[Item]:
    # Actualizar SELECT para incluir nuevos campos

def get_item_by_hash(self, file_hash: str) -> Optional[Item]:
    # Nuevo método para detectar duplicados
```

**Tareas:**
- [ ] Actualizar queries SQL con nuevos campos
- [ ] Actualizar construcción de objetos Item
- [ ] Implementar método get_item_by_hash
- [ ] Actualizar todos los lugares que llaman add_item/update_item

---

## Fase 6: Interface de Configuración

### 6.1 Nueva Pestaña "Archivos" en SettingsWindow
**Archivo:** `src/views/settings_window.py`

**Layout de la pestaña:**
```
┌─ Gestión de Archivos ──────────────────────────┐
│                                                 │
│  Ruta Base de Almacenamiento                   │
│  ┌──────────────────────────────┐ [📁 Examinar]│
│  │ D:\ARCHIVOS_GENERAL          │              │
│  └──────────────────────────────┘              │
│                                                 │
│  □ Crear carpetas automáticamente si no existen│
│                                                 │
│  ─────────────────────────────────────────────  │
│                                                 │
│  Carpetas Predefinidas                         │
│  ┌────────────────────────────────────────┐   │
│  │  VIDEOS      → VIDEOS                  │   │
│  │  IMAGENES    → IMAGENES                │   │
│  │  PDFS        → PDFS                    │   │
│  │  WORDS       → WORDS                   │   │
│  │  EXCELS      → EXCELS                  │   │
│  │  TEXT        → TEXT                    │   │
│  │  OTROS       → OTROS                   │   │
│  └────────────────────────────────────────┘   │
│                                                 │
│  [➕ Agregar] [✏️ Editar] [🗑️ Eliminar]        │
│                                                 │
│  ─────────────────────────────────────────────  │
│                                                 │
│  Estado del Almacenamiento                     │
│  • Archivos almacenados: 247                   │
│  • Espacio utilizado: 1.2 GB                   │
│  • Última sincronización: 2025-11-08 15:30     │
│                                                 │
│                         [💾 Guardar] [❌ Cerrar]│
└─────────────────────────────────────────────────┘
```

**Componentes:**
- `QLineEdit` + `QPushButton` para ruta base
- `QCheckBox` para auto-crear carpetas
- `QTableWidget` para lista de carpetas personalizables
- Botones de gestión de carpetas
- Labels informativos de estado

**Tareas:**
- [ ] Crear método `create_files_tab()`
- [ ] Implementar selector de directorio
- [ ] Implementar tabla editable de carpetas
- [ ] Implementar validaciones (ruta existe, permisos escritura)
- [ ] Conectar con FileManager para guardar configuración
- [ ] Implementar cálculo de estadísticas de almacenamiento

---

## Fase 7: Modificar ItemEditor

### 7.1 Agregar UI para Subir Archivos
**Archivo:** `src/views/dialogs/item_editor.py`

**Cambios cuando `item_type == "PATH"`:**

```python
def create_form_layout(self):
    # ... código existente ...

    # Detectar si es tipo PATH
    if self.type_combo.currentText() == "PATH":
        self.show_file_upload_section()
    else:
        self.hide_file_upload_section()

def show_file_upload_section(self):
    """Muestra sección de subida de archivos"""
    # Widget contenedor
    self.file_upload_widget = QWidget()
    layout = QVBoxLayout()

    # Botón seleccionar archivo
    btn_layout = QHBoxLayout()
    self.select_file_btn = QPushButton("📁 Seleccionar archivo...")
    self.clear_file_btn = QPushButton("🗑️")
    btn_layout.addWidget(self.select_file_btn)
    btn_layout.addWidget(self.clear_file_btn)

    # Área de información del archivo
    self.file_info_group = QGroupBox("Información del Archivo")
    info_layout = QFormLayout()
    self.file_name_label = QLabel("-")
    self.file_size_label = QLabel("-")
    self.file_type_label = QLabel("-")
    self.file_path_label = QLabel("-")

    info_layout.addRow("📄 Archivo:", self.file_name_label)
    info_layout.addRow("📊 Tamaño:", self.file_size_label)
    info_layout.addRow("📂 Tipo/Carpeta:", self.file_type_label)
    info_layout.addRow("🔗 Ruta destino:", self.file_path_label)

    # Conectar señales
    self.select_file_btn.clicked.connect(self.on_select_file)
    self.clear_file_btn.clicked.connect(self.on_clear_file)

def on_select_file(self):
    """Maneja selección de archivo"""
    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Seleccionar archivo",
        "",
        "Todos los archivos (*.*)"
    )

    if file_path:
        # Obtener metadatos usando FileManager
        metadata = self.file_manager.get_file_metadata(file_path)

        # Verificar duplicados
        duplicate = self.file_manager.check_duplicate(metadata['file_hash'])
        if duplicate:
            # Mostrar diálogo de confirmación
            reply = QMessageBox.question(
                self,
                "Archivo duplicado",
                f"Este archivo ya existe como '{duplicate.label}'.\n¿Desea agregarlo de todos modos?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        # Guardar temporalmente
        self.selected_file_path = file_path
        self.file_metadata = metadata

        # Actualizar UI con información
        self.update_file_info_display(metadata)

        # Auto-llenar label si está vacío
        if not self.label_input.text():
            self.label_input.setText(metadata['original_filename'])

def update_file_info_display(self, metadata: dict):
    """Actualiza labels con información del archivo"""
    self.file_name_label.setText(metadata['original_filename'])
    self.file_size_label.setText(
        self.file_manager.format_file_size(metadata['file_size'])
    )
    self.file_type_label.setText(
        f"{metadata['file_type']} ({self.file_manager.get_target_folder(metadata['file_extension'])})"
    )

    # Construir ruta destino
    base_path = self.file_manager.get_base_path()
    folder = self.file_manager.get_target_folder(metadata['file_extension'])
    dest_path = os.path.join(base_path, folder, metadata['original_filename'])
    self.file_path_label.setText(dest_path)
    self.file_path_label.setWordWrap(True)

def save_item(self):
    """Guardar item (modificado para PATH)"""
    if self.type_combo.currentText() == "PATH" and hasattr(self, 'selected_file_path'):
        # Copiar archivo a ubicación final
        result = self.file_manager.copy_file_to_storage(self.selected_file_path)

        # Usar ruta completa como content
        content = result['full_path']

        # Guardar en BD con metadatos
        item_id = self.db.add_item(
            category_id=self.category_id,
            label=self.label_input.text(),
            content=content,
            item_type="PATH",
            description=self.description_input.toPlainText(),
            is_sensitive=self.sensitive_checkbox.isChecked(),
            # Metadatos
            file_size=result['file_size'],
            file_type=result['file_type'],
            file_extension=result['file_extension'],
            original_filename=result['original_filename'],
            file_hash=result['file_hash']
        )
    else:
        # Lógica existente para otros tipos
        pass
```

**Validaciones:**
- Verificar que ruta base está configurada
- Verificar permisos de escritura
- Validar tamaño del archivo (límite configurable)
- Manejar errores de copia

**Tareas:**
- [ ] Crear sección UI para archivos
- [ ] Implementar selector de archivos
- [ ] Implementar preview de metadatos
- [ ] Implementar detección de duplicados con confirmación
- [ ] Implementar lógica de guardado con copia de archivo
- [ ] Agregar manejo de errores robusto
- [ ] Agregar indicador de progreso para archivos grandes

---

## Fase 8: Mejorar Item Widget

### 8.1 Actualizar ItemWidget para PATH
**Archivo:** `src/views/widgets/item_widget.py`

**Mejoras visuales:**
```python
def update_display(self):
    """Actualizar visualización del item"""
    if self.item.item_type == "PATH":
        # Mostrar ícono según tipo de archivo
        icon = self.item.get_file_type_icon()
        self.icon_label.setText(icon)

        # Mostrar tamaño en label secundario
        if self.item.file_size:
            size_text = self.item.get_formatted_file_size()
            self.size_label.setText(size_text)
            self.size_label.setVisible(True)

def create_tooltip(self) -> str:
    """Crear tooltip mejorado para PATH"""
    if self.item.item_type == "PATH":
        tooltip_parts = []

        if self.item.description:
            tooltip_parts.append(f"📝 {self.item.description}")

        # Información del archivo
        if self.item.original_filename:
            tooltip_parts.append(f"📄 Archivo: {self.item.original_filename}")

        if self.item.file_size:
            tooltip_parts.append(f"📊 Tamaño: {self.item.get_formatted_file_size()}")

        if self.item.file_type:
            tooltip_parts.append(f"📂 Tipo: {self.item.file_type}")

        # Validar si archivo existe
        if not os.path.exists(self.item.content):
            tooltip_parts.append("⚠️ Archivo no encontrado")

        tooltip_parts.append(f"🔗 {self.item.content}")

        return "\n".join(tooltip_parts)
    else:
        # Tooltip existente
        return self.create_standard_tooltip()
```

**Menú contextual adicional:**
- "Abrir archivo" → Abrir con aplicación predeterminada
- "Abrir ubicación" → Abrir carpeta contenedora
- "Verificar existencia" → Validar que archivo existe
- "Propiedades" → Mostrar diálogo con metadatos completos

**Tareas:**
- [ ] Agregar íconos según tipo de archivo
- [ ] Mejorar tooltip con metadatos
- [ ] Agregar opciones de menú contextual
- [ ] Implementar validación de existencia visual
- [ ] Agregar indicador de advertencia si archivo no existe

---

## Fase 9: Migración de Datos Existentes

### 9.1 Script de Migración para Items PATH Existentes
**Archivo:** `util/migrations/migrate_existing_path_items.py`

**Propósito:** Actualizar items existentes de tipo PATH con metadatos

```python
def migrate_existing_path_items():
    """
    Busca items con type='PATH' y agrega metadatos
    si el archivo aún existe
    """
    # 1. Obtener todos los items PATH sin metadatos
    # 2. Para cada item:
    #    - Verificar si archivo existe
    #    - Extraer metadatos
    #    - Actualizar BD
    # 3. Generar reporte de migración
```

**Tareas:**
- [ ] Crear script de migración
- [ ] Manejar archivos que ya no existen
- [ ] Generar reporte detallado
- [ ] Ejecutar y verificar migración

---

## Fase 10: Testing y Validación

### 10.1 Tests Unitarios
**Archivos a crear:**
- `tests/test_file_manager.py`
- `tests/test_path_items.py`

**Casos de prueba:**
- [ ] Detección correcta de tipo de archivo por extensión
- [ ] Cálculo correcto de hash SHA256
- [ ] Copia de archivos a carpetas correctas
- [ ] Detección de duplicados
- [ ] Formato de tamaños (bytes, KB, MB, GB)
- [ ] Validación de existencia de archivos
- [ ] Creación automática de carpetas
- [ ] Manejo de errores (permisos, espacio, etc.)

### 10.2 Tests de Integración
- [ ] Flujo completo: configurar ruta → subir archivo → guardar item
- [ ] Edición de item PATH existente
- [ ] Eliminación de item (¿eliminar archivo físico?)
- [ ] Exportación/importación con archivos PATH

### 10.3 Tests de UI
- [ ] Navegación en pestaña Archivos
- [ ] Selector de archivos funciona correctamente
- [ ] Preview de metadatos se actualiza
- [ ] Diálogo de duplicados se muestra
- [ ] Validación de formularios

---

## Fase 11: Documentación

### 11.1 Actualizar Documentación
**Archivos a actualizar:**
- `CLAUDE.md` - Agregar sección de FileManager y gestión de archivos
- `util/documentacion/GUIA_USUARIO.md` - Tutorial de uso
- `util/documentacion/ARQUITECTURA.md` - Documentar FileManager

**Contenido a documentar:**
- [ ] Cómo configurar ruta base
- [ ] Cómo subir archivos
- [ ] Estructura de carpetas
- [ ] Detección de duplicados
- [ ] Metadatos almacenados
- [ ] Solución de problemas comunes

### 11.2 Comentarios en Código
- [ ] Docstrings en todos los métodos nuevos
- [ ] Comentarios explicativos en lógica compleja
- [ ] Type hints en todas las funciones

---

## Fase 12: Optimizaciones y Mejoras Futuras

### 12.1 Optimizaciones
- [ ] Caché de detección de duplicados
- [ ] Progress bar para archivos grandes (>10MB)
- [ ] Procesamiento asíncrono de hash para archivos grandes
- [ ] Limpieza de archivos huérfanos (sin item asociado)

### 12.2 Mejoras Futuras (Post-MVP)
- [ ] Vista previa de imágenes en tooltip o panel
- [ ] Renombrado automático si archivo con mismo nombre existe
- [ ] Compresión automática de imágenes grandes
- [ ] Sincronización con cloud storage
- [ ] Metadatos avanzados (EXIF, duración videos)
- [ ] Búsqueda por metadatos
- [ ] Filtros por tipo de archivo
- [ ] Estadísticas de almacenamiento por categoría

---

## Checklist de Completitud

### Base de Datos
- [ ] Migración ejecutada exitosamente
- [ ] Campos agregados a tabla items
- [ ] Campos agregados a tabla settings
- [ ] Backup de BD realizado

### Capa de Negocio
- [ ] FileManager implementado y testeado
- [ ] Detección de tipo funciona correctamente
- [ ] Copia de archivos funciona
- [ ] Detección de duplicados funciona
- [ ] Integrado con ConfigManager

### Modelos
- [ ] Modelo Item extendido
- [ ] DBManager actualizado
- [ ] Todos los métodos CRUD actualizados

### Interface de Usuario
- [ ] Pestaña "Archivos" en Settings completa
- [ ] ItemEditor con sección de subida
- [ ] ItemWidget mejorado para PATH
- [ ] Validaciones y mensajes de error

### Testing
- [ ] Tests unitarios pasando
- [ ] Tests de integración pasando
- [ ] Tests de UI realizados manualmente

### Documentación
- [ ] CLAUDE.md actualizado
- [ ] Guía de usuario creada
- [ ] Comentarios en código completos

---

## Estimación de Tiempo

| Fase | Duración Estimada |
|------|-------------------|
| Fase 1-2: Base de datos | 2 horas |
| Fase 3: FileManager | 4 horas |
| Fase 4-5: Modelos y DBManager | 2 horas |
| Fase 6: Settings UI | 3 horas |
| Fase 7: ItemEditor | 4 horas |
| Fase 8: ItemWidget | 2 horas |
| Fase 9: Migración | 1 hora |
| Fase 10: Testing | 3 horas |
| Fase 11: Documentación | 2 horas |
| **TOTAL** | **23 horas** |

---

## Notas Importantes

1. **Backup antes de empezar:** Crear backup completo de la BD antes de cualquier migración
2. **Desarrollo incremental:** Implementar fase por fase, testeando cada una antes de continuar
3. **Manejo de errores:** Priorizar manejo robusto de errores (permisos, espacio, archivos no encontrados)
4. **Compatibilidad retroactiva:** Items PATH existentes deben seguir funcionando
5. **Performance:** Considerar performance con archivos grandes (>100MB)

---

## Dependencias Externas

**Librerías Python necesarias:**
- `hashlib` (built-in) - Para SHA256
- `shutil` (built-in) - Para copia de archivos
- `pathlib` (built-in) - Para manejo de rutas
- `os` (built-in) - Para operaciones de archivos

**No se requieren dependencias adicionales** ✅

---

## Criterios de Éxito

✅ **La implementación será exitosa cuando:**
1. Usuario puede configurar ruta base desde Settings
2. Usuario puede subir archivo y se organiza automáticamente
3. Metadatos se extraen y almacenan correctamente
4. Duplicados se detectan y se avisa al usuario
5. Items PATH muestran información de archivo en UI
6. Archivos se pueden abrir desde la aplicación
7. Tests pasan exitosamente
8. Documentación está completa

---

**Fecha de creación:** 2025-11-08
**Versión:** 1.0
**Estado:** Pendiente de implementación
