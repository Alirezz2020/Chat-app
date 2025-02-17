# ChatProject

A real-time chat application built with **Django** and **Django Channels** (daphne).  
Users can create profiles, send messages in one-to-one or group chats, and share images in their profiles.

## Features

- **User Registration & Authentication**  
  Users can register and log in to create profiles with pictures and bios.

- **One-to-One Chat**  
  Users can search for others by a unique ID and chat in real time.  
  Unread messages are marked as "sent" until the receiver opens the chat.

- **Group Chats**  
  - Users can create groups with a unique group ID (no spaces) and invite others.  
  - Group owners can edit group info, remove members, or delete the group.  
  - Non-members can see a group in search results but cannot access the group chat until they join.  
  - A user can leave a group unless they are the group owner.

- **Profile Page**  
  - Each user has a profile with a display picture, bio, and unique ID.  
  - Users can edit their profile details.

- **Read/Unread Message Tracking**  
  - Once a user opens a chat, all unread messages in that chat are marked as read.



## Prerequisites

- **Python 3.8+**  
- **Django 3.2+**  
- **Django Channels**  
- **Redis** (Recommended for production; optional for dev if using InMemoryChannelLayer)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Alirezz2020/Chat-app.git
   cd Chat-app

2. Create and Activate a Virtual Environment :
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install Dependencies**
    ```bash
   pip install -r requirements.txt

4. **Run migrations**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
5. **Run the Server**
    ```bash
   python manage.py runserver
6. **Open your browser at http://127.0.0.1:8000/**


## Usage

Register or Log in.
Create your Profile (if prompted).
Search for Users by unique ID or create/join groups in the “Groups” section.
Send Messages in one-to-one or group chats.
Profile – View or edit your profile from the navbar.

## Contributing

Fork the project.
Create your feature branch (git checkout -b feature/new-stuff).
Commit your changes (git commit -m 'Add some new stuff').
Push to the branch (git push origin feature/new-stuff).
Open a Pull Request.

## License

This project is open-sourced under the MIT License. Feel free to use it as a reference or a starting point.

# NOTE
I am aweful at frontend specially in this project and only focused on BACKEND
