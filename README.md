# West Bengal 2026 Exit Poll Prediction System

### Statistical Exit-Poll Calibration + AI-Assisted Forecast

A **demo/academic project** that combines historical exit-poll performance, current exit-poll estimates, statistical bias correction, uncertainty estimation, and manual ChatGPT sentiment analysis to generate an AI-assisted forecast for the **2026 West Bengal Assembly Election**.

## 🔄 Workflow

```text
Historical Exit Polls
        ↓
Historical Bias Analysis
        ↓
Current Exit Poll Dataset
        ↓
Statistical Calibration
        ↓
Seat Estimate + Prediction Range
        ↓
ChatGPT Sentiment Analysis
        ↓
Capped AI Adjustment
        ↓
Final Forecast
```

## ⚙️ How It Works

1. Loads historical exit-poll data from **2011, 2016 and 2021**.
2. Calculates historical polling errors and bias profiles.
3. Takes a selected current exit-poll dataset.
4. Calculates mean, median, spread and agency variation.
5. Applies historical bias correction to the current poll median.
6. Generates a statistical prediction range.
7. Generates a poll-agreement/confidence indicator.
8. Generates a structured prompt for ChatGPT.
9. User manually provides sentiment scores in JSON format.
10. The system applies a **capped AI adjustment** and produces the final forecast.

## ✅ Currently Working

* Historical polling analysis
* Bias correction
* Current exit-poll processing
* Statistical seat prediction
* Prediction intervals
* Poll-agreement indicator
* 294-seat normalization
* Winner & majority estimation
* ChatGPT prompt generation
* Manual AI sentiment integration
* AI-adjusted final forecast
* FastAPI backend
* Interactive web dashboard

## 🚧 Current Limitations

This is a **functional demonstration**, not a production election forecasting system.

Currently **not implemented**:

* True supervised ML model
* Constituency-level prediction
* Monte Carlo simulation
* Real-time news collection
* Automated LLM/API integration
* GIS/geospatial forecasting
* Demographic modeling
* Pollster-specific ML
* Extensive historical backtesting

The displayed confidence value is **not a probability of winning**, and the AI-to-seat adjustment is a heuristic rather than a scientifically validated relationship.

## 🧠 Technology

**Backend:** Python, FastAPI, Pandas, NumPy, SciPy
**Frontend:** HTML, CSS, JavaScript
**Data:** CSV
**AI:** Manual ChatGPT integration

## 🎯 What It Achieves

The project demonstrates how:

> **Historical polling behavior + current exit polls + statistical calibration + qualitative AI sentiment**

can be combined into an interactive election forecasting workflow.

It is primarily intended to demonstrate **statistical modeling, uncertainty analysis, human-in-the-loop AI, and full-stack application development**.

## 🔮 Future Scope

Future versions can include:

```text
Constituency-level ML
        ↓
Monte Carlo simulation
        ↓
Real-time news & sentiment
        ↓
Pollster-specific modeling
        ↓
Historical backtesting
        ↓
Probability-based election forecasting
```

## ⚠️ Disclaimer

This is an **educational/demo project** and is not an official election forecast. Results depend on the supplied polling data, assumptions, statistical methodology, and manually provided AI sentiment.
