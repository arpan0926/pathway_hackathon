FROM pathwaycom/pathway:latest

WORKDIR /app

# Install Groq for RAG bot
RUN pip install groq

# Copy files
COPY pipeline.py .
COPY rag_bot.py .
COPY prompts.py .

# Default command (can be overridden in docker-compose)
CMD ["python", "pipeline.py"]