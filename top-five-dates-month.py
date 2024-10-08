
import pandas as pd
from datetime import datetime


file_path = "processed_ticket_data_20241004_134045.csv" 
data = pd.read_csv(file_path)


location_input = input("Enter the event time zone (e.g., America/New_York, America/Los_Angeles): ")
month_name_input = input("Enter the name of the month (e.g., January, February, etc.): ").capitalize()


try:
  
    month_number = datetime.strptime(month_name_input, "%B").month

    month_input = f"2024-{str(month_number).zfill(2)}"
except ValueError:
    print("Invalid month name. Please enter a valid month name.")
    exit()


filtered_data = data[(data['event_time_zone'] == location_input) & (data['event_date'].str.startswith(month_input))]


if filtered_data.empty:
    print(f"No events occurred in {location_input} for the month of {month_name_input}.")
else:
  
    top_5_dates = filtered_data.groupby('event_date')['sold_ticket'].sum().reset_index()
    top_5_dates_sorted = top_5_dates.sort_values(by='sold_ticket', ascending=False).head(5)


    top_dates = top_5_dates_sorted.head(min(5, len(top_5_dates_sorted)))


    print(f"\nTop {len(top_dates)} dates in {location_input} for the month of {month_name_input} based on ticket sales:\n")
    print(top_dates[['event_date', 'sold_ticket']]) 

  
    try:
        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 6))
        plt.bar(top_dates['event_date'], top_dates['sold_ticket'], color='orange')
        plt.xlabel('Event Date')
        plt.ylabel('Total Sold Tickets')
        plt.title(f'Top {len(top_dates)} Dates for Ticket Sales in {location_input} ({month_name_input})')
        plt.xticks(rotation=45)
        for index, value in enumerate(top_dates['sold_ticket']):
            plt.text(index, value, str(value), ha='center', va='bottom')
        plt.show()
    except ImportError:
        print("matplotlib not installed. Please install it to see the graph visualization.")
