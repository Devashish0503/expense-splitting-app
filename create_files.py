import os

def create_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

# Create run.py
create_file('run.py', """from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
""")

# Create .env
create_file('.env', """FLASK_APP=run.py
FLASK_DEBUG=1
DATABASE_URL=sqlite:///expenses.db
SECRET_KEY=your-dev-secret-key
""")

print("Files created successfully!")