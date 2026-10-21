# Changelog

Formato basado en *Keep a Changelog*. Fechas en UTC.

## 0.7.1 — 2026-10-21

### Añadido
- Datos fiscales completos del emisor en la cotización: sitio web, dirección,
  ciudad, estado, código postal y país (nuevas columnas en `empresa_config`,
  migración `0007_empresa_direccion`).
- Campos de domicilio en **Configuración → Empresa**.

### Cambiado
- PDF de cotización rediseñado con HTML/CSS (WeasyPrint) y la estética HAPMED /
  Apple HIG: cabecera con logo y datos del emisor, tarjetas de emisor y cliente,
  metadatos, tabla de partidas, totales, notas y pie legal.
- El PDF respeta los colores de marca de la empresa.
- Los ceros de las columnas de partidas (cantidad, precio, descuento, entrega e
  importe) ya no se imprimen: la celda queda vacía.

### Eliminado
- Dependencia `fpdf2`; el PDF se genera con `weasyprint` + `jinja2`.
