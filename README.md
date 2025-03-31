# Tropical Vending Management System

A full-stack web application for managing a vending machine business, built with Django and Vue.js.

## Technology Stack

### Backend
- Django 4.2+
- Django REST Framework for API development
- SQLite (development) / PostgreSQL (production)
- SimpleJWT for authentication
- Whitenoise for static files serving

### Frontend
- Vue 3 with Composition API
- Vite as build tool
- Tailwind CSS for styling
- Pinia for state management
- Vue Router for navigation
- Chart.js and Vue-Chartjs for analytics visualizations
- Headless UI and Heroicons for UI components

## Project Structure

```
tropical-vending/
├── backend/
│   ├── core/                  # Main Django application
│   │   ├── migrations/        # Database migrations
│   │   ├── models/            # Database models
│   │   ├── serializers/       # API serializers
│   │   ├── views/             # API views
│   │   └── urls.py            # API URL routing
│   ├── media/                 # User-uploaded files
│   ├── static/                # Static files
│   ├── staticfiles/           # Collected static files for production
│   ├── templates/             # Django templates
│   ├── vendingapp/            # Django project settings
│   └── manage.py              # Django management script
├── frontend/
│   ├── src/
│   │   ├── assets/            # Static assets
│   │   ├── components/        # Vue components
│   │   ├── layouts/           # Page layouts
│   │   ├── router/            # Vue Router configuration
│   │   ├── store/             # Pinia stores
│   │   ├── views/             # Vue pages
│   │   ├── App.vue            # Root component
│   │   └── main.js            # Application entry
│   ├── index.html             # HTML template
│   └── package.json           # Frontend dependencies
└── .gitignore                 # Git ignore file
```

## Project Setup

### Prerequisites
- Python 3.9+ 
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the project directory:

```bash
cd tropical-vending
```

2. Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Run database migrations:

```bash
cd backend
python manage.py migrate
```

5. Create a superuser (admin):

```bash
python manage.py createsuperuser
```

6. Run the Django development server:

```bash
python manage.py runserver
```

The backend will be available at http://localhost:8000/

### Frontend Setup

1. Open a new terminal window and navigate to the frontend directory:

```bash
cd tropical-vending/frontend
```

2. Install JavaScript dependencies:

```bash
npm install
# or
yarn install
```

3. Run the development server:

```bash
npm run dev
# or
yarn dev
```

The frontend will be available at http://localhost:5173/

## Building for Production

### Build Frontend

```bash
cd tropical-vending/frontend
npm run build
# or
yarn build
```

This will create the production build in the `backend/static` directory, which will be served by Django.

### Collect Static Files

```bash
cd tropical-vending/backend
python manage.py collectstatic
```

## Deployment

### Environment Variables

In production, you'll need to set the following environment variables:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to `False` in production
- `DATABASE_URL`: PostgreSQL connection string
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

### Using Railway

This project is configured to deploy on Railway using the included Procfile.

## API Documentation

The API endpoints are available at:

- REST API: http://localhost:8000/api/
- Admin interface: http://localhost:8000/admin/

## Features

### User Management
- Secure authentication with JWT tokens
- Role-based access control
- User profile management

### Location and Machine Management
- Create and manage multiple vending machine locations
- Track individual machines with unique identifiers
- Assign machines to specific locations
- Configure machine types and capacities

### Product Management
- Comprehensive product catalog with images
- Product categorization
- Stock level tracking per product
- Price configuration per machine

### Inventory Operations
- Restock tracking with timestamps
- Stock movement history
- Low stock alerts
- Inventory reconciliation tools

### Wholesale Purchase Tracking
- Record wholesale product purchases
- Cost tracking for profitability analysis
- Vendor management
- Purchase history

### Analytics Dashboard
- Real-time stock level monitoring
- Product demand analysis
- Revenue and profit reporting
- Performance metrics by location and machine
- Visual data representation with charts

### Mobile Responsive Design
- Access the system from any device
- Optimized interface for both desktop and mobile
- Mobile-friendly data entry forms

## License

This project is licensed under the MIT License - see the LICENSE file for details. 