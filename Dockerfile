# השתמש בתמונה רזה של Python
FROM python:3.11-slim

# הגדר את תיקיית העבודה
WORKDIR /app

# העתק קבצי requirements והתקן תלויות תחילה (כדי לשמור על cache)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# העתק את שאר הקבצים לפרויקט
COPY . .

# הרץ את Flask
CMD ["python", "app.py"]
