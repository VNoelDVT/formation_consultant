# Devoteam Coach - PRINCE2 AI Demo

A standalone, visually stunning demo of the **Devoteam Coach** AI assistant for PRINCE2 certification training. This project is a frontend-only demonstration designed for client presentations.

## Key Features

- **Multi-Certification Support**: Choose between **PRINCE2** and **PMP** (Project Management Professional) tracks.
- **Gemini-Style UI**: Modern, dark-themed interface with glassmorphism and smooth animations.
- **Interactive Quiz**: A 5-question flow (PRINCE2 or PMP) with instant feedback.
- **Adaptive Learning**: Fails in **any** question trigger targeted, clickable exercise recommendations (e.g., Facts, Lectures) specific to the error.
- **Session Memory Mock**: Simulates a Google SSO login to "retrieve" historical progress.
- **PDF Reporting**: Generates a fast, printable HTML-based PDF report customized for the selected certification.

## How to Run

This is a single-file application. No server, Node.js, or backend is required.

1. **Locate the file**: `demo.html` in the root directory.
2. **Open in Browser**: Double-click the file or drag it into Chrome/Edge.
   - Or paste this path: `file:///c:/Dev/formation_consultant/demo.html`

## Demo Scenario Script

To showcase all features effectively, follow this script:

1. **Start**: Click **"Quiz rapide (5 questions)"**.
2. **The "Mistake"**: Answer questions 1-3 correctly, but **intentionally fail Question 4** (Select "Qualité" instead of "Cas d'Affaire").
3. **Adaptive Feedback**: Notice the specific "Lecture approfondie : Cas d'Affaire" exercise card appears.
4. **Interactive Exercise**: Click the exercise card to show the detailed reading view.
5. **PDF Generation**:
   - Scroll down and click **"📄 Générer mon résumé PDF"**.
   - Authenticate with the **Google** button (Mock SSO).
   - View the **"Rapport de progression"** dashboard.
   - Click **"📥 Télécharger le PDF complet"** to open the print view.

## Project Structure

- `demo.html`: Contains all HTML, CSS, and JavaScript. Zero external dependencies (except Fonts).
