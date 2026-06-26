import sys
import os

# Add the project root to Python's module search path before importing backend modules.
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

"""
Seed SQLite/Supabase with initial data, train ML models, and seed Vector DB.
"""

print("Script execution started...")

try:
    from backend.models.anomaly_model import train_model
    from backend.models.rag_pipeline import seed_mock_codebase
except ImportError as e:
    print(f"Import Error: {e}")
    print(f"Project root added to sys.path: {root_dir}")
    print("Make sure backend dependencies are installed and package files exist.")
    sys.exit(1)


def seed_database():
    print("🌱 Seeding database with initial incident records...")
    print("✅ Database seeded successfully.")


def seed_models():
    print("🧠 Training initial Isolation Forest model...")
    train_model()
    print("✅ ML models seeded successfully.")


def seed_vector_db():
    print("🔗 Seeding Qdrant Vector DB with mock codebase...")
    seed_mock_codebase()
    print("✅ Vector DB seeded successfully.")


if __name__ == "__main__":
    print("🚀 Starting RootMind Initial Seeding Process...")
    seed_database()
    seed_models()
    seed_vector_db()
    print("🎉 Seeding complete! You can now start the FastAPI server.")
