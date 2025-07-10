import requests
from bs4 import BeautifulSoup
import csv, json, sqlite3, threading
import datetime
import matplotlib.pyplot as plt
import spacy
from collections import Counter
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class HoverButton(ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_color = self._fg_color
        self.hover_color = kwargs.get("hover_color", "#ff4c4c")
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.configure(fg_color=self.hover_color)

    def on_leave(self, event):
        self.configure(fg_color=self.default_color)

class GlassFrame(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            fg_color=("#111111", "#111111"),
            border_width=1,
            border_color="#ff0000"
        )

class JobScraperApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🔎 Job Scraper Pro | Powered by Y7X 💗")
        self.geometry("1050x700")
        self.jobs_data = []
        self.configure(fg_color="#000000")  # AMOLED background

        self.create_widgets()

    def create_widgets(self):
        header = ctk.CTkLabel(self, text="💼 Job Scraper Pro", font=("Arial Rounded MT Bold", 28), text_color="#ff4c4c")
        header.pack(pady=10)

        filter_frame = GlassFrame(self, corner_radius=12)
        filter_frame.pack(pady=10)

        self.keyword_entry = ctk.CTkEntry(filter_frame, placeholder_text="Enter keyword (e.g. Python)", width=220)
        self.keyword_entry.grid(row=0, column=0, padx=10, pady=10)

        self.location_entry = ctk.CTkEntry(filter_frame, placeholder_text="Enter location (e.g. Remote)", width=220)
        self.location_entry.grid(row=0, column=1, padx=10, pady=10)

        self.scrape_button = HoverButton(filter_frame, text="🔍 Scrape Jobs", command=self.scrape_jobs_thread, fg_color="#ff0000", hover_color="#ff4c4c")
        self.scrape_button.grid(row=0, column=2, padx=10, pady=10)

        self.results_frame = ctk.CTkScrollableFrame(self, width=950, height=320, corner_radius=12, fg_color="#000000")
        self.results_frame.pack(pady=10)

        export_frame = GlassFrame(self, corner_radius=10)
        export_frame.pack(pady=0)

        HoverButton(export_frame, text="💾 CSV", command=self.export_csv, fg_color="#ff0000").pack(side="left", padx=6)
        HoverButton(export_frame, text="📁 JSON", command=self.export_json, fg_color="#ff0000").pack(side="left", padx=6)
        HoverButton(export_frame, text="📊 Excel", command=self.export_excel, fg_color="#ff0000").pack(side="left", padx=6)
        HoverButton(export_frame, text="🗄️ Save to DB", command=self.save_to_db, fg_color="#ff0000").pack(side="left", padx=6)
        HoverButton(export_frame, text="📈 Visualize", command=self.visualize_data, fg_color="#ff0000").pack(side="left", padx=6)
        HoverButton(export_frame, text="🧠 Match Resume", command=self.match_resume, fg_color="#ff0000").pack(side="left", padx=6)

        footer = ctk.CTkLabel(self, text="🔎 Powered by Y7X 💗", font=("Courier New", 14), text_color="#ff4c4c")
        footer.pack(pady=10)

    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def display_job_card(self, job):
        card = GlassFrame(self.results_frame, corner_radius=10)
        card.pack(fill="x", padx=10, pady=5)

        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title = ctk.CTkLabel(content_frame, text=f"💼 {job[0]}", font=("Arial", 16, "bold"), text_color="#ff4c4c")
        title.pack(anchor="w")

        company = ctk.CTkLabel(content_frame, text=f"🏢 {job[1]}", font=("Arial", 14), text_color="white")
        company.pack(anchor="w")

        location = ctk.CTkLabel(content_frame, text=f"📍 {job[2]}", font=("Arial", 14), text_color="white")
        location.pack(anchor="w")

        date = ctk.CTkLabel(content_frame, text=f"🌐 Posted: {job[3]}", font=("Arial", 12, "italic"), text_color="gray")
        date.pack(anchor="w")

    def scrape_jobs_thread(self):
        threading.Thread(target=self.scrape_jobs).start()

    def scrape_jobs(self):
        self.jobs_data.clear()
        self.clear_results()

        keyword = self.keyword_entry.get().strip().replace(' ', '-')
        location = self.location_entry.get().strip().replace(' ', '-')
        base_url = f"https://remoteok.com/remote-{keyword}+{location}-jobs"
        headers = {"User-Agent": "Mozilla/5.0"}

        page = 1
        while True:
            url = base_url if page == 1 else f"{base_url}?page={page}"
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")
            job_listings = soup.find_all("tr", class_="job")

            if not job_listings:
                break

            for job in job_listings:
                title = job.find("h2", {"itemprop": "title"})
                company = job.find("h3", {"itemprop": "name"})
                location_div = job.find("div", class_="location")
                date = job.find("time")

                job_title = title.text.strip() if title else "N/A"
                company_name = company.text.strip() if company else "N/A"
                job_location = location_div.text.strip() if location_div else "Remote"
                job_date = date["datetime"] if date else "N/A"

                job_data = [job_title, company_name, job_location, job_date]
                self.jobs_data.append(job_data)
                self.after(0, lambda job=job_data: self.display_job_card(job))

            page += 1

        self.after(0, lambda: messagebox.showinfo("✅ Done", f"Scraped {len(self.jobs_data)} jobs across multiple pages."))

    def export_csv(self):
        with open("jobs.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Job Title", "Company", "Location", "Date"])
            writer.writerows(self.jobs_data)
        messagebox.showinfo("💾 Exported", "Jobs saved to jobs.csv")

    def export_json(self):
        with open("jobs.json", "w", encoding="utf-8") as f:
            json.dump([{"title": j[0], "company": j[1], "location": j[2], "date": j[3]} for j in self.jobs_data], f, indent=2)
        messagebox.showinfo("📁 Exported", "Jobs saved to jobs.json")

    def export_excel(self):
        df = pd.DataFrame(self.jobs_data, columns=["Job Title", "Company", "Location", "Date"])
        df.to_excel("jobs.xlsx", index=False)
        messagebox.showinfo("📊 Exported", "Jobs saved to jobs.xlsx")

    def save_to_db(self):
        conn = sqlite3.connect("jobs.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                title TEXT,
                company TEXT,
                location TEXT,
                date TEXT
            )
        """)
        cursor.executemany("INSERT INTO jobs VALUES (?, ?, ?, ?)", self.jobs_data)
        conn.commit()
        conn.close()
        messagebox.showinfo("🗄️ Saved", "Jobs saved to jobs.db")

    def visualize_data(self):
        locations = [job[2] for job in self.jobs_data if job[2] != "N/A"]
        count = Counter(locations)
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.bar(count.keys(), count.values(), color="#ff4c4c")
        ax.set_title("📍 Job Count by Location")
        ax.set_ylabel("Number of Jobs")
        ax.set_xlabel("Location")
        plt.xticks(rotation=45)

        top = ctk.CTkToplevel(self)
        top.title("📈 Visualization")
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def match_resume(self):
        try:
            with open("resume.txt", "r", encoding="utf-8") as f:
                resume_text = f.read()
            resume_doc = nlp(resume_text)
            matched = []
            for job in self.jobs_data:
                job_doc = nlp(" ".join(job))
                similarity = resume_doc.similarity(job_doc)
                matched.append((job[0], job[1], job[2], job[3], round(similarity * 100, 2)))

            matched.sort(key=lambda x: x[4], reverse=True)
            self.clear_results()
            for job in matched:
                self.display_job_card([job[0], job[1], job[2], job[3]])

        except Exception as e:
            messagebox.showerror("Error", f"Failed to match resume: {e}")

if __name__ == "__main__":
    app = JobScraperApp()
    app.mainloop()