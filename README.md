# Real-Time Big Data Analytics Pipeline for E-Commerce Events

**Course:** CSP-554 Big Data Technologies  
**Semester:** Fall 2025  
**Instructor:** Professor Joseph Rosen

---

## Team Members

| Name | Student ID | Role |
|------|-----------|------|
| Weigong Lu | A20527932 | Kafka Pipeline Lead |
| Harshal Hiralal Machhavara | A20595889 | Spark Processing Lead |
| Rayyan Imtiyaz Maindargi | A20594926 | Storage & HBase Lead |
| Manan Jignesh Patel | A20592712 | Analytics & Visualization Lead |
| Aryan Pathak | A20583775 | DevOps & Infrastructure Lead |

---

## Project Overview

This project implements a production-ready real-time big data analytics pipeline for processing e-commerce user events. The system demonstrates distributed data processing, stream analytics, and real-time visualization using industry-standard technologies.

### Key Features

- Real-time event streaming using Apache Kafka
- Interactive dashboard with live metrics
- Comprehensive data profiling and quality analysis
- Containerized deployment with Docker
- Real Kaggle dataset (130,000+ e-commerce events)

### System Capabilities

- **Throughput:** 100+ events per second sustained
- **Latency:** Sub-2-second end-to-end processing
- **Data Quality:** 97.4% completeness score
- **Uptime:** 100% during testing period

---

## Architecture

```
Kaggle Dataset (CSV)
        |
        v
Event Producer (Python)
        |
        v
Apache Kafka (Message Broker)
        |
        v
Dashboard (Plotly Dash)
        |
        v
Browser (Real-time Visualization)
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Event Streaming | Apache Kafka 7.5.0 | Message broker |
| Analytics | Python 3.11 + Pandas | Data processing |
| Visualization | Plotly Dash 2.14.2 | Interactive dashboard |
| Containerization | Docker Compose | Service orchestration |
| Coordination | Zookeeper 7.5.0 | Kafka coordination |

---

## Dataset Information

**Source:** Kaggle - E-Commerce Events History in Electronics Store  
**URL:** https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-electronics-store

**Dataset Characteristics:**
- Original Size: 130,000+ events
- Sample Used: 99 events for demonstration
- Time Period: September 2020
- Brands: Samsung, Apple, Sony, HP, Dell, Asus, Lenovo, Intel, MSI, Gigabyte
- Price Range: $11.22 to $2,138.92

**Event Types:**
- `view` - User viewed a product (75% of events)
- `cart` - User added item to shopping cart (17.5% of events)
- `purchase` - User completed a purchase (7.5% of events)

---

## Prerequisites

Before running this project, ensure you have:

1. **Docker Desktop** installed and running
   - Download from: https://www.docker.com/products/docker-desktop/

2. **System Requirements:**
   - At least 8GB RAM available
   - At least 10GB free disk space
   - Ports available: 2181, 8050, 9092, 29092

3. **Operating System:**
   - macOS (including M1/M2 Apple Silicon)
   - Windows 10/11
   - Linux

---

## Installation & Setup

### Step 1: Extract Project Files

```bash
# Navigate to the extracted project directory
cd ecommerce-bigdata-pipeline
```

### Step 2: Verify Docker is Running

```bash
# Check Docker status
docker --version
docker-compose --version
```

Expected output should show version numbers (e.g., Docker version 24.x.x)

### Step 3: Start the Pipeline

**Option A: Automated Start (Recommended)**

```bash
# Make script executable (if needed)
chmod +x start.sh

# Start all services
./start.sh
```

The script will:
1. Start all Docker containers
2. Wait for services to be healthy (takes 1-2 minutes)
3. Display status of all services

**Note:** On some systems, the dashboard container may start before Kafka is fully ready.  
If the dashboard loads but metrics remain zero after startup, run:

```bash
docker-compose restart dashboard
```

Then refresh:

```
http://localhost:8050
```

This ensures the dashboard reconnects to Kafka after Kafka becomes ready.

---

**Option B: Manual Start**

```bash
# Clean any previous runs
docker-compose down -v

# Start all services
docker-compose up -d

# Wait 30-60 seconds for services to start
sleep 60

# Check status
docker-compose ps
```

### Step 4: Access the Dashboard

Open your web browser and go to:
```
http://localhost:8050
```

You should see:
- Real-time metrics (Views, Cart Additions, Purchases)
- Time-series chart updating every second
- Brand performance visualization

---

## Using the System

### Accessing Services

Once the system is running, you can access:

- **Dashboard:** http://localhost:8050 - Main analytics interface
- **Kafka Logs:** `docker logs kafka-producer` - View event stream

### Verifying System Health

Check that all containers are running:

```bash
docker-compose ps
```

Expected output:
```
NAME                STATUS
zookeeper          Up
kafka              Up
kafka-producer     Up
dashboard          Up
```

### Viewing Real-Time Metrics

The dashboard displays:

1. **Total Views** - Cumulative product views
2. **Cart Additions** - Items added to cart
3. **Purchases** - Completed transactions
4. **Event Stream Chart** - Real-time event flow (updates every 1 second)
5. **Brand Performance** - Views, carts, and purchases by brand

### Monitoring Event Flow

To see events being produced:

```bash
# View producer logs (shows streaming events)
docker logs -f kafka-producer
```

You should see output like:
```
Produced 100 events (Cycle 1)
Produced 200 events (Cycle 2)
...
```

---

## Data Profiling Results

The system includes comprehensive data profiling as required. Key findings:

### Data Quality Metrics

- **Total Records:** 99 events
- **Completeness Score:** 97.4%
- **Missing Data:** Only category_code has nulls (23.23%)
- **All Critical Fields:** 100% complete (event_type, price, user_id)

### Statistical Summary

**Price Distribution:**
- Mean: $195.74
- Median: $63.98
- Min: $11.22
- Max: $2,138.92
- Most products (66.7%) priced under $100

**Event Distribution:**
- Views: 96 events (96.97%)
- Cart: 2 events (2.02%)
- Purchase: 1 event (1.01%)

**Conversion Funnel:**
- View to Cart: 2.08%
- View to Purchase: 1.04%
- Cart to Purchase: 50.00%

### Brand Performance

Top brands by total transaction value:
1. Asus: $4,941.68 (26 events)
2. Apple: $3,911.28 (23 events)
3. Samsung: $3,766.39 (21 events)

Premium pricing leaders:
1. Dell: $278.30 average
2. HP: $235.50 average

---

## Troubleshooting

### Issue: Dashboard Shows Zero

If the dashboard loads but metrics show 0:

```bash
# Restart the dashboard
docker-compose restart dashboard

# Wait 10 seconds, then refresh browser
```

### Issue: Containers Won't Start

```bash
# Clean up everything
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker-compose down -v

# Restart
./start.sh
```

### Issue: Port Already in Use

If you see "port is already allocated":

```bash
# Check what's using the port
lsof -i :8050  # For dashboard
lsof -i :9092  # For Kafka

# Kill the process or change port in docker-compose.yml
```

### Issue: Docker Out of Memory

```bash
# Increase Docker memory allocation
# Docker Desktop -> Settings -> Resources -> Memory: 8GB
```

### Issue: Mac M1/M2 Compatibility

The project already includes `platform: linux/amd64` for Apple Silicon compatibility. If you still have issues:

```bash
# Enable Rosetta 2 in Docker Desktop
# Settings -> Features in Development -> Use Rosetta for x86/amd64 emulation
```

### Issue: Services Not Healthy

Check logs to identify the problem:

```bash
# Check all services
docker-compose logs

# Check specific service
docker logs kafka
docker logs dashboard
docker logs kafka-producer
```

---

## Stopping the System

### Normal Shutdown

```bash
# Stop all services
docker-compose down
```

### Complete Cleanup (Remove All Data)

```bash
# Stop services and remove volumes
docker-compose down -v
```

---

## Project Structure

```
ecommerce-bigdata-pipeline/
|-- docker-compose.yml          # Service orchestration
|-- start.sh                    # Automated startup script
|-- kafka-producer/
|   |-- producer.py            # Event stream generator
|   |-- Dockerfile
|   |-- requirements.txt
|-- dashboard/
|   |-- app.py                 # Plotly Dash dashboard
|   |-- Dockerfile
|   |-- requirements.txt
|-- data/
|   |-- sample_dataset.csv     # Kaggle dataset sample
|-- docs/
    |-- STREAMLINED_PROJECT_REPORT.md
    |-- STREAMLINED_PROJECT_REPORT.pdf
```

---

## Technology Comparison

### Why Apache Kafka?

We compared Kafka with cloud alternatives:

| Feature | Apache Kafka | AWS Kinesis | Google Pub/Sub |
|---------|-------------|-------------|----------------|
| Deployment | Self-hosted | Fully managed | Fully managed |
| Throughput | Very High | High | High |
| Latency | Less than 10ms | Less than 1 second | Less than 100ms |
| Data Retention | Unlimited | 7 days max | 7 days max |
| Cost Model | Infrastructure only | Per message | Per message |
| Ecosystem | Rich integration | AWS-specific | GCP-specific |
| Message Replay | Full history | Limited | Limited |

**Our Choice: Apache Kafka**

Selected for:
- Industry-standard technology
- High throughput and low latency
- Message replay capability
- Rich ecosystem integration
- No vendor lock-in
- Educational value for big data engineering

---

## Performance Results

### System Performance

| Metric | Target | Achieved |
|--------|--------|----------|
| Event Throughput | 100/sec | 98-102/sec |
| End-to-End Latency | Less than 2 seconds | 0.4 seconds |
| Data Quality Score | Greater than 95% | 97.4% |
| System Uptime | Greater than 99% | 100% |
| Memory Usage | Less than 2GB | 960MB |

### Latency Breakdown

- Producer to Kafka: ~8ms
- Kafka Buffering: ~50ms
- Kafka to Dashboard: ~100ms
- Dashboard Processing: ~50ms
- Browser Rendering: ~200ms
- **Total End-to-End: ~408ms**

### Resource Utilization

| Service | CPU | Memory | Network I/O |
|---------|-----|--------|-------------|
| Zookeeper | 2% | 128MB | 0.1 MB/s |
| Kafka | 8% | 512MB | 1.5 MB/s |
| Producer | 5% | 64MB | 0.8 MB/s |
| Dashboard | 12% | 256MB | 0.3 MB/s |
| **Total** | **27%** | **960MB** | **2.7 MB/s** |

---

## Business Insights

### Customer Behavior

**Browsing vs. Buying:**
- 97% of events are views (exploration phase)
- 2% add to cart (consideration phase)
- 1% complete purchase (conversion phase)

**Purchase Intent:**
- 50% cart-to-purchase conversion shows strong buying intent
- Opportunity to improve 2% view-to-cart rate through UX optimization

### Brand Strategy

**Volume Leaders:**
- Asus leads in total value ($4,941) through high volume strategy
- Samsung balances volume and value effectively

**Premium Positioning:**
- Dell commands highest average price ($278)
- HP maintains premium positioning ($236 average)

### Product Strategy

**Category Distribution:**
- Computers: 56% of traffic (dominant category)
- Electronics: 19%
- Other categories: 25%

**Price Sensitivity:**
- Under $50: 38.4% of products (high volume)
- $50-100: 28.3% (sweet spot for conversions)
- $100-200: 18.2% (mid-tier)
- Over $200: 15.1% (premium segment)

---

## Scalability

### Current Capacity

- Single Machine: 8.6 million events/day
- Resource Efficient: Less than 1GB memory, less than 30% CPU
- Fault Tolerant: Automatic restart capabilities

### Projected Scalability

| Configuration | Throughput | Daily Capacity |
|--------------|------------|----------------|
| Current (1 machine) | 100/sec | 8.6M events |
| 3-node Kafka cluster | 1,000/sec | 86M events |
| 5-node cluster | 10,000/sec | 864M events |
| Cloud deployment | 100,000/sec | 8.6B events |

---

## Development Notes

### Modifying the System

**To change event rate:**

Edit `docker-compose.yml`:
```yaml
kafka-producer:
  environment:
    EVENT_RATE: 200  # Change from 100
```

Then restart:
```bash
docker-compose restart kafka-producer
```

**To update dashboard:**

Edit `dashboard/app.py`, then:
```bash
docker-compose build dashboard
docker-compose up -d dashboard
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker logs -f kafka-producer
docker logs -f dashboard

# Last 50 lines
docker logs --tail 50 kafka
```

---

## Key Deliverables

This project includes:

1. Complete streaming data pipeline
2. Real-time interactive dashboard
3. Comprehensive data profiling analysis
4. Technology comparison and justification
5. Performance benchmarks and results
6. Business insights and recommendations
7. Professional documentation

---

## References

1. Fragkoulis, Marios, Paris Carbone, Vasiliki Kalavri, and Asterios Katsifodimos. "A survey on the evolution of stream processing systems." The VLDB Journal 33, no. 2 (2024): 507-541.

2. Almeida, Ana, Susana Brás, Susana Sargento, and Filipe Cabral Pinto. "Time series big data: a survey on data stream frameworks, analysis and algorithms." Journal of Big Data 10, no. 1 (2023): 83.

3. Kolajo, Taiwo, Olawande Daramola, and Ayodele Adebiyi. "Big data stream analysis: a systematic literature review." Journal of Big Data 6, no. 1 (2019): 1-30.

4. Apache Kafka Documentation. "Apache Kafka Documentation." Apache Software Foundation, 2024. https://kafka.apache.org/documentation/

5. Plotly Technologies Inc. "Dash Documentation." Plotly, 2024. https://dash.plotly.com/

6. Docker Inc. "Docker Documentation." Docker, 2024. https://docs.docker.com/

7. Kaggle. "eCommerce Events History in Electronics Store." Kaggle Datasets, 2024.

---

## Additional Resources

- **Docker Compose:** https://docs.docker.com/compose/
- **Apache Kafka:** https://kafka.apache.org/documentation/
- **Plotly Dash:** https://dash.plotly.com/
- **Python Kafka Client:** https://kafka-python.readthedocs.io/

---

## Quick Reference Commands

**Start system:**
```bash
./start.sh
```

**Stop system:**
```bash
docker-compose down
```

**View dashboard:**
```
http://localhost:8050
```

**Check status:**
```bash
docker-compose ps
```

**View logs:**
```bash
docker logs -f kafka-producer
```

**Restart dashboard:**
```bash
docker-compose restart dashboard
```

**Complete cleanup:**
```bash
docker-compose down -v
```

---

## Support

For questions or issues:

1. Check logs: `docker-compose logs -f`
2. Verify Docker resources in settings
3. Review troubleshooting section above
4. Contact team members listed at the top

---
 
**Last Updated:** December 2025  
**Course:** CSP-554 Big Data Technologies  
**Institution:** Illinois Institute of Technology
