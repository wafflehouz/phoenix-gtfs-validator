import pandas as pd
import numpy as np
from datetime import datetime
import gtfs_kit as gk
import sys

# Load the GTFS feed
# GTFS (General Transit Feed Specification) is a standard format for public transportation schedules
# gtfs_kit provides convenient methods to read and process GTFS data
feed = gk.read_feed('googletransit', dist_units='km')

def get_all_trips_for_route(feed, route_id):
    """
    Get all trips for a specific route from the GTFS dataset.
    
    Why this is needed:
    - We need to find all trips that belong to the specified route
    - Each trip represents a specific journey on that route
    - We want to capture all service patterns for this route (weekday, weekend, etc.)
    """
    # Filter trips for the specific route
    # Each trip represents a specific journey on the route
    route_trips = feed.trips[feed.trips['route_id'] == route_id]
    
    if route_trips.empty:
        print(f"No trips found for route {route_id}")
        return pd.DataFrame()
    
    print(f"Found {len(route_trips)} trips for route {route_id}")
    
    # Get stop times for all trips on this route
    # stop_times.txt contains the detailed schedule for each trip
    # It tells us exactly when a vehicle arrives at and departs from each stop
    trip_stop_times = feed.stop_times[feed.stop_times['trip_id'].isin(route_trips['trip_id'])]
    
    if trip_stop_times.empty:
        print(f"No stop times found for trips on route {route_id}")
        return pd.DataFrame()
    
    # Get first and last stops for each trip
    # These represent the origin and destination of each trip
    first_stops = trip_stop_times.groupby('trip_id').first().reset_index()
    last_stops = trip_stop_times.groupby('trip_id').last().reset_index()
    
    # Merge with stops to get stop names and coordinates
    # stops.txt contains the names and locations of all stops
    # We need this to show meaningful stop names and coordinates in our output
    first_stops = first_stops.merge(feed.stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']], on='stop_id')
    last_stops = last_stops.merge(feed.stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']], on='stop_id')
    
    # Merge with trips to get route and direction info
    # This ensures we have the correct route and direction for each trip
    first_stops = first_stops.merge(route_trips[['trip_id', 'route_id', 'direction_id', 'service_id']], on='trip_id')
    
    # Create the final table
    # This is the output format that shows:
    # - Route identification
    # - Direction of travel
    # - Origin stop and departure time
    # - Destination stop and arrival time
    # - Coordinates for both origin and destination
    # - Service ID to identify the service pattern
    route_table = pd.DataFrame({
        'route_id': first_stops['route_id'],
        'direction': first_stops['direction_id'].map({0: 'NB', 1: 'SB', 2: 'WB', 3: 'EB'}),
        'origin_name': first_stops['stop_name'],
        'origin_latitude': first_stops['stop_lat'],
        'origin_longitude': first_stops['stop_lon'],
        'origin_departure_time': first_stops['departure_time'],
        'destination_name': last_stops['stop_name'],
        'destination_latitude': last_stops['stop_lat'],
        'destination_longitude': last_stops['stop_lon'],
        'destination_arrival_time': last_stops['arrival_time'],
        'service_id': first_stops['service_id']
    })
    
    # Sort by service_id, departure time, and direction
    # This groups all trips with the same service pattern together
    # Then sorts chronologically within each service group
    route_table = route_table.sort_values(['service_id', 'origin_departure_time', 'direction'])
    
    # Remove any rows where times are null
    # Invalid or missing times would make the table unreliable
    route_table = route_table.dropna(subset=['origin_departure_time', 'destination_arrival_time'])
    
    return route_table

def main():
    """
    Main function to process command line arguments and generate the route table.
    """
    # Check if route ID is provided as command line argument
    if len(sys.argv) != 2:
        print("Usage: python single_route_all_trips.py <route_id>")
        print("Example: python single_route_all_trips.py 0")
        print("Example: python single_route_all_trips.py 0A")
        sys.exit(1)
    
    route_id = sys.argv[1]
    print(f"Processing all trips for route {route_id}")
    
    # Get all trips for the specified route
    route_table = get_all_trips_for_route(feed, route_id)
    
    if route_table.empty:
        print(f"No valid trips found for route {route_id}")
        sys.exit(1)
    
    # Create output filename
    output_file = f'route_{route_id}_all_trips.csv'
    
    # Save to CSV
    route_table.to_csv(output_file, index=False)
    print(f"Created {output_file} with {len(route_table)} trips")
    print(f"Columns: {', '.join(route_table.columns)}")

if __name__ == "__main__":
    main() 