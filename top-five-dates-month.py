#  These file gives us info about the top 5 dates in a month of a particular selected place by the user where the tickets have been sold very much.
# Here once u run this file, u will be asked the venue name and the month name and accordingly u will give the output.
# the dataset that we are using here is processed_ticket_data_20241004_134045.csv
# For output example u can refer the top-five-dates-month.png file

import pandas as pd
from datetime import datetime

# CSV फ़ाइल को लोड करना
file_path = "processed_ticket_data_20241004_134045.csv"  # अपनी फाइल के नाम को यहाँ बदलें अगर यह अलग है
data = pd.read_csv(file_path)

# यूज़र से इनपुट लेना (location और month name)
location_input = input("Enter the event time zone (e.g., America/New_York, America/Los_Angeles): ")
month_name_input = input("Enter the name of the month (e.g., January, February, etc.): ").capitalize()

# month_name_input को datetime से month number (01, 02, ...) में कनवर्ट करना
try:
    # माह के नाम को माह के नंबर में बदलना
    month_number = datetime.strptime(month_name_input, "%B").month
    # month_number को 2-digit string में बदलना (01, 02, etc.)
    month_input = f"2024-{str(month_number).zfill(2)}"
except ValueError:
    print("Invalid month name. Please enter a valid month name.")
    exit()

# सही month और location के लिए डेटा को फ़िल्टर करना
filtered_data = data[(data['event_time_zone'] == location_input) & (data['event_date'].str.startswith(month_input))]

# यदि कोई डेटा नहीं है तो, यूज़र को सूचित करना
if filtered_data.empty:
    print(f"No events occurred in {location_input} for the month of {month_name_input}.")
else:
    # sold_ticket के आधार पर descending order में sort करना और top 5 दिनांक चुनना
    top_5_dates = filtered_data.groupby('event_date')['sold_ticket'].sum().reset_index()
    top_5_dates_sorted = top_5_dates.sort_values(by='sold_ticket', ascending=False).head(5)

    # यदि top 5 से कम तिथियाँ हैं तो जितनी भी उपलब्ध हों, वही दिखाएँ
    top_dates = top_5_dates_sorted.head(min(5, len(top_5_dates_sorted)))

    # परिणाम दिखाना
    print(f"\nTop {len(top_dates)} dates in {location_input} for the month of {month_name_input} based on ticket sales:\n")
    print(top_dates[['event_date', 'sold_ticket']])  # केवल event_date और sold_ticket दिखाएँ

    # ग्राफ़िकल विज़ुअलाइज़ेशन के लिए matplotlib का उपयोग (यदि ज़रूरी हो)
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
