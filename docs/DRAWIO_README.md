# Fixora draw.io diagrams

## Open the file

1. Go to **https://app.diagrams.net** (draw.io)
2. **File → Open from → Device**
3. Select: `docs/fixora-high-level.drawio`

Or in **VS Code / Cursor**: install extension **Draw.io Integration**, then open `fixora-high-level.drawio`.

## Pages included

| Tab | Diagram |
|-----|---------|
| 1 | High-level system architecture (Figure 15 style) |
| 2 | Three-layer framework (Section 4.3) |
| 3 | System context |
| 4 | Multi-agent collaboration |
| 5 | DFD Level 0 |
| 6 | ER diagram (high-level entities only) |
| 7 | Sequence overview (text flow — expand with UML shapes) |

## Export for Word / PDF

1. Open the page you need  
2. **File → Export as → PNG** or **PDF**  
3. Insert into thesis with caption: *Source: Researcher's own work, 2026*

## Edit tips

- Drag shapes to reposition; colours match report layers (blue = UI, green = agents, yellow = API, purple = orchestration).
- **Page 7**: For a formal UML sequence diagram, use **+ → Advanced → Mermaid** and paste from `DESIGN_DIAGRAMS.md` Figure C, or add lifelines from the left panel (**UML → Sequence**).

## MySQL ER (detailed)

For a full ER with all columns:

1. Run Fixora MySQL (`docker compose up mysql`)
2. MySQL Workbench → **Database → Reverse Engineer**
3. Export PNG separately as *Figure: Detailed ER diagram*
