# TenshiGuard AI 🛡️

**Next-Generation AI-Powered Endpoint Security & Threat Detection System**

TenshiGuard is a comprehensive cybersecurity platform designed to protect organizations from advanced threats. It combines a lightweight endpoint agent with a powerful cloud-based dashboard and an AI-driven analysis engine to detect, correlate, and mitigate security incidents in real-time.

![Dashboard Preview](https://via.placeholder.com/800x400?text=TenshiGuard+Dashboard)

## 🚀 Key Features

### 1. **AI-Powered Threat Detection**
*   **Hybrid Analysis**: Combines signature-based detection with behavioral analysis using AI models.
*   **Real-time Scoring**: Assigns risk scores (0-100) to files, processes, and network events.
*   **Feedback Loop**: Admin feedback (True/False Positive) retrains the system to improve accuracy over time.

### 2. **Centralized Command Center**
*   **Live Dashboard**: Monitor device health, online status, and resource usage (CPU/RAM) in real-time.
*   **Threat Timeline**: Visualize attack chains and correlated events.
*   **Device Management**: Remote commands, isolation, and detailed telemetry for every endpoint.

### 3. **Intelligent Correlation Engine**
*   **Multi-Vector Analysis**: Links disparate events (e.g., a suspicious file download followed by a registry change) to identify complex attack patterns.
*   **Automated Incident Response**: Generates high-fidelity alerts and suggests mitigation steps.

### 4. **Multi-Tenancy & Security**
*   **Organization Isolation**: Strict data separation ensures one organization cannot access another's data.
*   **Role-Based Access Control (RBAC)**: Granular permissions for Admins and Users.
*   **Secure Communication**: All agent-server communication is encrypted and authenticated via unique tokens.

### 5. **Cross-Platform Agent**
*   **Windows Support**: Native PowerShell-based agent for deep system integration.
*   **Lightweight**: Minimal performance impact on host devices.
*   **Resilient**: Auto-recovery and offline caching capabilities.

## 🛠️ Tech Stack

*   **Backend**: Python, Flask, SQLAlchemy
*   **Database**: PostgreSQL (Production), SQLite (Dev)
*   **Frontend**: HTML5, Bootstrap 5, Vanilla JS, Chart.js
*   **AI/ML**: Scikit-learn (Random Forest), Custom Heuristics
*   **Agent**: Python / PowerShell

## 📦 Installation

### Prerequisites
*   Python 3.8+
*   Git

### Quick Start

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/TenshiGuard/TenshiGuard-Live.git
    cd TenshiGuard-Live
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Server**
    ```bash
    python run.py
    ```
    Access the dashboard at `http://localhost:5001`.

4.  **Deploy Agent**
    *   Go to **Dashboard > Setup Agent**.
    *   Copy the installation command.
    *   Run it on your target Windows machine (PowerShell as Admin).

For detailed deployment instructions, see [INSTALL.md](INSTALL.md).

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
