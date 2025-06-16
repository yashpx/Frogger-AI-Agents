## 🧠 AI-Driven Frogger Game: FSM vs Behavior Trees

> 🎮 A modern AI-enhanced take on the classic arcade game **Frogger**, leveraging **Finite State Machines (FSM)** and **Behavior Trees (BT)** to simulate intelligent autonomous agents.
> 🔬 Developed as part of the course **CSCI218 – Foundations of Artificial Intelligence** to explore applied game AI in dynamic environments.

## 📖 Overview

This project reimagines the nostalgic game **Frogger** by integrating artificial intelligence techniques to create adaptive, responsive, and strategic gameplay. The AI controls the frog agent, allowing it to autonomously navigate through streets filled with vehicles, cross rivers using moving platforms, and reach safe zones — all without player input.

We implemented two AI paradigms:

- 🌀 **Finite State Machines (FSM)** for simple, fast, rule-based logic.
- 🌳 **Behavior Trees (BT)** for modular, scalable, and layered decision-making.

This project demonstrates how **AI can enrich game environments**, making them more immersive and intelligent while acting as a real-world application of foundational AI principles.

---

## 🧠 Core AI Concepts

# 🔁 Finite State Machines (FSM)
- Deterministic transitions between `IDLE`, `MOVING`, and `WAITING`.
- Quick response to immediate threats (e.g., cars).
- Lightweight and efficient, ideal for simpler agents.

# 🌲 Behavior Trees (BT)
- Hierarchical structure for modular behavior.
- Nodes like **Selectors**, **Sequences**, and **Conditions** simulate complex decisions.
- Enables smarter adaptation based on game context.

---

## 🎮 Game Mechanics & Intelligence

| Section      | AI Logic                                                                 |
|--------------|--------------------------------------------------------------------------|
| 🚗 Street     | Predictive "danger zones" for vehicle avoidance; prioritizes upward movement |
| 🌊 River      | Detects floating platforms before moving; handles edge-of-screen logic    |
| 🏁 Safe Zones | Enters only unoccupied zones; avoids redundant or invalid moves           |

Additional behaviors:
- Randomized start delay for realism
- Movement cooldowns to simulate human-like reflexes

---

## 📊 FSM vs BT: Comparative Insights

| Feature                 | FSM                             | Behavior Tree                        |
|------------------------|----------------------------------|--------------------------------------|
| Decision Complexity     | Low                             | Medium to High                       |
| Performance             | Faster Execution                | Slower due to hierarchical traversal |
| Modularity              | Limited                         | Highly Modular                       |
| Scalability             | Poor for large logic sets       | Excellent for expanding behaviors    |
| Realism of Behavior     | Basic                           | More Natural                         |

---

## 🧪 Tech Stack

- **Language**: Python 3.8+
- **Game Engine**: Pygame
- **AI Framework**: `py_trees` (BT only)
- **Tools**: VS Code, Git, Windows OS

---

## 📁 Directory Structure

📦 frogger-ai-project
├── frogger_FSM.py # FSM-based autonomous frog AI
├── frogger_BT.py # Behavior Tree-based autonomous frog AI
├── /images # Game sprites and visuals
├── /sounds # Game SFX
├── requirements.txt # Dependency list
└── README.md # Project documentation


## ⚙️ Installation & Execution

# 1. Install Dependencies

pip install pygame py_trees

# 2. Run the Game
bash
Copy
Edit
# FSM AI Version
python frogger_FSM.py

# Behavior Tree AI Version
python frogger_BT.py
Ensure that /images and /sounds folders are in the same directory.

## 🎓 Learning Outcomes
Applied FSM and BT structures in a real-time game environment

Analyzed strengths and weaknesses of rule-based vs modular AI

Learned to implement human-like constraints (reaction delay, decision cooldowns)

Understood trade-offs between performance and intelligence in AI agents

## 🚀 Future Improvements
Implement reinforcement learning for self-learning agents (e.g., Q-Learning, DQN)

Add pathfinding algorithms (e.g., A*) to intelligently navigate dynamic terrain

Improve safe zone logic to seek alternatives when zones are filled

Add disappearing platforms, reactive obstacles, and multi-agent competition


## 📜 Acknowledgements
Base game adapted from: Pygame Frogger Project
Developed at University of Wollongong in Dubai for the CSCI218 AI course

## 🧾 License
This project is created solely for academic and learning purposes.
Commercial use or redistribution is not permitted without prior permission.
