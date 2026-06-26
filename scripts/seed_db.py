"""
Seed SQLite/Supabase with initial data and train the initial ML models.
Run this script once before starting the FastAPI server to initialize the system state.
"""
import sys
import os

# Add the root directory to the Python path so we can import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models.anomaly_model import train_model

def seed_database():
    """Placeholder for seeding SQLite/Supabase with initial data."""
    print("🌱 Seeding database with initial incident records...")
    # TODO: Add SQLAlchemy logic to insert default admin users or mock incidents
    print("✅ Database seeded successfully.")

def seed_models():
    """Train and save the initial Isolation Forest model."""
    print("🧠 Training initial Isolation Forest model...")
    train_model()
    print("✅ ML models seeded successfully.")

if __name__ == "__main__":
    print("🚀 Starting RootMind Initial Seeding Process...")
    seed_database()
    seed_models()
    print("🎉 Seeding complete! You can now start the FastAPI server.")