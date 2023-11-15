// Define Buttons
const generateButton = document.getElementById('generate');
const genreButtons = document.querySelectorAll('.genre-button');
const selectAllButton = document.getElementById('select-all');
const showGenresButton = document.getElementById('show-genres');

// Update all songs upon clicking "generate" button
generateButton.addEventListener('click', function () {
  const chosenGenresList = getChosenGenres();
  const requestData = { chosenGenresList };

  generateButton.textContent = '...thinking...';

  console.log(requestData);

  fetch('/post_genres', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData),
  })
    .then(console.log('posted genres'))
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      fetch('/get_songs', { method: 'GET' })
        .then((response) => response.json())
        .then((data) => {
          document.getElementById('song-1-embed').src = data.song_1_embed;
          document.getElementById('song-1-genre').textContent = data.song_1_genre;
          document.getElementById('song-2-embed').src = data.song_2_embed;
          document.getElementById('song-2-key').textContent = data.song_2_key;
          document.getElementById('song-3-embed').src = data.song_3_embed;
          document.getElementById('song-3-bpm').textContent = data.song_3_bpm;
          document.getElementById('song-3-time').textContent = data.song_3_time_signature;
          generateButton.textContent = 'Generate Songs';
        })
        .catch((error) => console.error('Error:', error));
    });
});

// Update genre pool buttons when clicked
genreButtons.forEach((button) => {
  button.addEventListener('click', () => {
    button.classList.toggle('clicked');

    if (Array.from(genreButtons).some((button) => button.classList.contains('clicked'))) {
      generateButton.textContent = 'Generate Songs';
      generateButton.style.fontWeight = 'bold';
      generateButton.removeAttribute('disabled');
    } else {
      generateButton.textContent = 'Select at least 1 genre';
      generateButton.style.fontWeight = 'normal';
      generateButton.setAttribute('disabled', 'true');
    }
  });
});

// Collate selected genres into array
function getChosenGenres() {
  const chosenGenres = [];

  genreButtons.forEach((genreButtons) => {
    if (genreButtons.classList.contains('clicked')) {
      chosenGenres.push(genreButtons.id);
    }
  });

  return chosenGenres;
}

// Select all genres
selectAllButton.addEventListener('click', () => {
  const anyChecked = Array.from(genreButtons).some((button) => button.classList.contains('clicked'));

  genreButtons.forEach((button) => {
    if (anyChecked) {
      button.classList.remove('clicked');
      generateButton.textContent = 'Select at least 1 genre';
      generateButton.setAttribute('disabled', 'true');
    } else {
      button.classList.add('clicked');
      generateButton.textContent = 'Generate Songs';
      generateButton.removeAttribute('disabled');
    }
  });
});

// Show/Hide Genre Pool
showGenresButton.addEventListener('click', () => {
  document.getElementById('genre-pool').classList.toggle('hidden');
  if (document.getElementById('genre-pool').classList.contains('hidden')) {
    showGenresButton.textContent = 'Show genres';
  } else {
    showGenresButton.textContent = 'Hide genres';
  }
});
