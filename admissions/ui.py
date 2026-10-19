"""UI layer: an ipywidgets app with three tabs (Registration, Update Profile, Leaderboard & Radar)."""
import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import clear_output, display

from .engine import normalized_scores, validate_registration
from .models import Applicant


class UniversityUI:
    def __init__(self, engine, producer):
        self.engine = engine
        self.producer = producer
        self.output = widgets.Output()
        self.setup_widgets()

    def setup_widgets(self):
        # Registration
        self.reg_fn = widgets.Text(description="First Name:", placeholder="John")
        self.reg_ln = widgets.Text(description="Last Name:", placeholder="Doe")
        self.reg_mail = widgets.Text(description="Gmail:", placeholder="example@gmail.com")
        self.reg_sat = widgets.IntSlider(value=1200, min=400, max=1600, description="SAT Score:")  # REQ-10
        self.reg_ec = widgets.IntSlider(value=3, min=1, max=5, description="EC Impact:")
        self.reg_gpa = widgets.FloatSlider(value=3.0, min=0.0, max=4.0, step=0.1, description="GPA:")
        self.reg_int = widgets.IntSlider(value=3, min=1, max=5, description="Interview:")
        self.reg_rec_text = widgets.Textarea(
            description="Rec Letter:",
            placeholder="Paste the recommendation letter here...",
            layout=widgets.Layout(height="100px", width="90%"),
        )
        self.btn_register = widgets.Button(description="Submit Application", button_style="success", icon="paper-plane")
        self.btn_register.on_click(self.on_register_click)

        # Self-service (REQ-03, REQ-09)
        self.upd_mail = widgets.Text(description="Verify Email:")
        self.upd_sat = widgets.IntSlider(value=1200, min=400, max=1600, description="New SAT:")
        self.upd_ec = widgets.IntSlider(value=3, min=1, max=5, description="New EC:")
        self.btn_update = widgets.Button(description="Update My Scores", button_style="warning", icon="refresh")
        self.btn_delete = widgets.Button(description="Delete My Account", button_style="danger", icon="trash")
        self.btn_update.on_click(self.on_update_click)
        self.btn_delete.on_click(self.on_delete_click)

        # Admin weights
        def weight(label):
            return widgets.FloatSlider(value=0.2, min=0, max=1.0, step=0.05, description=label)
        self.w_sat, self.w_ec, self.w_gpa = weight("SAT Weight:"), weight("EC Weight:"), weight("GPA Weight:")
        self.w_int, self.w_rec = weight("Int. Weight:"), weight("Rec. Weight:")
        self.btn_refresh = widgets.Button(description="Fetch Analytics", button_style="info", icon="bar-chart")
        self.btn_refresh.on_click(self.render_leaderboard)

    def on_register_click(self, _):
        with self.output:
            clear_output()
            first_name = self.reg_fn.value.strip()
            last_name = self.reg_ln.value.strip()
            email = self.reg_mail.value.lower().strip()

            error = validate_registration(first_name, last_name, email)
            if error:
                print(f"❌ ERROR: {error}")
                return
            if self.engine.is_email_taken(email):
                print(f"⚠️ ERROR: Email ({email}) already exists!")
                return

            app = Applicant(first_name, last_name, email, self.reg_sat.value, self.reg_ec.value,
                            self.reg_gpa.value, self.reg_int.value, rec_text=self.reg_rec_text.value)
            self.engine.applicants[email] = app
            self.producer.send_event("NEW_REGISTRATION", {"id": app.user_id, "email": email})
            print(f"✅ SUCCESS: Registered! Assigned ID: {app.user_id}")
            print("🤖 Letter assessment:")
            for line in app.audit_log[-3:]:
                print(f"  {line}")

    def on_update_click(self, _):
        with self.output:
            email = self.upd_mail.value.lower().strip()
            app = self.engine.applicants.get(email)
            if not app:
                print("❌ ERROR: Email not found!")
                return
            app.sat, app.ec = self.upd_sat.value, self.upd_ec.value
            app.add_log(f"Updated SAT to {app.sat}, EC to {app.ec}")
            self.producer.send_event("SCORE_UPDATE", {"id": app.user_id})
            print(f"🔄 Profile updated for {app.first_name}.")

    def on_delete_click(self, _):
        with self.output:
            email = self.upd_mail.value.lower().strip()
            if self.engine.applicants.pop(email, None):
                print(f"🗑️ Account for {email} deleted.")
            else:
                print("❌ ERROR: User not found.")

    def plot_radar_chart(self):
        """Compare up to three applicants across all five criteria."""
        if not self.engine.applicants:
            return
        categories = ["SAT Score", "Extra-Curricular", "GPA", "Interview", "Auto Rec Score"]
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        for app in self.engine.ranked()[:3]:
            values = list(normalized_scores(app).values())
            values += values[:1]
            ax.plot(angles, values, label=f"{app.first_name} ({app.user_id})", linewidth=2)
            ax.fill(angles, values, alpha=0.15)

        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.degrees(angles[:-1]), categories)
        ax.set_ylim(0, 100)
        plt.title("Candidate Comparison (Radar View)", y=1.1, fontsize=12, fontweight="bold")
        plt.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
        plt.show()

    def render_leaderboard(self, _):
        with self.output:
            clear_output()
            weights = {"SAT": self.w_sat.value, "EC": self.w_ec.value, "GPA": self.w_gpa.value,
                       "INT": self.w_int.value, "REC": self.w_rec.value}
            self.engine.calculate_rankings(weights)
            if not self.engine.applicants:
                print("No applicants yet.")
                return

            rows = [{
                "Rank": rank,
                "User ID": app.user_id,
                "Name": f"{app.first_name} {app.last_name}",
                "Weighted Score": round(app.total_score, 2),
                "Rec Score (auto)": f"{app.recommendation}/5",
                "Strengths": ", ".join(app.strengths),
                "Scholarship Tier": app.scholarship_status,
            } for rank, app in enumerate(self.engine.ranked(), 1)]
            display(pd.DataFrame(rows).set_index("Rank"))  # REQ-08
            print("\n" + "=" * 50 + "\n")
            self.plot_radar_chart()

    def render(self):
        tab1 = widgets.VBox([widgets.HTML("<h3>Create New Application</h3>"), self.reg_fn, self.reg_ln,
                             self.reg_mail, self.reg_sat, self.reg_ec, self.reg_gpa, self.reg_int,
                             self.reg_rec_text, self.btn_register])
        tab2 = widgets.VBox([widgets.HTML("<h3>Student Self-Service</h3>"), self.upd_mail, self.upd_sat,
                             self.upd_ec, widgets.HBox([self.btn_update, self.btn_delete])])
        tab3 = widgets.VBox([widgets.HTML("<h3>Admin Analytics</h3>"),
                             widgets.HBox([widgets.VBox([self.w_sat, self.w_ec, self.w_gpa]),
                                           widgets.VBox([self.w_int, self.w_rec, self.btn_refresh])])])
        tabs = widgets.Tab(children=[tab1, tab2, tab3])
        for i, title in enumerate(["Registration", "Update Profile", "Leaderboard & Radar"]):
            tabs.set_title(i, title)
        display(tabs, self.output)
