# Modern PySide6 Authentication Interface (Web2 + Web3-Ready)

A professional, dark-themed authentication template built with **PySide6**.

This UI bridges the gap between native desktop apps and modern web design. It ships
with a clean design system, proper focus/hover states, and support for both
traditional email login and Web3-style wallet buttons (e.g., Phantom).

![Screenshot](assets/preview.png)

> ⚠️ Don’t forget to capture a screenshot of the app, name it `preview.png`,
> and place it in the `assets/` folder.

---

## ✨ Features

- **Modern UI/UX**
  - Custom QSS theming (no default “Win95” look).
  - Card-style layout, proper spacing, and typography.

- **Hybrid Auth UI**
  - **Web2:** Email + password fields, validation hooks, forgot-password flow.
  - **Web3-Ready:** Dedicated “Google” and “Phantom” circular buttons you can wire
    to OAuth / wallet connect logic.

- **Interactive elements**
  - Password visibility toggle with hoverable eye icon.
  - Hover and focus states for inputs and buttons.
  - Inline error + success messages (e.g., invalid login, reset link sent).

- **Modular architecture**
  - `LoginPage` emits a `login_successful` signal with the username/email.
  - Easy to drop into an existing `QMainWindow` or stacked-widget app.
  - Backend-agnostic: you can plug in Firebase, Supabase, a custom API, Solana RPC, etc.

---

## 🧱 Tech Stack

- **Language:** Python 3.10+
- **GUI Framework:** [PySide6](https://doc.qt.io/qtforpython/)
- **Styling:** QSS (Qt Style Sheets)
- **Assets:** SVG + PNG icons in `assets/`

---

## 📦 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/YourUsername/modern-pyside6-auth.git
   cd modern-pyside6-auth
