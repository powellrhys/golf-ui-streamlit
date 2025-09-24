# golf-ui-streamlit

### Project Codebase

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Terraform](https://img.shields.io/badge/terraform-%235835CC.svg?style=for-the-badge&logo=terraform&logoColor=white)
![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![PowerShell](https://img.shields.io/badge/PowerShell-%235391FE.svg?style=for-the-badge&logo=powershell&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![Gherkin BDD](https://img.shields.io/badge/Gherkin%20BDD-darkgreen?style=for-the-badge&logo=cucumber&logoColor=white)

### Project Github Action Pipelines

![Collect Scorecard Data Status](https://github.com/powellrhys/golf-ui-streamlit/actions/workflows/collect-scorecard-data.yml/badge.svg)
![Collect Trackman Range Data Status](https://github.com/powellrhys/golf-ui-streamlit/actions/workflows/collect-trackman-range-data.yml/badge.svg)
![Build & Deploy](https://github.com/powellrhys/golf-ui-streamlit/actions/workflows/build-and-deploy.yml/badge.svg)

### Codebase Coverage

[![codecov](https://codecov.io/gh/powellrhys/golf-ui-streamlit/branch/main/graph/badge.svg?token=yNhANNzdtx)](https://codecov.io/gh/powellrhys/golf-ui-streamlit)
![GitHub issues](https://img.shields.io/github/issues/powellrhys/golf-ui-streamlit.svg)


### Codebase structure

```
golf-ui-streamlit
├── .github
│   └── workflows
├── backend
│   ├── functions
│   └── interfaces
├── frontend
│   ├── functions
│   └── pages
├── infra
├── shared
│   ├── functions
│   └── interfaces
└── tests
    ├── features
    ├── integration_tests
    └── unit_tests
```

## Overview

**golf-ui-streamlit** is a full-stack application designed to help golfers visualize and analyze their performance over time. It automatically collects data from scorecards and range sessions, stores it securely in the cloud, and provides interactive dashboards to explore your golfing stats.

- Collects individual golfing data from **Hole 19** (scorecards) and **Trackman** (range performance).  
- Automates data collection using **GitHub Actions** on a scheduled cron job.  
- Stores data in **Azure Blob Storage** for easy access and scalability.  
- Provides interactive visualizations via a **Streamlit** frontend.  
- Infrastructure is fully managed with **Terraform**, ensuring reproducibility and scalability.  

## Backend
- Python-based backend handles data ingestion, processing, and storage.  
- Integrates with Hole 19 and Trackman APIs to pull user-specific data.  
- Scheduled jobs run on GitHub Actions to keep the dataset up-to-date.  

## Frontend
- Built with **Streamlit** for quick, interactive dashboards.  
- Allows users to explore individual performance, plot trends, and analyze stats over time.

## Infrastructure
- Infrastructure-as-Code using **Terraform** located in the `infra/` directory.  
- Easily reproducible setup for deployment or migration.
- Azure cloud storage for secure and scalable data management.
- Azure app service for frontend distribution.

## Testing
- **Behavior-Driven Development (BDD)** feature tests for end-to-end workflows.  
- **Pytest** for unit and integration testing to ensure code reliability.  

## Deployment

The frontend application has been deployed to both streamlit cloud and to an azure app service. Both resources can be navigated to via the following urls:

- [Azure App Service Deployment](strava-streamlit-frontend.azurewebsites.net)
- [Streamllit Cloud Deployment](https://golf-frontend.streamlit.app/)

Due to the sensitive nature of the data, both applications are secured behind authentication, powered by oauth0. Renders of the application are illustrated below.

## Frontend Application

### Home Page
![Screenshot of Home Page](docs/assets/home_page.png?raw=true "Home Page")

### Trackman Club Analysis

![Screenshot of Trackman Club Analysis Page](docs/assets/trackman_club_analysis.png?raw=true "Trackman Club Analysis Page")

### Trackman Session Analysis

![Screenshot of Trackman Session Analysis Page](docs/assets/trackman_session_analysis.png?raw=true "Trackman Session Analysis Page")

### Trackman Yardages Analysis

![Screenshot of Trackman Yardages Analysis Page](docs/assets/trackman_yardages_analysis.png?raw=true "Trackman Yardages Analysis Page")

### Course Hole by Hole Analysis

![Screenshot of Course Hole by Hole Analysis Page](docs/assets/course_hole_by_hole_analysis.png?raw=true "Crouse Hole by Hole Analysis Page")

### Course Overview Analysis

![Screenshot of Course Overview Analysis Page](docs/assets/course_overview_analysis.png?raw=true "Crouse Overview Analysis Page")