# Automated Microwave Scatterometer and Digital Twin

## Overview

This project implements an Automated Microwave Scatterometer with a cloud-based Digital Twin platform. The system enables fully unattended microwave scattering measurements using a PTZ-controlled antenna platform and a Vector Network Analyzer (VNA). Users can remotely configure measurement tasks, monitor execution, visualize results, and interact with a real-time 3D model through a web interface.

The system architecture consists of:

* Command Server (Render Cloud)
* Data Server (Render Cloud)
* Instrument Controller (Windows PC)
* PTZ Rotation Platform
* Vector Network Analyzer (VNA)
* Interactive Web Interface
* 3D Digital Twin Visualization

---

# Part I – User Guide

## 1. Accessing the Web Interface

Open the scatterometer web dashboard in a browser. **Website Address: https://render-a2mh.onrender.com (TO BE UPDATED)**

The interface contains three major sections:

### Control Panel

Used to submit measurement commands.

Parameters:

* **VRS (Vertical Rotation Steps)**

  * Range: 0°–180°
  * Increment: 10°

* **HRS (Horizontal Rotation Steps)**

  * Range: 0°–180°
  * Increment: 10°

* **Auto Shutdown**

  * ON: Automatically power off after measurement completion.
  * OFF: Remain active after measurement completion.

---

## 2. Starting a Measurement

1. Enter desired VRS value.
2. Enter desired HRS value.
3. Select Auto Shutdown option.
4. Click **Start Measurement**.

The command will be uploaded to the cloud Command Server and automatically downloaded by the instrument controller.

The uploaded command is available at https://render-er7w.onrender.com/data.

Example:

VRS = 40

HRS = 30

Auto Shutdown = OFF

This will perform measurements from (0°,0°) to (30°,40°) using the predefined angular step size.

---

## 3. Monitoring Progress

The measurement system automatically:

1. Downloads the command.
2. Rotates antennas to each angle position.
3. Performs S21 measurement.
4. Performs S11 measurement.
5. Saves measurement logs.
6. Uploads processed data to the cloud Data Server.

No user intervention is required once the task starts.

---

## 4. Viewing Measurement Data

The center panel displays:

### Command Parameters

* Commanded HRS
* Commanded VRS

### Measured Angles

* Actual H angle
* Actual V angle

### S-Parameter Data

* S11 Magnitude
* S21 Magnitude
* S11 Phase
* S21 Phase

### Frequency Response Plots

Two charts are generated automatically:

* S11 vs Frequency
* S21 vs Frequency

The displayed data updates automatically when new measurement results are uploaded.

Data is also available at https://render-a2mh.onrender.com/data.

---

## 5. Downloading Data

Click:

**Download Data**

The system exports all currently stored measurement records from the Data Server.

The downloaded file can be opened in:

* Excel
* MATLAB
* Python
* Origin

---

## 6. Clearing Data

Before starting a new experiment:

1. Verify that all previous data have been downloaded.
2. Click **Clear Data**.

This removes all stored measurement records from the Data Server and resets the dashboard.

---

## 7. Digital Twin Visualization

The right-side panel contains a 3D model of the scatterometer.

The model updates automatically according to:

* Current horizontal angle
* Current vertical angle

allowing users to remotely observe antenna orientation during operation.

---

# Part II – Developer Guide

## 1. System Architecture

The project uses a dual-cloud architecture.

Command Path:

User Interface
→ Command Server
→ Instrument Controller
→ Measurement Execution

Data Path:

Instrument Controller
→ Data Server
→ User Interface

Separating command and data channels improves reliability and prevents traffic contention.

---

## 2. Software Components

### Cloud Side

#### Command Server

Responsibilities:

* Receive measurement commands
* Store command file
* Provide download API

Typical files:

* main.py
* command.csv

---

#### Data Server

Responsibilities:

* Receive uploaded measurement data
* Store CSV records
* Provide data retrieval API
* Provide clear-data API
* Provide download-data API

Typical files:

* main.py
* data.csv

---

### Instrument Side

#### download.py

Downloads latest command file from Command Server.

---

#### toplevel1.py

Persistent daemon.

Responsibilities:

* Poll Command Server every few seconds
* Detect new commands
* Launch final.c

---

#### final.c

Core measurement program.

Responsibilities:

* Control PTZ platform
* Communicate with VNA
* Execute measurement grid
* Generate log files

Main parameters:

* vrs
* hrs
* shutdown flag

Example:

final.exe -vrs 40 -hrs 30

---

#### toplevel2.py

Persistent daemon.

Responsibilities:

* Monitor log directory
* Detect new measurement files
* Trigger data processing

---

#### trans.py

Converts raw logs into structured CSV format.

Output format:

Target_H,
Target_V,
H,
V,
Frequency_Hz,
S11_Mag_dB,
S11_Phase,
S21_Mag_dB,
S21_Phase

---

#### upload.py

Uploads processed CSV files to Data Server.

---

## 3. Deploying the Render Servers

### Step 1: Create Render Account

Create an account at:

https://render.com

---

### Step 2: Create Command Server

Create a new Web Service.

Repository:

GitHub → Command Server project

Runtime:

Python

Start Command:

uvicorn main:app --host 0.0.0.0 --port $PORT

Deploy.

Record URL:

Example from the provided code:

https://render-er7w.onrender.com

---

### Step 3: Create Data Server

Create another Web Service.

Repository:

GitHub → Data Server project

Runtime:

Python

Start Command:

uvicorn main:app --host 0.0.0.0 --port $PORT

Deploy.

Record URL:

Example from the provided code:

https://render-a2mh.onrender.com

---

## 4. Modifying Server Addresses

Update the URLs inside:

download.py

Example:

COMMAND_SERVER_URL = "https://your-command-server.onrender.com"

---

upload.py

Example:

DATA_SERVER_URL = "https://your-data-server.onrender.com"

---

Web Interface

Replace fetch() URLs with your deployed Render addresses.

Example:

fetch("https://your-data-server.onrender.com/data")

fetch("https://your-command-server.onrender.com/upload")

---

## 5. Running the Instrument Controller

Install Python:

Python 3.10+

Required packages:

pip install requests pandas

Run:

python toplevel1.py

python toplevel2.py

These processes should remain running continuously.

For production deployment, configure them as:

* Windows Services
  or
* Task Scheduler background tasks

---

## 6. Directory Structure

project/

├── final.c

├── download.py

├── upload.py

├── trans.py

├── toplevel1.py

├── toplevel2.py

├── log/

├── output.csv

├── templates/

│   └── index.html

└── static/

---

## 7. Changing Measurement Parameters

Frequency settings are defined in:

final.c

Key constants:

VNA_START_FREQ

VNA_STOP_FREQ

VNA_NOP

Example:

Start Frequency = 5 GHz

Stop Frequency = 8 GHz

Points = 25

To modify:

1. Edit constants.
2. Recompile final.c.
3. Replace executable.

---

## 8. Adding New Features

Recommended future improvements:

### Reliability

* Add watchdog process
* Automatic daemon restart

### Data Processing

* Support phase calibration
* Support complex S-parameters

### Cloud Infrastructure

* Database backend (PostgreSQL)
* User authentication
* Experiment history management

### Instrumentation

* Soil moisture sensor integration
* Temperature sensor integration
* Weather station integration

---

## Troubleshooting

### No Measurement Starts

Check:

* Command Server reachable
* toplevel1.py running
* Command file updated

### No Data Appears

Check:

* final.c generated logs
* trans.py generated output.csv
* upload.py successfully uploaded data

### Web Dashboard Empty

Check:

* Data Server URL
* Browser developer console
* Render service status

### 3D Model Not Updating

Check:

* Latest H/V values uploaded
* Frontend fetch interval
* Three.js rendering errors

---

For technical questions, refer to:

* final.c (measurement execution)
* toplevel1.py (command orchestration)
* toplevel2.py (data processing)
* Render deployment settings
* VNA communication configuration
