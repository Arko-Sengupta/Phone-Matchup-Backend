# Phone-Matchup

## Overview
Welcome to _**Phone Matchup**_! _**Phone Matchup**_ is a _**ETL Pipelines**_ designed to extract and Standardize _**Smart Phone**_ data. Whether you are a developer or contributor, this _**README.md**_ will guide you through the essentials of the project.

## Table of Content
1. [Introduction](#introduction)
2. [Application UI](#application-ui)
3. [Getting Started](#getting-started)
4. [Installation](#installation)
5. [Contribution](#contribution)

## Introduction
**Phone Matchup** crafts an advanced **ETL Pipeline** designed to efficiently **Extract**, **Standardize**, and meticulously **Process** Smart Phone Data, tailoring the results to suit the user's budget preferences and specific brand preferences, delivering a seamless experience.

## Application UI
![Screenshot 2024-10-14 165121](https://github.com/user-attachments/assets/bc912cb8-b94f-4888-9181-bdef0bf83bdb)
![Screenshot 2024-10-14 165036](https://github.com/user-attachments/assets/d4a8cda1-fcb4-4ac4-8278-153b77bc0055)

## Getting Started
Before diving into the project, ensure you have the following prerequisites:
- Programming Language: [Python 3.X](https://www.python.org/)
- Package Manager: [pip](https://pypi.org/project/pip/)
- Version Control: [Git](https://git-scm.com/)
- Integrated Development Environment: [Visual Studio Code](https://code.visualstudio.com/), [PyCharm](https://www.jetbrains.com/pycharm/)

## Installation
1. Clone Repository
   ```bash
   https://github.com/Arko-Sengupta/Phone-Matchup.git
   ```

2. Navigate to the Backend Directory
   ```bash
   cd backend
   ```

3. Install Dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Add your Tavily API Key to `.env`:
   ```bash
   TAVILY_API_KEY="<YOUR_TAVILY_API_KEY>"
   ```

5. Start Backend Server
   ```bash
   python ETLPipe_API.py
   ```

6. Confirm Server Start: Open the below URL at Browser: [http://localhost:5000/](http://localhost:5000/)

7. Start the Application (from repo root)
   ```bash
   streamlit run frontend/App.py
   ```

## Contribution
If you'd like to contribute, follow the guidelines
- Create a branch using the format `Phone-Matchup_<YourUsername>` when contributing to the project.
- Add the label `Contributor` to your contributions to distinguish them within the project.
