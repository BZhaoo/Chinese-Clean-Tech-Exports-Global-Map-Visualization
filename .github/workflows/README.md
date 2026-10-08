# China Clean Tech Exports: Where the Money Lands

An interactive map of China's clean-technology exports, 2018 to present. Bar height shows the US$ value of exports to each destination. Explore by country, sub-region or continental region, filter by technology, set a minimum export value, and play the animation through time.

**Live map:** `https://YOUR-USERNAME.github.io/china-cleantech-export-map/` (replace after enabling GitHub Pages)

## Features
- Bars scaled by export value, with stacked columns by technology (solar PV, batteries, EVs, grid, heating and cooling, wind)
- Group by Countries, Sub-regions or Continental regions; click a region to zoom in
- Minimum-export threshold (slider or typed value), 12-month rolling or single-month measure
- China-to-destination flow lines and a 2018 to present animation
- Zoom and pan; labels and bars avoid overlapping

## Data and credits
- Export data: [Ember Energy, China Cleantech Export Data](https://ember-energy.org/data/china-cleantech-export-data/), based on Chinese customs data, licensed CC-BY-4.0.
- Country borders: [Natural Earth](https://www.naturalearthdata.com/) (public domain).

## Files
| File | Purpose |
|---|---|
| `index.html` | The finished map (what GitHub Pages serves) |
| `build_map.py` | Rebuilds `index.html` from the latest data |
| `template.html` | Page design and logic used by `build_map.py` |
| `ne_110m_admin_0_countries.geojson` | Country borders |
| `.github/workflows/rebuild.yml` | Rebuilds the map automatically on the 10th of each month |

## Publish with GitHub Pages
Settings → Pages → Source: **Deploy from a branch** → branch **main**, folder **/ (root)** → Save.

## Update the data
- **Automatic:** the workflow in `.github/workflows/rebuild.yml` runs monthly. Run it any time from the **Actions** tab → "Rebuild map" → **Run workflow**.
- **Manually:** `pip install pandas`, then
  `python build_map.py <path-or-url-to-csv> index.html ne_110m_admin_0_countries.geojson`

Keep `build_map.py` and `template.html` in the same folder.
