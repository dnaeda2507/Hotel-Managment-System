# AI Agent Planning Document

## AI Hotel PMS - Multi-Agent System

---

## 1. Project Overview

**Project Name:** AI Hotel PMS (Property Management System)

**Purpose:** A comprehensive hotel management system with AI-powered multi-agent automation for enhanced guest services and operational efficiency.

---

## 2. AI Agents Concept

### Agent 1: Guest Feedback Analyzer

**Problem:** Guest reviews are manually analyzed, causing delayed response to issues.

**Solution:** NLP-based keyword extraction from reviews automatically routes issues to appropriate departments.

**Keywords:**
| Keyword | Action |
|---------|--------|
| dirty, messy | → Housekeeping request |
| broken, malfunction | → Maintenance request |
| noise, loud | → Front desk notification |
| slow service | → Manager alert |
| excellent, amazing | → Positive feedback log |

---

### Agent 2: Dynamic Pricing Agent (Orchestrator)

**Problem:** Room prices are manually updated and don't reflect real-time events, weather, or occupancy.

**Solution:** This agent coordinates multiple sub-agents to calculate optimal pricing:

```
Dynamic Pricing Agent (Main Orchestrator)
    ├── Event Research Agent → City events, concerts, sports
    ├── Weather Agent → Weather conditions
    └── Occupancy Agent → Current room availability
```

**Pricing Factors:**
| Factor | Price Effect |
|--------|--------------|
| Concert/Festival | +30-50% |
| Marathon/Sports Event | +20% |
| New Year's Eve | +40% |
| Weekend | +15-25% |
| Rainy Weather | -10% |
| Low Occupancy | -10-20% |
| Holiday Season | +25% |

---

### Agent 3: Analytics Agent

**Problem:** Manual reporting takes significant time and lacks real-time insights.

**Solution:**

- Automatic report generation
- Occupancy analysis
- Revenue tracking
- Guest preference patterns
- Performance dashboards

---

## 3. System Architecture

```
                    +------------------+
                    |   Admin Panel    |
                    |  (React + TS)    |
                    +--------+---------+
                             |
                             v
+------------------------------------------------------------+
|                    BACKEND (FastAPI)                        |
|  Rooms | Bookings | Maintenance | Housekeeping | Pricing   |
+---------------------------+--------------------------------+
                            |
                            v
+------------------------------------------------------------+
|                   AI AGENT LAYER                           |
|                                                            |
|  +------------------+    +------------------+               |
|  |   Guest         |    |    Dynamic       |               |
|  |   Feedback      |    |    Pricing       |               |
|  |   Analyzer      |    |    Orchestrator  |               |
|  +------------------+    +--------+---------+               |
|                                   |                        |
|         +-------------+----+-------+-------+-----+          |
|         |             |    |       |       |     |          |
|         v             v    v       v       v     v          |
|  +----------+  +----------+ +----------+ +----------+        |
|  | Event    |  | Weather  | |Occupancy| | Report   |        |
|  | Research |  |  Agent   | |  Agent  | |  Agent   |        |
|  |  Agent   |  |          | |         | |          |        |
|  +----------+  +----------+ +----------+ +----------+        |
|       |            |          |            |                   |
|       v            v          v            v                   |
|  +----------+  +----------+ +----------+ +----------+        |
|  | Event    |  | Weather  | | Room DB  | |Database  |        |
|  |   API    |  |   API    | |  Query   | |  Query   |        |
|  +----------+  +----------+ +----------+ +----------+        |
+------------------------------------------------------------+
```

---

## 4. Agent Details

### 4.1 Dynamic Pricing Orchestrator

This is the main agent that coordinates sub-agents:

### 4.2 Sub-Agents

| Agent                | Responsibility                         | Data Source                           |
| -------------------- | -------------------------------------- | ------------------------------------- |
| Event Research Agent | Research city events, concerts, sports | Event APIs (Ticketmaster, Eventbrite) |
| Weather Agent        | Check weather forecast                 | Weather API (OpenWeatherMap)          |
| Occupancy Agent      | Get current room availability          | Database queries                      |
| Report Agent         | Generate analytics reports             | Database aggregation                  |

---

## 5. Implementation Plan

### Phase 1: Guest Feedback Analyzer

- Keyword detection system
- Automatic task creation
- Sentiment analysis
- Dashboard for managers

### Phase 2: Dynamic Pricing + Sub-Agents

- Event Agent API integration
- Weather Agent API integration
- Occupancy Agent database queries
- Orchestrator logic
- Price recommendation UI

### Phase 3: Analytics

- Report templates
- Real-time dashboards
- Export functionality
- Trend analysis

---

## 6. API Integration Points

| API                      | Purpose                | Data Flow                    |
| ------------------------ | ---------------------- | ---------------------------- |
| **Room API**             | Check availability     | Agent → Backend → Database   |
| **Booking API**          | Reservation management | Agent → Backend → Database   |
| **Event API**            | City events data       | Event Agent → External API   |
| **Weather API**          | Weather forecasts      | Weather Agent → External API |
| **Notification Service** | Alert staff/guests     | Agent → Backend → Push/SMS   |

---

## 7. Conclusion

The Multi-Agent System will transform hotel operations by:

1. **Faster Response** - Automated issue detection and routing
2. **Optimal Pricing** - Real-time dynamic pricing based on multiple factors
3. **Better Insights** - Automated analytics and reporting
4. **Improved Guest Experience** - Proactive service and personalization

This AI agent system will be implemented in future homework assignments.


