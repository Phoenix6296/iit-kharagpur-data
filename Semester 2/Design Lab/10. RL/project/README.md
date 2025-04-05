# 🧹 Reinforcement Learning Agent in Grid World

## 🧠 Objective

This project develops a **Reinforcement Learning (RL)** agent to optimally clean a room represented as a 2D **grid-world environment**. The room may contain multiple **dirt patches**, and the agent learns to clean them efficiently while avoiding **walls** and **obstacles**.

Implemented algorithms:

- 🔸 **Q-Learning** (Tabular)
- 🔹 **Deep Q-Network (DQN)**

✨ **Bonus:** Extended support for **multiple dirt patches**.

---

## 📁 Repository Structure

```
.
├── 24CS60R71_QLearning.py     # Q-Learning implementation
├── 24CS60R71_DQN.py           # Deep Q-Network implementation
├── 24CS60R71_Bonus.py         # BONUS: Multi-dirt cleaning logic
├── 24CS60R71_Report.pdf       # Project report with evaluations
├── requirements.txt           # Required Python packages
├── README.md                  # README
```

---

## ⚙️ Setup Instructions

### 🛠 Requirements

- Python 3.8+
- Install all dependencies via:

```bash
pip install -r requirements.txt
```

---

## 🔁 Running the Code

### 🟡 Q-Learning

```bash
python 24CS60R71_QLearning.py --hyperparameter        # Grid search tuning
python 24CS60R71_QLearning.py --visualize             # Visual run using PyGame
python 24CS60R71_QLearning.py --evaluate              # Evaluate performance
python 24CS60R71_QLearning.py --evaluate --hyperparameter  # Eval with best params
```

---

### 🔵 Deep Q-Learning (DQN)

```bash
python 24CS60R71_DQN.py --hyperparameter             # Tune DQN hyperparameters
python 24CS60R71_DQN.py --visualize                  # Visualize agent's run
python 24CS60R71_DQN.py --evaluate                   # Evaluate across grid sizes
python 24CS60R71_DQN.py --evaluate --hyperparameter  # Evaluate best-tuned DQN
```

---

### ⭐ Bonus: Multiple Dirt Patches

```bash
python 24CS60R71_Bonus.py --size 20 --dirts 5 --visualize
```

📝 **Arguments**:
- `--size`: Grid dimension (NxN)
- `--dirts`: Number of dirt patches
- `--visualize`: Enable real-time display

---

## 💡 Features

✅ **Custom Gym-Compatible Environment** (scales up to 10^7 cells)  
🎮 **Real-Time Visualization** with PyGame  
📈 **Hyperparameter Tuning** via grid search  
📊 **Evaluation Metrics**: Reward, steps, collisions, time  
📦 **Scalable & Efficient**  
🌟 **BONUS**: Smart handling of multiple dirt targets  

---

## 📄 Report

Check out `24CS60R71_Report.pdf` for:

- 🔍 Environment design choices  
- 🧠 Algorithm details & hyperparameter tuning  
- 📊 Training curves and performance plots  
- ⚔️ Comparison between Q-Learning and DQN  
- 🧪 Experiments on large grids  
- 💥 Bonus implementation strategy  

---

## ✅ Submission Checklist

✔️ `24CS60R71_QLearning.py`  
✔️ `24CS60R71_DQN.py`  
✔️ `24CS60R71_Bonus.py`  
✔️ `24CS60R71_Report.pdf`  
✔️ `README.md`  
✔️ `requirements.txt`  
📦 Zipped as: `24CS60R71_Project.zip`  

---

## 📬 Contact

For any doubts or clarifications, feel free to reach out:

**👤 Krishna Biswakarma**  
🎓 Roll No: `24CS60R71`  
📧 Email: krishnabiswakarma.24@kgpian.iitkgp.ac.in  

---