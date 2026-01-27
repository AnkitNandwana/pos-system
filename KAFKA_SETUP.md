# Kafka Setup Guide

## Option 1: Docker (Recommended - Easiest)

### 1. Install Docker
- Download from: https://www.docker.com/products/docker-desktop

### 2. Start Kafka
```bash
cd /home/ankit/projects/personal/pos-system
docker-compose up -d
```

### 3. Verify Kafka is Running
```bash
docker ps
```
You should see:
- cp-zookeeper
- cp-kafka

### 4. Create Kafka Topic
```bash
docker exec -it $(docker ps -q -f name=kafka) kafka-topics --create --topic pos-events --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

### 5. Stop Kafka (when done)
```bash
docker-compose down
```

---

## Option 2: Manual Installation (Linux/Mac)

### 1. Download Kafka
```bash
cd ~
wget https://downloads.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz
tar -xzf kafka_2.13-3.6.0.tgz
cd kafka_2.13-3.6.0
```

### 2. Start Zookeeper (Terminal 1)
```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
```

### 3. Start Kafka (Terminal 2)
```bash
bin/kafka-server-start.sh config/server.properties
```

### 4. Create Topic (Terminal 3)
```bash
bin/kafka-topics.sh --create --topic pos-events --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

### 5. Verify Topic Created
```bash
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

---

## Testing Kafka Setup

### Test Producer (send test message)
```bash
# Docker
docker exec -it $(docker ps -q -f name=kafka) kafka-console-producer --topic pos-events --bootstrap-server localhost:9092

# Manual
bin/kafka-console-producer.sh --topic pos-events --bootstrap-server localhost:9092
```
Type: `{"test": "message"}` and press Enter

### Test Consumer (receive messages)
```bash
# Docker
docker exec -it $(docker ps -q -f name=kafka) kafka-console-consumer --topic pos-events --bootstrap-server localhost:9092 --from-beginning

# Manual
bin/kafka-console-consumer.sh --topic pos-events --bootstrap-server localhost:9092 --from-beginning
```

---

## Complete Setup Flow

### Terminal 1: Start Kafka
```bash
# Using Docker (recommended)
cd /home/ankit/projects/personal/pos-system
docker-compose up

# OR Manual
cd ~/kafka_2.13-3.6.0
bin/zookeeper-server-start.sh config/zookeeper.properties
```

### Terminal 2: Start Kafka Server (if manual)
```bash
cd ~/kafka_2.13-3.6.0
bin/kafka-server-start.sh config/server.properties
```

### Terminal 3: Create Topic (one-time)
```bash
# Docker
docker exec -it $(docker ps -q -f name=kafka) kafka-topics --create --topic pos-events --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# Manual
cd ~/kafka_2.13-3.6.0
bin/kafka-topics.sh --create --topic pos-events --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

### Terminal 4: Start Django Kafka Consumer
```bash
cd /home/ankit/projects/personal/pos-system/backend
python manage.py consume_events
```

### Terminal 5: Start Django Server
```bash
cd /home/ankit/projects/personal/pos-system/backend
python manage.py runserver
```

---

## Verify Everything Works

### 1. Check Kafka is Running
```bash
# Docker
docker ps

# Manual
ps aux | grep kafka
```

### 2. Test with GraphQL
Open: http://localhost:8000/graphql/

```graphql
mutation {
  login(username: "john", password: "password123") {
    token
    terminal { terminalId }
  }
}
```

### 3. Check Consumer Terminal
You should see:
```
Kafka consumer started...
Received event: EMPLOYEE_LOGIN
Plugin employee_time_tracker handled event EMPLOYEE_LOGIN
```

---

## Troubleshooting

### Issue: "NoBrokersAvailable"
- Kafka not running
- Check: `docker ps` or `ps aux | grep kafka`
- Restart: `docker-compose restart` or restart Kafka manually

### Issue: "Topic does not exist"
- Create topic: See "Create Topic" section above

### Issue: Consumer not receiving events
- Check Kafka is running
- Check topic exists: `docker exec -it $(docker ps -q -f name=kafka) kafka-topics --list --bootstrap-server localhost:9092`
- Restart consumer: `python manage.py consume_events`

### Issue: Connection refused
- Check KAFKA_BOOTSTRAP_SERVERS in .env is `localhost:9092`
- Check Kafka port 9092 is not blocked

---

## Quick Commands Reference

```bash
# Start Kafka (Docker)
docker-compose up -d

# Stop Kafka (Docker)
docker-compose down

# View Kafka logs
docker-compose logs -f kafka

# List topics
docker exec -it $(docker ps -q -f name=kafka) kafka-topics --list --bootstrap-server localhost:9092

# Delete topic (if needed)
docker exec -it $(docker ps -q -f name=kafka) kafka-topics --delete --topic pos-events --bootstrap-server localhost:9092

# View messages in topic
docker exec -it $(docker ps -q -f name=kafka) kafka-console-consumer --topic pos-events --bootstrap-server localhost:9092 --from-beginning
```

---

## Recommended: Use Docker

Docker is the easiest way to run Kafka locally:

1. Install Docker Desktop
2. Run: `docker-compose up -d`
3. Create topic (one-time)
4. Start Django consumer
5. Start Django server
6. Test!

That's it! No manual Kafka installation needed.
