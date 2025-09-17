# 🗄️ Espionage Monitoring System - Data Storage Architecture

## Database Structure Overview

The 24/7 espionage monitoring system uses **SQLite** as its database with 4 main tables that work together to track nations and detect daily reset times.

```
📁 spy_bot.db (SQLite Database)
├── 🏛️ nations           (Basic nation info)
├── 🔍 espionage_status   (Historical status checks)
├── ⏰ reset_times        (Detected daily resets)
└── 📋 monitoring_queue   (Nations to check)
```

---

## 📊 Table Schemas & Data Flow

### 1. 🏛️ **nations** Table
**Purpose**: Store basic information about all alliance nations

```sql
CREATE TABLE nations (
    id INTEGER PRIMARY KEY,           -- Politics & War nation ID
    nation_name TEXT NOT NULL,        -- "Example Nation"
    leader_name TEXT,                 -- "Leader Name"
    alliance_id INTEGER,              -- Alliance ID (12345)
    alliance_name TEXT,               -- "Rose" / "TCM" etc.
    score REAL,                      -- Nation score (1500.25)
    cities INTEGER,                  -- Number of cities (10)
    last_updated TIMESTAMP,          -- When last updated
    is_active BOOLEAN DEFAULT 1      -- Still active (1/0)
)
```

**Sample Data**:
```
ID     | Nation Name    | Alliance | Score   | Cities | Active
123456 | Example Nation | Rose     | 1500.25 | 10     | 1
234567 | Test Nation    | TCM      | 2100.50 | 15     | 1
345678 | Demo Country   | NULL     | 800.75  | 5      | 0 (left alliance)
```

### 2. 🔍 **espionage_status** Table  
**Purpose**: Track espionage availability over time (historical log)

```sql
CREATE TABLE espionage_status (
    id INTEGER PRIMARY KEY,
    nation_id INTEGER,               -- Links to nations.id
    espionage_available BOOLEAN,     -- Can be spied on? (1/0)
    beige_turns INTEGER DEFAULT 0,   -- Beige protection left
    vacation_mode_turns INTEGER,     -- Vacation mode turns
    last_active TIMESTAMP,           -- Last seen active
    checked_at TIMESTAMP             -- When we checked
)
```

**Sample Data Timeline**:
```
Nation ID | Available | Beige | Vacation | Checked At
123456    | 0        | 72    | 0        | 2025-09-17 10:00:00
123456    | 0        | 48    | 0        | 2025-09-17 16:00:00
123456    | 1        | 0     | 0        | 2025-09-17 22:15:00  <- RESET DETECTED!
```

### 3. ⏰ **reset_times** Table
**Purpose**: Store detected daily reset times (the goal!)

```sql
CREATE TABLE reset_times (
    id INTEGER PRIMARY KEY,
    nation_id INTEGER,              -- Links to nations.id
    reset_time TIMESTAMP,           -- When reset occurred
    confidence_level REAL,          -- How confident (0.0-1.0)
    detection_method TEXT,          -- How we detected it
    verified BOOLEAN DEFAULT 0,     -- Manually verified?
    created_at TIMESTAMP            -- When we detected it
)
```

**Sample Data**:
```
Nation ID | Reset Time           | Method              | Confidence
123456    | 2025-09-17 22:15:00 | protection_to_available | 1.0
234567    | 2025-09-17 18:30:00 | protection_to_available | 1.0
345678    | 2025-09-17 14:45:00 | protection_to_available | 1.0
```

### 4. 📋 **monitoring_queue** Table
**Purpose**: Schedule which nations to check and when

```sql
CREATE TABLE monitoring_queue (
    id INTEGER PRIMARY KEY,
    nation_id INTEGER,              -- Nation to check
    reason TEXT,                    -- Why monitoring
    added_at TIMESTAMP,             -- When added to queue
    next_check TIMESTAMP,           -- When to check next
    priority INTEGER DEFAULT 1      -- Check priority
)
```

**Sample Data**:
```
Nation ID | Reason               | Next Check           | Priority
123456    | new_nation_monitoring| 2025-09-17 23:00:00 | 1
234567    | protection_detected  | 2025-09-17 22:30:00 | 2
345678    | status_change        | 2025-09-18 02:00:00 | 1
```

---

## 🔄 Data Flow Process

### **Phase 1: Nation Indexing**
```
API Query → All Nations Data → Filter Alliance Members → Store in 'nations' table
                             ↓
                    Add to 'monitoring_queue' (if no reset time found)
```

### **Phase 2: Monitoring Cycle**
```
monitoring_queue → Get nations ready to check → API Query Current Status
                                              ↓
                                    Store in 'espionage_status'
                                              ↓
                          Compare with last status → Status Change?
                                              ↓
                                   YES: Record in 'reset_times'
                                   NO:  Update 'next_check' time
```

### **Phase 3: Reset Detection**
```
Previous Status: espionage_available = FALSE (protected)
Current Status:  espionage_available = TRUE  (available)
                                ↓
                    RESET TIME DETECTED!
                                ↓
              Store in 'reset_times' + Remove from 'monitoring_queue'
```

---

## 📈 Storage Efficiency Features

### **Smart Filtering**
- ❌ **Vacation mode nations**: Skipped during indexing
- ❌ **Non-alliance nations**: Not stored at all  
- ❌ **Already found resets**: Removed from monitoring queue
- ✅ **Only alliance members**: Efficiently targeted

### **Automatic Cleanup**
- **Daily cleanup**: Removes completed nations from monitoring
- **Reset detection**: Auto-removes from queue when reset found
- **Inactive nations**: Marked as inactive, not deleted

### **Performance Indexes**
```sql
-- Fast alliance queries
CREATE INDEX idx_nation_alliance ON nations (alliance_id)

-- Fast espionage lookups  
CREATE INDEX idx_espionage_nation ON espionage_status (nation_id)

-- Fast time-based queries
CREATE INDEX idx_espionage_checked ON espionage_status (checked_at)

-- Fast reset time lookups
CREATE INDEX idx_reset_nation ON reset_times (nation_id)

-- Fast monitoring queue processing
CREATE INDEX idx_monitoring_next_check ON monitoring_queue (next_check)
```

---

## 💾 Storage Location

- **Database File**: `h:\Git\spyv2\database\spy_bot.db`
- **Format**: SQLite (single file, no server needed)
- **Size**: Grows as more nations/data collected
- **Backup**: Copy the `.db` file

---

## 🔍 How to View Stored Data

### **Check Database Stats**:
```python
from database.espionage_tracker import EspionageTracker
tracker = EspionageTracker()
stats = tracker.get_database_stats()
print(stats)
```

### **Discord Command**:
```
!monitor  # Shows current stats
```

### **Manual Database Access**:
```bash
# Install sqlite3 if needed
sqlite3 spy_bot.db

# View tables
.tables

# Check nation count
SELECT COUNT(*) FROM nations WHERE alliance_id IS NOT NULL;

# View recent reset detections
SELECT n.nation_name, rt.reset_time 
FROM reset_times rt 
JOIN nations n ON rt.nation_id = n.id 
ORDER BY rt.created_at DESC LIMIT 10;
```

---

## 🎯 Data Retention Strategy

### **What Gets Kept Forever**:
- ✅ **Nation basic info** (for historical reference)
- ✅ **Reset times** (the valuable data!)
- ✅ **Key status changes** (for analysis)

### **What Gets Cleaned Up**:
- 🧹 **Monitoring queue entries** (when reset found)
- 🧹 **Old espionage status** (keep recent only)
- 🧹 **Inactive nations** (marked inactive, not deleted)

This architecture ensures efficient storage while capturing all the critical intelligence data needed to track daily reset patterns across the Politics & War game!
