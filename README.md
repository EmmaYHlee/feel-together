# FeelTogether

FeelTogether is an emotion-first social platform that restructures online interaction around emotional states rather than algorithmic engagement. Users enter one of four emotional spaces (Happy, Sad, Angry, Boring) and share doodles and reflections with others experiencing the same emotion.

The system enforces emotional separation so that users only see content aligned with their current emotional state.

## Getting Started
 
### Requirements
 
- Python 3.8+ (verify with `python3 --version`)
- pip
- A modern web browser (Chrome, Firefox, Safari, or Edge)
### Installation
 
```bash
cd feel_together
pip install flask pillow
```
 
No manual database setup is needed — `feeltogether.db` and the `uploads/` directory are created automatically on first run.
 
### Running the App
 
```bash
python app.py
```
 
You should see:
 
```
DB ready, http://localhost:5000
```
 
Then open **http://localhost:5000** in your browser.

---

## 1. Overview

### Problem

Traditional social media mixes emotionally incompatible content into a single feed, often intensifying negative feelings through emotional contrast and comparison.

Research has shown:
- High social media usage is associated with increased anxiety and depression (Valkenburg et al., 2022)
- Many users report worsened mood after social media use (APA, 2023)

---

### Solution

FeelTogether introduces an **emotion-segmented social model**:

- Users select their current emotional state
- They enter a matching emotional space
- All content is restricted to that emotion
- Users express themselves via doodles and short reflections
- Interaction is based on peer recognition rather than algorithms

---

## 2. Features

### Emotion Segmentation
- Four isolated spaces: Happy / Sad / Angry / Boring
- Server-side enforcement using cookies
- No cross-emotion interaction

### Doodle System
- HTML5 canvas drawing tool
- Pen, eraser, brush controls
- Optional text reflection per doodle
- Anonymous posting supported

### Physics Board
- Floating doodle cards with physics-based movement
- Drag-and-drop interaction
- Popular doodles scale with likes

### Social Interaction
- Like / dislike system (login required)
- Users can delete their own doodles
- Anonymous posting allowed (limited permissions)

### Mood-Aware UI
- Dynamic theme colors per emotion
- Background music per emotional state
- Animated UI elements tied to mood

---

## 3. Tech Stack

### Backend
- Flask (Python)
- SQLite
- Pillow (image processing)
- hashlib (password hashing)

### Frontend
- Vanilla JavaScript
- HTML5 Canvas API
- CSS (no frameworks)
- Jinja2 templates

---

## 4. Project Structure

```text
feel_together/
├── app.py
├── feeltogether.db
├── uploads/
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── draw.html
│   ├── board.html
│   └── signup.html
│
├── static/
│   ├── app.js
│   ├── style.css
│   └── music/
│       ├── happy.mp3
│       ├── sad.mp3
│       ├── angry.mp3
│       └── boring.mp3
