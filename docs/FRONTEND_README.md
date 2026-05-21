# Simple Frontend for Game Search Engine

This is a simple Flask-based web frontend for searching games through your Solr instance.

## Features

- 🔍 Simple search interface
- 🎨 Modern, responsive design
- ⚡ Fast results display
- 🎮 Game cards with images, descriptions, and metadata
- 📊 Shows number of results and query time

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements-frontend.txt
```

Or install manually:
```bash
pip install Flask flask-cors requests
```

### 2. Make Sure Solr is Running

Ensure your Solr instance is running on `http://localhost:8983`:

```bash
docker-compose up -d
```

### 3. Run the Frontend Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

### 4. Open in Browser

Navigate to: `http://localhost:5000`

## Usage

1. Enter your search query in the search box
2. Select the number of results you want to see (10, 20, 50, or 100)
3. Click "Search" or press Enter
4. Browse the results with game information, images, and metadata

## Project Structure

```
PRI/
├── app.py                 # Flask backend application
├── requirements-frontend.txt  # Python dependencies
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── style.css         # Stylesheet
│   └── script.js         # Frontend JavaScript
└── ...
```

## Customization

### Change Solr Collection Name

Edit `app.py` and change the `COLLECTION` variable:

```python
COLLECTION = "your_collection_name"  # Default is "courses"
```

### Change Port

Edit the last line in `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=YOUR_PORT)
```

### Modify Search Fields

Edit the `fields` array in `app.py` to change which fields are returned:

```python
"fields": ["id", "title", "about_the_game", ...]
```

### Styling

Modify `static/style.css` to customize the appearance.

## Troubleshooting

### Solr Connection Error

Make sure:
- Docker container is running: `docker ps`
- Solr is accessible: Visit `http://localhost:8983/solr`
- The collection name matches your Solr core name

### No Results Found

- Check if your Solr collection has data
- Try simpler search queries
- Verify the collection name in `app.py` matches your Solr core

### Import Errors

Make sure all dependencies are installed:
```bash
pip install -r requirements-frontend.txt
```

## Example Queries

Try these searches:
- "action adventure games"
- "multiplayer"
- "puzzle strategy"
- "horror survival"

## API Endpoints

### POST /search
Search for games

**Request:**
```json
{
  "query": "action games",
  "rows": 10
}
```

**Response:**
```json
{
  "success": true,
  "results": [...],
  "numFound": 42,
  "qtime": 15
}
```

## Notes

- The frontend uses the same Solr query format as your existing `query_solr.py` script
- Results are displayed in a card layout with images and metadata
- The interface is responsive and works on mobile devices
- Search results show game title, description, release date, price, genres, and more

Enjoy your game search engine! 🎮
