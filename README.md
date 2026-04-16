# 🏥 Pharmacy App (Apollo-Inspired)

A full-stack pharmacy mobile application built for local medical stores to digitize medicine ordering, inventory management, and customer engagement.

---

## Features

### Customer App

* OTP-based login/signup
* Smart medicine search with autocomplete
* View medicine details (price, stock, substitutes)
* Add to cart & checkout
* Online payment (Razorpay) + Cash on Delivery
* Upload prescription
* Order tracking & history
* Notifications & offers

### Admin Dashboard

* Manage medicines & inventory
* Process and track orders
* Verify prescriptions
* Create coupons & offers
* View analytics (sales, users)

---

## Tech Stack

* **Mobile App:** React Native (Expo)
* **Backend:** FastAPI (Python)
* **Database:** PostgreSQL
* **Admin Panel:** React.js
* **Payments:** Razorpay
* **Notifications:** Firebase Cloud Messaging

---

## Project Structure

See folder structure below 👇

---

## Installation & Setup

### 🔹 1. Clone Repository

```bash
git clone https://github.com/ujjwalgaur/app.git
cd app
```

---

### 🔹 2. Backend Setup (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt

# Run server
uvicorn main:app --reload
```

Backend runs on: `http://127.0.0.1:8000`

---

### 🔹 3. Database Setup (PostgreSQL)

Create database:

```sql
CREATE DATABASE pharmacy_db;
```

Update `.env` in backend:

```
DATABASE_URL=postgresql://user:password@localhost/pharmacy_db
JWT_SECRET=your_secret_key
RAZORPAY_KEY=your_key
```

Run migrations (if using Alembic):

```bash
alembic upgrade head
```

---

### 🔹 4. Mobile App Setup (React Native)

```bash
cd mobile
npm install
npx expo start
```

Run on:

* Android Emulator / Device
* iOS Simulator

---

### 🔹 5. Admin Dashboard Setup

```bash
cd admin
npm install
npm start
```

---

### 🔹 6. Firebase Setup (Notifications)

* Create Firebase project
* Add config in mobile app
* Enable FCM

---

### 🔹 7. Razorpay Setup

* Create Razorpay account
* Add API keys in backend `.env`

---

##  Environment Variables

Create `.env` file in backend:

```
DATABASE_URL=
JWT_SECRET=
RAZORPAY_KEY=
RAZORPAY_SECRET=
```

---

##  API Endpoints (Sample)

* `POST /auth/login`
* `GET /medicines`
* `POST /cart`
* `POST /order`
* `POST /upload-prescription`
* `GET /admin/orders`

---

## Deployment

* Backend: AWS / Render / Railway
* Database: AWS RDS / Supabase
* Mobile App: Expo build / Play Store / App Store
* Admin Panel: Vercel / Netlify

---

## Future Enhancements

* AI-based medicine recommendations
* Subscription for monthly medicines
* Chat with pharmacist
* Delivery tracking system

---

## Contributing

Pull requests are welcome. For major changes, open an issue first.

---

##  License

MIT License


