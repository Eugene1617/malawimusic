let section =document.getElementById("main_body");
function submit() {
  const name = document.querySelector("#name").value.toUpperCase();
  const password = document.querySelector("#password").value;

  if (name || password) {
    if (name === "ADMIN" || password === "Malawi@vibes") {
      admin();
    } else {
      alert("wrong details");
    }
  } else {
    return 0;
  }
}
function admin() {
  section.innerHTML = "";
  section.innerHTML =
    "<section id='main_body'><main id='login' > <h1> choose operation</h1><div> <button class='but' onclick=view_all_music() >view all music</button> <button class='but' onclick=Delete()>delete form the website</button> <button onclick=upload() class='but'>upload new music</button> </div></main></section>";
}

function Delete(){
  section.innerHTML="";
  section.innerHTML="<input type='text' id='delete' placeholder='enter the name of artist'> <input type='text' id='album' placeholder='enter the song name'> <button onclick=delete_music() class='but'>delete</button>"
  
}

function upload(){
  section.innerHTML="";
  section.innerHTML="<input type='text' id='artist' placeholder='enter the name of artist'><input type='text' id='genre' placeholder='enter the genre of the song'> <input type='text' id='song' placeholder='enter song title'><label for='file'>Choose a file:</label><input type='file' id='file'><button onclick=upload_music() class='but'>upload</button>"
}
async function delete_music() {
  const artist = document.getElementById("delete").value.trim();
  const title = document.getElementById("album").value.trim();

  if (!artist || !title) {
    alert("Please enter both artist and song title.");
    return;
  }

  try {
    const params = new URLSearchParams({ artist, title });
    const response = await fetch(`https://malawimusic.onrender.com/delete-song?${params}`, {
      method: "DELETE"
    });

    const data = await response.json();
    
    if (response.ok) {
      alert(data.message || "Music deleted successfully");
    } else {
      alert("Failed to delete music: " + (data.detail || "Unknown error"));
    }
  } catch (error) {
    console.error("Delete error:", error);
    alert("Network/server error while deleting music.");
  }
}

async function upload_music() {
  const artist = document.getElementById("artist").value.trim();
  const genre = document.getElementById("genre").value.trim();
  const song = document.getElementById("song").value.trim();
  const file = document.getElementById("file").files[0];

  if (!artist || !genre || !song || !file) {
    alert("Please fill artist, genre, title, and choose a file.");
    return;
  }

  const formData = new FormData();
  formData.append("artist_name", artist);
  formData.append("genre", genre);
  formData.append("song_title", song);
  formData.append("song_file", file);

  try {
    const response = await fetch("https://malawimusic.onrender.com/upload", {
      method: "POST",
      body: formData
    });

    const data = await response.json();
    if (response.ok) {
      alert(data.message || "Music uploaded successfully!");
    } else {
      alert("Failed to upload music: " + (data.detail || "Unknown error"));
    }
  } catch (error) {
    console.error("Upload error:", error);
    alert("Network/server error while uploading music.");
  }
}
async function view_all_music() {
  section.innerHTML = "";
  try {
    const response = await fetch("https://malawimusic.onrender.com/all-entries");
    const data = await response.json();
    if (response.ok) {
      if (data.length === 0) {
        section.innerHTML = "<p>No music entries found.</p>";
        return;
      }
      let html = "<div class='music_entries'>";
      data.forEach(entry => {
        html += `<div class='entry'><h3>${entry.song}</h3><p>Artist: ${entry.artist}</p><p>Genre: ${entry.genre}</p></div>`;
      });
      html += "</div>";
      section.innerHTML = html;
    } else {
      section.innerHTML = "<p>Error fetching music entries.</p>";
    }
  } catch (error) {
    console.error("Error fetching all entries:", error);
    section.innerHTML = "<p>Error fetching music entries.</p>";
  }
}

