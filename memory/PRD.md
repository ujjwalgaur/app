# RxOrder - Pharmacy Mobile Application PRD

## Product Overview
RxOrder is a production-ready mobile pharmacy application built for a local medical store serving 3000-4000 users. It enables medicine ordering, real-time inventory browsing, prescription handling, and complete order management.

## Tech Stack
- **Mobile App**: React Native (Expo) with expo-router file-based navigation
- **Backend**: FastAPI (Python)
- **Database**: MongoDB (with Motor async driver)
- **State Management**: Zustand (cart), React Context (auth)
- **Authentication**: JWT + Phone OTP (mock for development)
- **Navigation**: expo-router with bottom tabs + stack navigation

## Architecture
```
Frontend (Expo/React Native)
    ├── Auth Context (JWT persistence via AsyncStorage)
    ├── Cart Store (Zustand global state)
    ├── Tab Navigation (Home, Search, Cart, Orders, Profile)
    └── Stack Navigation (Medicine Detail, Checkout, Order Success)

Backend (FastAPI)
    ├── Auth Module (Phone OTP + JWT)
    ├── Medicine Module (CRUD, Search, Filters)
    ├── Cart Module (Per-user cart management)
    ├── Order Module (Creation, Tracking, Status)
    ├── Prescription Module (Upload, Verification)
    └── Admin Module (Dashboard, Inventory, Orders)

Database (MongoDB)
    ├── users
    ├── medicines
    ├── carts
    ├── orders
    └── prescriptions
```

## Features Implemented (Phase 1 MVP)

### Customer Features
1. **Phone OTP Login** - Mock OTP authentication with JWT persistence
2. **Medicine Discovery** - Grid view, category filters, search
3. **Medicine Details** - Composition, usage, substitutes, pricing
4. **Cart Management** - Add/remove/update quantities
5. **Checkout** - Delivery address, COD/Online payment
6. **Order Tracking** - Status updates (placed → delivered)
7. **Profile Management** - Name, email, phone

### Admin Features (API-only)
1. **Dashboard Stats** - Revenue, orders, users, inventory
2. **Order Management** - View all, update status
3. **Inventory CRUD** - Add/edit/delete medicines
4. **Prescription Review** - Verify/reject prescriptions

## API Endpoints
- Auth: `/api/auth/send-otp`, `/api/auth/verify-otp`, `/api/auth/me`
- Medicines: `/api/medicines`, `/api/medicines/{id}`, `/api/categories`
- Cart: `/api/cart`, `/api/cart/add`, `/api/cart/update/{id}`, `/api/cart/clear`
- Orders: `/api/orders`, `/api/orders/{id}`
- Prescriptions: `/api/prescriptions`
- Admin: `/api/admin/login`, `/api/admin/dashboard`, `/api/admin/orders`, `/api/admin/medicines`

## Database Seed Data
10 medicines across 5 categories (Tablets, Syrups, Antibiotics, Supplements, Antihistamines) with substitutes, pricing, and prescription requirements.

## Future Phases
- **Phase 2**: Razorpay payment integration, enhanced prescription UI, push notifications (FCM)
- **Phase 3**: Web admin dashboard (React.js), AI medicine recommendations, refill reminders
- **Phase 4**: Chat with pharmacist, voice search, subscription service

## Business Enhancement
- **Subscription Model**: Monthly medicine subscription at discounted rates for recurring medicines (diabetes, BP, etc.) - potential recurring revenue of ₹200-500/subscriber/month
- **Referral Program**: Existing users refer new users for ₹50 credit each
- **Health Tips & Content**: In-app health content to increase engagement and reduce churn

## Deployment
- Backend: FastAPI on port 8001
- Frontend: Expo with tunnel on port 3000
- Database: MongoDB on localhost:27017
