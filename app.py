from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os

app = Flask(__name__)

# Set your secret key
app.secret_key = os.environ.get('SECRET_KEY', '123456')  # Using environment variable for security

# Load your CSV file
file_path = 'final_data.csv'  # Replace with your actual file path

# Load DataFrame
df = pd.read_csv(file_path) if os.path.exists(file_path) else pd.DataFrame()

# Calculate occupancy percentage
def calculate_occupancy():
    if df.empty:
        return
    df['occupancy'] = 100 - ((df['availability_standard'] / df['capacity']) * 100)
    df['occupancy'] = df['occupancy'].fillna(0).astype(float)
    df.to_csv(file_path, index=False)

# Home route
@app.route('/')
def index():
    venues = df['venue_id'].unique() if not df.empty else []
    return render_template('index.html', venues=venues)

# Route to get mean occupancy
@app.route('/mean_occupancy', methods=['GET', 'POST'])
def mean_occupancy():
    if request.method == 'POST':
        venue_id = request.form['venue_id']
    else:
        venue_id = request.args.get('venue_id')

    if not venue_id:
        flash("Venue ID is required.")
        return redirect(url_for('index'))

    try:
        page = int(request.args.get('page', 1))
        venue_id = int(venue_id)

        calculate_occupancy()

        # Filter DataFrame by selected venue_id
        filtered_df = df[df['venue_id'] == venue_id]

        if filtered_df.empty:
            flash("No data found for the selected venue ID.")
            return redirect(url_for('index'))

        # Get event time zone for the selected venue_id
        event_time_zone = filtered_df['event_time_zone'].iloc[0]

        # Calculate mean occupancy per section and venue
        mean_occupancy = filtered_df.groupby(['section_id', 'venue_id'])['occupancy'].mean().reset_index()
        mean_occupancy.columns = ['section_id', 'venue_id', 'mean_occupancy_percentage']
        mean_occupancy['mean_occupancy_percentage'] = mean_occupancy['mean_occupancy_percentage'].round(2)
        mean_occupancy['serial_number'] = range(1, len(mean_occupancy) + 1)

        # Get filter mean occupancy if exists
        filter_mean_occupancy = request.args.get('filter_mean_occupancy')
        section_id_search = request.args.get('section_id_search')

        # Adjust filtering conditions
        if filter_mean_occupancy:
            filters = {
                "100": (100, 101),
                "90-100": (90, 100),
                "80-90": (80, 90),
                "70-80": (70, 80),
                "60-70": (60, 70),
                "50-60": (50, 60),
                "less than 50": (0, 50)
            }
            if filter_mean_occupancy in filters:
                low, high = filters[filter_mean_occupancy]
                mean_occupancy = mean_occupancy[(mean_occupancy['mean_occupancy_percentage'] >= low) & 
                                                 (mean_occupancy['mean_occupancy_percentage'] < high)]

        # Filter by section ID if provided
        if section_id_search:
            mean_occupancy = mean_occupancy[mean_occupancy['section_id'] == section_id_search]

        # Pagination logic
        chunk_size = 100
        total_rows = len(mean_occupancy)
        total_pages = (total_rows + chunk_size - 1) // chunk_size
        start_row = (page - 1) * chunk_size
        end_row = start_row + chunk_size
        paginated_data = mean_occupancy.iloc[start_row:end_row]

        # Specify paths to your PNG images
        image_folder = f'static/{event_time_zone}'  # Directory based on the event_time_zone
        top_images = []  # To hold top images if they exist
        other_images = []  # To hold other images

        # Ensure the directory exists and load images
        if os.path.exists(image_folder):
            # Check for top images (1.png and 2.png)
            for img_name in ['1.png', '2.png']:
                img_path = os.path.join(image_folder, img_name)
                if os.path.isfile(img_path):
                    top_images.append(f'{image_folder}/{img_name}')  # Store full path for template rendering

            # Add all other images in the directory excluding top images
            for img in os.listdir(image_folder):
                img_path = os.path.join(image_folder, img)
                if os.path.isfile(img_path) and img.endswith(('.png', '.jpg', '.jpeg')) and img not in ['1.png', '2.png']:
                    other_images.append(f'{image_folder}/{img}')  # Store full path for template rendering

        return render_template(
            'results.html',
            paginated_data=paginated_data,
            page=page,
            total_pages=total_pages,
            venue_id=venue_id,
            event_time_zone=event_time_zone,
            top_images=top_images,
            other_images=other_images
        )

    except ValueError:
        flash("Invalid venue ID.")
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)