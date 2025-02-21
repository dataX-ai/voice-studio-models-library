FROM pytorch/pytorch:2.6.0-cuda12.4-cudnn9-runtime

ENV ENV=prod

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt
# RUN apt-get -qq -y install espeak-ng > /dev/null 2>&1

COPY . .

# Create data directory
RUN mkdir /app/data
RUN mkdir /app/output

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
