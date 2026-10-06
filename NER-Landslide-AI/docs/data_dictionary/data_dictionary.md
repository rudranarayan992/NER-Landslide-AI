# Data Dictionary (Planned)

This file contains the planned schema conventions for datasets that will eventually be ingested.

## Historical landslide events

- event_id: unique identifier for an event
- event_date: date when the slide occurred
- event_year: year of occurrence
- latitude: decimal latitude in WGS84
- longitude: decimal longitude in WGS84
- state: state name
- district: district name
- subdistrict: administrative sub-district if available
- village: village or settlement if available
- location_name: human-readable place label
- landslide_type: e.g., rockfall, debris flow, translational slide
- trigger: rainfall, slope failure, excavation, tectonic activity, or other documented cause
- severity: low / moderate / high / severe
- fatalities: integer or null
- injuries: integer or null
- infrastructure_damage: boolean or null
- road_blockage: boolean or null
- rainfall_before_event: rainfall in mm before the event or null
- source_name: original data source
- source_url: source URL or reference
- source_publication: report, paper, or publication name
- source_date: publication or dataset date
- confidence: confidence score from source or null
- geometry: geospatial point for the location

## Rainfall

- timestamp
- latitude
- longitude
- rainfall_1h
- rainfall_3h
- rainfall_6h
- rainfall_12h
- rainfall_24h
- rainfall_3d
- rainfall_7d
- rainfall_30d

## Terrain

- elevation
- slope
- aspect
- curvature
- roughness
- topographic wetness index

## Soil

- soil type
- soil texture
- bulk density
- soil moisture
- organic matter
- clay
- sand
- silt
- permeability

## Geology

- lithology
- geological formation
- rock type
- weathering information
- faults

## Land cover

- vegetation
- built-up area
- agricultural area
- forest
- bare land

## Infrastructure

- roads
- bridges
- settlements
- villages
- important infrastructure

## Data provenance

Every dataset must retain:
- source
- source_url
- provider
- download_timestamp
- dataset_date
- version
- license
- processing_step
- file_hash (if practical)
