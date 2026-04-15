# Sessions Marketplace

A full-stack web application where users can browse and book sessions,
and creators can publish and manage their own sessions.

## Tech Stack

| Layer          | Technology                        |
|----------------|-----------------------------------|
| Frontend       | React + Vite                      |
| Backend        | Django + Django REST Framework    |
| Database       | PostgreSQL 15                     |
| Reverse Proxy  | Nginx                             |
| Auth           | OAuth 2.0 (Google/GitHub) + JWT   |
| Infrastructure | Docker + Docker Compose           |

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/)
- A Google or GitHub OAuth app (see setup below)

---

## Setup Steps

### 1. Clone the repository

git clone https://github.com/YOUR_USERNAME/sessions-marketplace.git
cd sessions-marketplace

### 2. Configure environment variables

cp .env.example .env

Open `.env` and fill in:
- Your Django secret key
- Your OAuth credentials (Google or GitHub
- Razorpay key and secret key
- VITE_GOOGLE_CLIENT_ID: with same google client id
- Keep the rest as-is for local development

### 3. Start the application

docker-compose up --build

That's it. One command starts all 4 containers.

| Service   | URL                          |
|-----------|------------------------------|
| App        | http://localhost/5173        |
| Backend API| http://localhost/api         |
| Django Admin| http://localhost/admin      |
| Backend direct | http://localhost:8000   |

### 4. Create a superuser (optional, for admin access)

In a new terminal while containers are running:

docker exec -it sessions_backend python manage.py createsuperuser

---

## OAuth Client Setup

### Google OAuth

1. Go to https://console.cloud.google.com
2. Create a new project (or select existing)
3. Navigate to **APIs & Services → Credentials**
4. Click **Create Credentials → OAuth 2.0 Client ID**
5. Application type: **Web application**
6. Authorized JavaScript origins
URIs 1 
http://localhost
URIs 2 
http://localhost:5173
7. Authorized redirect URIs
URIs 1 
http://localhost
URIs 2 
http://localhost/api/auth/google/
URIs 3 
http://localhost:5173
URIs 4 
http://localhost:8000/api/auth/google/
URIs 5 
http://localhost:5173/auth/google/callback
URIs 6 
http://localhost/auth/google/callback

## Demo Flow

### As a User — Browse and Book a Session

1. Open http://localhost
2. Click **Sign in with Google**
3. After login you land on the **Session Catalog**
4. Browse available sessions, click any session card
5. On the Session Detail page, click **Book Now**
6. Go to **My Dashboard** to see your active booking

### As a Creator — Create and Manage Sessions

1. Sign in via OAuth
2. Go to **Profile → Role** and switch to **Creator**
   (or ask an admin to assign the Creator role via `/admin`)
3. Navigate to **Creator Dashboard**
4. Click **Create Session** — fill in title, description, price, date/time
5. Your session is now live in the public catalog
6. Under **Bookings Overview** you can see who has booked your sessions

### Admin

1. Go to http://localhost/admin
2. Log in with the superuser credentials you created
3. Manage users, sessions, and bookings directly

---

## License

MIT
