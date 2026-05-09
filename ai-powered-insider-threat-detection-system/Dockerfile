FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Ensure entrypoint script is executable
RUN chmod +x entrypoint.sh

# Expose Streamlit port
EXPOSE 8501

# Run entrypoint
ENTRYPOINT ["./entrypoint.sh"]
