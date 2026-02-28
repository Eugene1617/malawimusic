import os
import sqlite3
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()
cloudinary.config( 
  cloud_name=os.getenv("cloud_name"),
api_key=os.getenv("api_key"),
api_secret=os.getenv("api_secret"),
   secure=True
)
# --- 2. Database Initialization ---
def init_db():
    conn = sqlite3.connect('music', check_same_thread=False)
    cursor = conn.cursor()
    # public_id is required to delete the file from Cloudinary later
    cursor.execute('''CREATE TABLE IF NOT EXISTS music_cat(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        artist_name TEXT,
                        genre TEXT,
                        song_title TEXT,
                        song_url TEXT,
                        public_id TEXT)''')
    conn.commit()
    return conn

conn = init_db()
cursor = conn.cursor()
app = FastAPI(title="Cloud Music API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. Endpoints ---

@app.get("/all-entries")
def get_all_entries():
    cursor.execute("SELECT id, artist_name, genre, song_title, song_url FROM music_cat")
    rows = cursor.fetchall()
    return [
        {"id": r[0], "artist": r[1], "genre": r[2], "song": r[3], "url": r[4]} 
        for r in rows
    ]

@app.post("/upload")
async def upload_artist_and_song(
    artist_name: str = Form(...), 
    genre: str = Form(...),
    song_title: str = Form(...),
    song_file: UploadFile = File(...)
):
    # Clean inputs
    artist = artist_name.strip()
    title = song_title.strip()

    # CHECK FOR DUPLICATES (Artist & Title)
    cursor.execute(
        "SELECT id FROM music_cat WHERE LOWER(artist_name) = LOWER(?) AND LOWER(song_title) = LOWER(?)", 
        (artist, title)
    )
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail=f"The song '{title}' by '{artist}' already exists.")

    try:
        # UPLOAD TO CLOUDINARY
        # Note: resource_type="video" is used for audio files (mp3, wav, etc.)
        upload_result = cloudinary.uploader.upload(
            song_file.file, 
            resource_type="video",
            folder="music_api_storage"
        )
        
        file_url = upload_result.get("secure_url")
        public_id = upload_result.get("public_id")

        # SAVE TO DATABASE
        cursor.execute(
            "INSERT INTO music_cat (artist_name, genre, song_title, song_url, public_id) VALUES (?, ?, ?, ?, ?)",
            (artist, genre, title, file_url, public_id)
        )
        conn.commit()
        
        return {"message": "Upload successful", "artist": artist, "song": title, "url": file_url}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/stream-song/{entry_id}")
def stream_song(entry_id: int):
    cursor.execute("SELECT song_url FROM music_cat WHERE id=? ", (entry_id,))
    result = cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Song not found")
    
    # Redirects the request to the Cloudinary URL for playback
    return RedirectResponse(result[0])

@app.delete("/delete-song")
def delete_song_by_name(artist: str, title: str):
    # FIND SONG AND PUBLIC_ID
    cursor.execute(
        "SELECT id, public_id FROM music_cat WHERE LOWER(artist_name) = LOWER(?) AND LOWER(song_title) = LOWER(?)", 
        (artist.strip(), title.strip())
    )
    result = cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Song not found in database.")
    
    db_id, cloud_id = result

    try:
        # DELETE FROM CLOUDINARY
        cloudinary.uploader.destroy(cloud_id, resource_type="video")

        # DELETE FROM DATABASE
        cursor.execute("DELETE FROM music_cat WHERE id=?", (db_id,))
        conn.commit()

        return {"message": f"Deleted '{title}' by '{artist}' from database and cloud storage."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during deletion: {str(e)}")