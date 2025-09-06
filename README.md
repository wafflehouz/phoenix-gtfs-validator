# Phoenix GTFS Validator

A Python toolkit for analyzing Phoenix Valley Metro's publicly available GTFS (General Transit Feed Specification) data to reverse engineer transit timetables and validate trip planning information.

## Purpose

This project transforms raw GTFS data from Phoenix Valley Metro into structured timetables that can be used to:
- **Validate trip planning times** posted on Google Maps, Apple Maps, and other third-party applications
- **Analyze transit service patterns** across different days of the week
- **Extract detailed trip information** for specific routes
- **Compare weekday vs weekend service** variations

## What You Get

The toolkit generates comprehensive CSV files containing:
- **Route timetables** separated by service type (weekday, Saturday, Sunday)
- **First trip departure times** for each route and direction
- **Detailed trip analysis** for individual routes including all stops and times
- **Service pattern classification** to understand when routes operate

## Quick Start

### Prerequisites
- Python 3.9+
- Phoenix Valley Metro GTFS feed (download from [Valley Metro's GTFS page](https://www.valleymetro.org/gtfs))

### 1. Clone and Setup
```bash
git clone <repository-url>
cd phoenix-gtfs-validator
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Add GTFS Data
- Download the latest GTFS feed from Valley Metro
- Extract the contents to a `googletransit/` directory in the project root
- The directory should contain files like `stops.txt`, `trips.txt`, `routes.txt`, etc.

### 3. Generate Network Timetables
```bash
python full_network_first_trip.py
```

This creates three CSV files:
- `route_timetable_weekday.csv` - Weekday first trip times
- `route_timetable_saturday.csv` - Saturday first trip times  
- `route_timetable_sunday.csv` - Sunday first trip times

### 4. Analyze Specific Routes
```bash
python single_route_all_trips.py <route_id>
```

Examples:
```bash
python single_route_all_trips.py 0      # Route 0
python single_route_all_trips.py 0A     # Route 0A
```

This generates `route_<route_id>_all_trips.csv` with complete trip details.

## Finding Route IDs

```bash
# From generated timetables
cut -d, -f1 route_timetable_weekday.csv | sort -u | head -n 20

# Directly from GTFS data
cut -d, -f1 googletransit/routes.txt | tail -n +2 | sort -u | head -n 20
```

## Output Files

| File | Description |
|------|-------------|
| `route_timetable_weekday.csv` | First trip times for all routes on weekdays |
| `route_timetable_saturday.csv` | First trip times for all routes on Saturdays |
| `route_timetable_sunday.csv` | First trip times for all routes on Sundays |
| `route_<id>_all_trips.csv` | Complete trip details for a specific route |

## Dependencies

- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `gtfs-kit` - GTFS data processing

## Updating Data

To use a newer GTFS feed:
1. Download the latest feed from Valley Metro
2. Replace the `googletransit/` directory
3. Re-run the scripts

## Use Cases

- **Transit Planning**: Validate that published schedules match GTFS data
- **Service Analysis**: Compare weekday vs weekend service patterns
- **Route Investigation**: Deep dive into specific route operations
- **Data Validation**: Ensure third-party apps are using accurate transit data

## Related Projects

This GTFS analysis toolkit is part of a broader transit data validation system. For inquiries about additional applications or private access to extended functionality, please open an issue or contact the maintainer.

## Contributing

This project uses publicly available Phoenix Valley Metro data. Contributions are welcome for:
- Additional analysis scripts
- Data validation improvements
- Documentation enhancements
- Bug fixes

## License

This project is open source. The GTFS data is provided by City of Phoenix - Valley Metro under their terms of use.

## Data Source

- **GTFS Feed**: [Phoenix - Valley Metro Bus Schedule](https://phoenixopendata.com/dataset/valley-metro-bus-schedule)
- **Data Format**: [GTFS Specification](https://gtfs.org/)

