import pandas as pd
import numpy as np
from datetime import datetime
import gtfs_kit as gk

# Load the GTFS feed
# GTFS (General Transit Feed Specification) is a standard format for public transportation schedules
# gtfs_kit provides convenient methods to read and process GTFS data
feed = gk.read_feed('googletransit', dist_units='km')

def classify_service_ids_by_day(calendar_dates, calendar, target_date):
    """
    Classify service_ids as 'weekday', 'saturday', or 'sunday' for a given date.
    Returns a dict: {day_type: [service_ids]}
    
    Why this is needed:
    - GTFS feeds often have different service patterns for different days of the week
    - Some routes might only run on weekdays, others on weekends
    - Service IDs are used to group trips that follow the same schedule pattern
    - We need to identify which service IDs are active on our target date
    """
    # Convert target_date to datetime
    # This allows us to determine the day of the week for the target date
    # GTFS feeds often use YYYYMMDD format for dates
    target_dt = datetime.strptime(target_date, '%Y%m%d')
    day_of_week = target_dt.strftime('%A').lower()
    
    # Initialize active services list
    # We'll collect all service IDs that are active on our target date
    active_services = []
    
    # If calendar.txt exists, get services from it
    # calendar.txt defines regular service patterns (e.g., "runs every Monday")
    # This is the primary source for determining which services run on which days
    if calendar is not None:
        calendar_services = calendar[
            (calendar['start_date'] <= int(target_date)) & 
            (calendar['end_date'] >= int(target_date)) &
            (calendar[day_of_week] == 1)
        ]['service_id'].tolist()
        active_services.extend(calendar_services)
    
    # Add any service exceptions for this date
    # calendar_dates.txt defines exceptions to the regular schedule
    # For example, a route might not run on a specific holiday
    if calendar_dates is not None:
        exceptions = calendar_dates[
            (calendar_dates['date'] == int(target_date)) & 
            (calendar_dates['exception_type'] == 1)
        ]['service_id'].tolist()
        active_services.extend(exceptions)
    
    # If no services found through calendar or exceptions, use all service IDs
    # This is a fallback to ensure we don't miss any services
    # Some GTFS feeds might only use calendar_dates.txt or have a different structure
    if not active_services and hasattr(feed, 'trips'):
        active_services = feed.trips['service_id'].unique().tolist()
    
    # Remove duplicates to ensure each service ID is only counted once
    active_services = list(set(active_services))
    
    # Classify services based on their names
    # This is a heuristic approach - we look for keywords in the service_id
    # to determine if it's a weekday, Saturday, or Sunday service
    classified = {'weekday': [], 'saturday': [], 'sunday': []}
    for sid in active_services:
        if 'Saturday' in sid or '7-days' in sid:
            classified['saturday'].append(sid)
        elif 'Sunday' in sid:
            classified['sunday'].append(sid)
        else:
            classified['weekday'].append(sid)
    return classified

def create_route_table(feed, service_ids, day_type):
    """
    Create a timetable table for the specified day type.
    
    Why this is needed:
    - We need to show the first trip of the day for each route and direction
    - This helps passengers plan their earliest possible journey
    - The table needs to show both the start and end points of each route
    - Direction information is crucial for understanding the route's path
    """
    if not service_ids:
        print(f"No service IDs found for {day_type}")
        return pd.DataFrame()
        
    # Filter trips for the specific service IDs
    # Each trip represents a specific journey on a route
    # We only want trips that are part of our target service pattern
    day_trips = feed.trips[feed.trips['service_id'].isin(service_ids)]
    if day_trips.empty:
        print(f"No trips found for {day_type}")
        return pd.DataFrame()
        
    # Get stop times for all trips
    # stop_times.txt contains the detailed schedule for each trip
    # It tells us exactly when a vehicle arrives at and departs from each stop
    trip_stop_times = feed.stop_times[feed.stop_times['trip_id'].isin(day_trips['trip_id'])]
    
    # Find the first trip of the day for each route and direction
    # We need to group by route and direction because:
    # - Each route can have multiple directions (e.g., northbound and southbound)
    # - We want the earliest trip in each direction
    first_trips = []
    for (route_id, direction_id), route_trips in day_trips.groupby(['route_id', 'direction_id']):
        # Get all trips for this route and direction
        route_stop_times = trip_stop_times[trip_stop_times['trip_id'].isin(route_trips['trip_id'])]
        
        # Find the trip with the earliest departure time
        # This ensures we get the first service of the day
        earliest_trip = route_stop_times.sort_values('departure_time').iloc[0]['trip_id']
        first_trips.append(earliest_trip)
    
    # Get stop times for first trips
    # Now we have the schedule for just the first trip of each route/direction
    first_trip_stops = trip_stop_times[trip_stop_times['trip_id'].isin(first_trips)]
    
    # Get first and last stops for each trip
    # These represent the origin and destination of each route
    first_stops = first_trip_stops.groupby('trip_id').first().reset_index()
    last_stops = first_trip_stops.groupby('trip_id').last().reset_index()
    
    # Merge with stops to get stop names
    # stops.txt contains the names and locations of all stops
    # We need this to show meaningful stop names in our output
    first_stops = first_stops.merge(feed.stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']], on='stop_id')
    last_stops = last_stops.merge(feed.stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']], on='stop_id')
    
    # Merge with trips to get route and direction info
    # This ensures we have the correct route and direction for each trip
    first_stops = first_stops.merge(day_trips[['trip_id', 'route_id', 'direction_id']], on='trip_id')
    
    # Create the final table
    # This is the output format that shows:
    # - Route identification
    # - Direction of travel
    # - Origin stop and departure time
    # - Destination stop and arrival time
    # - Coordinates for both origin and destination
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
        'destination_arrival_time': last_stops['arrival_time']
    })
    
    # Sort by Route ID and Direction
    # This makes the table easier to read and navigate
    route_table = route_table.sort_values(['route_id', 'direction'])
    
    # Remove any rows where times are null
    # Invalid or missing times would make the table unreliable
    route_table = route_table.dropna(subset=['origin_departure_time', 'destination_arrival_time'])
    
    return route_table

# Use the specified dates for each day type
# These dates are chosen to represent:
# - A typical weekday (Monday)
# - A Saturday
# - A Sunday
dates = {
    'weekday': '20250602',  # Monday
    'saturday': '20250607',  # Saturday
    'sunday': '20250608'    # Sunday
}

# Create tables for each day type
# This loop processes each day type separately because:
# - Different days have different service patterns
# - We want separate tables for easier reference
# - It allows for comparison between weekday and weekend service
for day_type, target_date in dates.items():
    print(f"\nProcessing {day_type} schedule for date {target_date}")
    service_ids_by_day = classify_service_ids_by_day(feed.calendar_dates, feed.calendar, target_date)
    print(f"Found {len(service_ids_by_day[day_type])} service_ids for {day_type}")
    
    route_table = create_route_table(feed, service_ids_by_day[day_type], day_type)
    output_file = f'route_timetable_{day_type}.csv'
    route_table.to_csv(output_file, index=False)
    print(f"Created {day_type} table with {len(route_table)} routes") 