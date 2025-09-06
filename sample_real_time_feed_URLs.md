# Sample GTFS-RT Feed URLs

This document provides examples of what GTFS-RT (Real-Time) feed URLs might look like. These feeds provide real-time information about vehicle locations, service alerts, and trip updates.

## Feed Endpoints

GTFS-RT feeds are typically provided by transit agencies and expose real-time data through a set of URLs. The exact structure of these URLs will vary by provider, but they generally follow a similar pattern.

### Vehicle Locations
Provides real-time vehicle position data for all active vehicles in the system.

**Example URL:**
```
https://api.transitagency.com/gtfs-rt/vehicles
```

### Service Alerts
Provides real-time service alerts and disruptions affecting services.

**Example URL:**
```
https://api.transitagency.com/gtfs-rt/alerts
```

### Trip Updates
Provides real-time updates about trip progress, delays, and schedule changes.

**Example URL:**
```
https://api.transitagency.com/gtfs-rt/trip-updates
```

## Notes
- Feeds may be available in different formats (e.g., JSON, Protocol Buffers).
- Access may require an API key.
- Feeds are typically updated in real-time or at frequent intervals.
- Consult the specific transit agency's developer documentation for the correct URLs and access details.