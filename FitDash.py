#!/usr/bin/env python3
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas

# ======================================================
# =============== CORE FUNCTIONS & DATA ================
# ======================================================

def mifflin_st_jeor(sex, weight, height, age):
    if sex.lower() == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

ACTIVITY_MAP = {
    "No sport (sedentary)": 1.2,
    "Light (1-2x/week)": 1.375,
    "Moderate (3-4x/week)": 1.55,
    "High (5-6x/week)": 1.725,
    "Very high (daily training)": 1.9,
}

EXERCISES = {
    "Push": ["Bench Press", "Overhead Press", "Dips", "Incline Dumbbell Press"],
    "Pull": ["Pull-ups", "Barbell Row", "Face Pull", "Biceps Curls"],
    "Legs": ["Squat", "Deadlift", "Leg Press", "Calf Raise"],
    "Full Body": ["Squat", "Bench Press", "Barbell Row", "Pull-up"],
}

SPLITS = ["Push", "Pull", "Legs", "Full Body"]

def generate_calorie_plan(data):
    bmr = mifflin_st_jeor(data["sex"], data["weight"], data["height"], data["age"])
    tdee = bmr * ACTIVITY_MAP[data["activity"]]
    intensity_map = {"slow": 0.1, "normal": 0.15, "fast": 0.2}
    goal = tdee * (1 + intensity_map[data["intensity"]])
    protein = data["weight"] * 2.2
    fat = data["weight"] * 0.8
    carbs = (goal - (protein * 4 + fat * 9)) / 4
    meals = [
        ("Breakfast", ["Oats with milk", "Banana", "Eggs"]),
        ("Lunch", ["Rice", "Chicken breast", "Vegetables"]),
        ("Snack", ["Greek yogurt", "Almonds"]),
        ("Dinner", ["Sweet potato", "Salmon", "Broccoli"]),
    ]
    return {
        "bmr": bmr, "tdee": tdee, "calorie_goal": goal,
        "protein_g": protein, "fat_g": fat, "carbs_g": carbs, "meals": meals
    }

def pick_exercises_for_split(split, level="Beginner"):
    exs = EXERCISES.get(split, [])
    return [{"exercise": e, "sets": 3, "reps": 10, "notes": "Controlled form"} for e in exs]

def generate_sport_plan(prefs):
    plan = []
    for i in range(int(prefs["days_per_week"])):
        split = SPLITS[i % len(SPLITS)]
        plan.append({
            "day": i + 1, "split": split,
            "exercises": pick_exercises_for_split(split, prefs["level"])
        })
    return {
        "plan": plan,
        "guidance": {"Warmup": "5–10 min light cardio", "Cool-down": "Stretch after training"},
        "nutrition": {"pre_workout": "Fast carbs + protein", "post_workout": "Protein shake + meal"},
    }

def export_pdf_general(title, lines, path):
    c = pdf_canvas.Canvas(path, pagesize=A4)
    w, h = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, h - 50, title)
    c.setFont("Helvetica", 11)
    y = h - 80
    for line in lines:
        if y < 50:
            c.showPage()
            y = h - 50
        c.drawString(50, y, line)
        y -= 15
    c.save()


# ======================================================
# =================== MAIN DASHBOARD ===================
# ======================================================

class DashboardApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("🏋️ Fitness Dashboard")
        self.geometry("1150x750")
        self.minsize(950, 650)

        self.sidebar = Sidebar(self)
        self.sidebar.pack(side="left", fill="y")

        self.content_frame = ctk.CTkFrame(self, fg_color="#101820")
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.show_home()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_home(self):
        self.clear_content()
        HomeFrame(self.content_frame, self).pack(fill="both", expand=True)

    def show_calorie(self):
        self.clear_content()
        CalorieFrame(self.content_frame, self.show_home).pack(fill="both", expand=True)

    def show_workout(self):
        self.clear_content()
        SportFrame(self.content_frame, self.show_home).pack(fill="both", expand=True)


# ======================================================
# ===================== SIDEBAR ========================
# ======================================================

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, width=220, fg_color="#161b22", corner_radius=0)
        self.parent = parent

        ctk.CTkLabel(self, text="💪 FIT DASH", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(30, 40))

        self._add_button("🏠  Home", self.parent.show_home)
        self._add_button("🍽️  Calorie Plan", self.parent.show_calorie)
        self._add_button("🏋️  Workout Plan", self.parent.show_workout)

        ctk.CTkLabel(self, text="Built with Python by reax7", text_color="#777", font=ctk.CTkFont(size=11)).pack(side="bottom", pady=20)

    def _add_button(self, text, command):
        btn = ctk.CTkButton(
            self, text=text, command=command,
            corner_radius=10, fg_color="#1f2630",
            hover_color="#3a7bd5", height=40,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        btn.pack(fill="x", padx=20, pady=8)


# ======================================================
# ===================== HOME PAGE ======================
# ======================================================

class HomeFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#101820")
        ctk.CTkLabel(self, text="🏋️ Fitness Dashboard", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=(100, 10))
        ctk.CTkLabel(self, text="Train smart. Eat clean. Grow stronger.",
                     font=ctk.CTkFont(size=16), text_color="#999").pack(pady=(0, 40))
        ctk.CTkLabel(self, text="Use the sidebar to get started.", font=ctk.CTkFont(size=14), text_color="#777").pack()


# ======================================================
# =================== CALORIE FRAME ====================
# ======================================================

class CalorieFrame(ctk.CTkFrame):
    def __init__(self, parent, on_back):
        super().__init__(parent, fg_color="#101820")
        self.on_back = on_back
        self._build()

    def _build(self):
        sidebar = ctk.CTkFrame(self, width=280, fg_color="#181c25", corner_radius=10)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)

        content = ctk.CTkFrame(self, fg_color="#1b1f27", corner_radius=10)
        content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(sidebar, text="Calorie Settings", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 15))

        self.sex = ctk.CTkComboBox(sidebar, values=["male", "female"])
        self.sex.set("male")
        self._entry(sidebar, "Gender:", self.sex)

        self.age = self._entry(sidebar, "Age:", ctk.CTkEntry(sidebar))
        self.age.insert(0, "25")

        self.weight = self._entry(sidebar, "Weight (kg):", ctk.CTkEntry(sidebar))
        self.weight.insert(0, "80")

        self.height = self._entry(sidebar, "Height (cm):", ctk.CTkEntry(sidebar))
        self.height.insert(0, "180")

        self.target = self._entry(sidebar, "Target (kg):", ctk.CTkEntry(sidebar))
        self.target.insert(0, "90")

        self.activity = ctk.CTkComboBox(sidebar, values=list(ACTIVITY_MAP.keys()))
        self.activity.set("Moderate (3-4x/week)")
        self._entry(sidebar, "Activity:", self.activity)

        self.intensity = ctk.CTkComboBox(sidebar, values=["slow", "normal", "fast"])
        self.intensity.set("normal")
        self._entry(sidebar, "Intensity:", self.intensity)

        ctk.CTkButton(sidebar, text="Calculate", command=self.calculate, fg_color="#3a7bd5").pack(pady=10, fill="x")
        ctk.CTkButton(sidebar, text="← Back", command=self.on_back).pack(pady=5, fill="x")

        self.output = ctk.CTkTextbox(content, wrap="word", font=ctk.CTkFont(size=13))
        self.output.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkButton(content, text="Save as PDF", command=self.save_pdf).pack(pady=10)

    def _entry(self, frame, label, widget):
        ctk.CTkLabel(frame, text=label).pack(anchor="w")
        widget.pack(fill="x", pady=4)
        return widget

    def calculate(self):
        data = {
            "sex": self.sex.get(),
            "age": int(self.age.get()),
            "weight": float(self.weight.get()),
            "height": float(self.height.get()),
            "target": float(self.target.get()),
            "activity": self.activity.get(),
            "intensity": self.intensity.get(),
        }
        plan = generate_calorie_plan(data)
        self.plan = plan
        self._show(plan)

    def _show(self, plan):
        self.output.delete("1.0", "end")
        lines = [
            f"BMR: {plan['bmr']:.0f} kcal",
            f"TDEE: {plan['tdee']:.0f} kcal",
            f"Goal Calories: {plan['calorie_goal']:.0f} kcal",
            f"Protein: {plan['protein_g']:.0f} g | Fat: {plan['fat_g']:.0f} g | Carbs: {plan['carbs_g']:.0f} g",
            "", "Example Day Plan:",
        ]
        for meal, items in plan["meals"]:
            lines.append(f"{meal}:")
            for i in items:
                lines.append(f"  - {i}")
        self.output.insert("1.0", "\n".join(lines))

    def save_pdf(self):
        if not hasattr(self, "plan"):
            messagebox.showerror("Error", "Calculate a plan first.")
            return
        f = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not f:
            return
        lines = self.output.get("1.0", "end").splitlines()
        export_pdf_general("Calorie Plan", lines, f)
        messagebox.showinfo("Saved", f"PDF saved: {f}")


# ======================================================
# =================== SPORT FRAME ======================
# ======================================================

class SportFrame(ctk.CTkFrame):
    def __init__(self, parent, on_back):
        super().__init__(parent, fg_color="#101820")
        self.on_back = on_back
        self._build()

    def _build(self):
        sidebar = ctk.CTkFrame(self, width=280, fg_color="#181c25", corner_radius=10)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)

        content = ctk.CTkFrame(self, fg_color="#1b1f27", corner_radius=10)
        content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(sidebar, text="Workout Settings", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 15))

        self.level = ctk.CTkComboBox(sidebar, values=["Beginner", "Advanced", "Pro"])
        self.level.set("Beginner")
        self._entry(sidebar, "Level:", self.level)

        self.days = ctk.CTkEntry(sidebar, placeholder_text="Days per week (1–6)")
        self.days.insert(0, "4")
        self._entry(sidebar, "Days per Week:", self.days)

        self.equipment = ctk.CTkComboBox(sidebar, values=["Gym", "Home"])
        self.equipment.set("Gym")
        self._entry(sidebar, "Equipment:", self.equipment)

        ctk.CTkButton(sidebar, text="Generate", command=self.generate_plan, fg_color="#3a7bd5").pack(pady=10, fill="x")
        ctk.CTkButton(sidebar, text="← Back", command=self.on_back).pack(pady=5, fill="x")

        self.output = ctk.CTkTextbox(content, wrap="word", font=ctk.CTkFont(size=13))
        self.output.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkButton(content, text="Save as PDF", command=self.save_pdf).pack(pady=10)

    def _entry(self, frame, label, widget):
        ctk.CTkLabel(frame, text=label).pack(anchor="w")
        widget.pack(fill="x", pady=4)
        return widget

    def generate_plan(self):
        prefs = {"level": self.level.get(), "days_per_week": self.days.get(), "equipment_pref": self.equipment.get()}
        result = generate_sport_plan(prefs)
        self.plan = result
        self._show(result)

    def _show(self, result):
        self.output.delete("1.0", "end")
        lines = ["Workout Plan (Week):"]
        for day in result["plan"]:
            lines.append(f"Day {day['day']} - {day['split']}")
            for ex in day["exercises"]:
                lines.append(f"  - {ex['exercise']}: {ex['sets']} sets × {ex['reps']} reps ({ex['notes']})")
            lines.append("")
        lines.append("\nGeneral Guidance:")
        for k, v in result["guidance"].items():
            lines.append(f"- {k}: {v}")
        lines.append("\nNutrition:")
        lines.append(f"- Pre: {result['nutrition']['pre_workout']}")
        lines.append(f"- Post: {result['nutrition']['post_workout']}")
        self.output.insert("1.0", "\n".join(lines))

    def save_pdf(self):
        if not hasattr(self, "plan"):
            messagebox.showerror("Error", "Generate a plan first.")
            return
        f = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not f:
            return
        lines = self.output.get("1.0", "end").splitlines()
        export_pdf_general("Workout Plan", lines, f)
        messagebox.showinfo("Saved", f"PDF saved: {f}")


# ======================================================
# ===================== RUN APP ========================
# ======================================================

if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()
