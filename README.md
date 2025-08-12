🧠 Recipe Intelligence Platform

A scalable, cloud-native app that analyzes and visualizes recipe data using PostgreSQL, Streamlit, and Python. Built for maintainability, automation, and clarity.

Features
- 🔍 Full-text search across recipes
- 📊 Streamlit UI for interactive exploration
- 🛠️ Modular Python backend with robust error handling
- ☁️ Cloud deployment via Render + Neon
- 🔄 Automated database migration and connection testing

⚙️ Setup Instructions
1. Clone the repo
git clone https://github.com/your-username/recipe-intelligence.git
cd recipe-intelligence

2. Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

3. Install dependencies
pip install -r requirements.txt

4. Configure environment
Create a .env file with your Neon DB credentials:
DB_URL=postgresql://username:password@host:port/dbname

🧪 Local Development
Run the app locally:
streamlit run app.py

Test database connection:
python utils/test_connection.py

☁️ Deployment Render Setup
- Create a new Web Service on Render
- Set build command: pip install -r requirements.txt
- Set start command: streamlit run app.py
- Add environment variables from .env
Neon Setup
- Create a Neon project and database
- Whitelist Render’s IP or use pooled connection
- Use connection string in .env

🧠 Future Enhancements
- 🧬 Vector search with pgvector
- 📈 Analytics dashboard
- 🔐 Role-based access control
- 🧪 CI/CD pipeline with GitHub Actions