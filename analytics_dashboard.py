import tkinter as tk
from tkinter import ttk
from datetime import datetime
from collections import Counter
from app.db import get_session
from app.models import Score, JournalEntry

class AnalyticsDashboard:
    def __init__(self, parent_root, username):
        self.parent_root = parent_root
        self.username = username
        
    def open_dashboard(self):
        """Open analytics dashboard"""
        dashboard = tk.Toplevel(self.parent_root)
        dashboard.title("📊 Emotional Health Dashboard")
        dashboard.geometry("600x500")
        
        tk.Label(dashboard, text="📊 Emotional Health Analytics", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        notebook = ttk.Notebook(dashboard)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # EQ Trends
        eq_frame = ttk.Frame(notebook)
        notebook.add(eq_frame, text="EQ Trends")
        self.show_eq_trends(eq_frame)
        
        # Journal Analytics
        journal_frame = ttk.Frame(notebook)
        notebook.add(journal_frame, text="Journal Analytics")
        self.show_journal_analytics(journal_frame)
        
        # Insights
        insights_frame = ttk.Frame(notebook)
        notebook.add(insights_frame, text="Insights")
        self.show_insights(insights_frame)
        
    def show_eq_trends(self, parent):
        """Show EQ score trends"""
        session = get_session()
        try:
            # Query only the total_score
            rows = session.query(Score.total_score)\
                .filter_by(username=self.username)\
                .order_by(Score.id)\
                .all()
            scores = [r[0] for r in rows]
        finally:
            session.close()
        
        if not scores:
            tk.Label(parent, text="No EQ data available", font=("Arial", 14)).pack(pady=50)
            return
            
        tk.Label(parent, text="📈 EQ Score Progress", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Stats
        stats_frame = tk.Frame(parent)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(stats_frame, text=f"Total Tests: {len(scores)}", font=("Arial", 12)).pack(anchor="w")
        tk.Label(stats_frame, text=f"Latest Score: {scores[-1]}", font=("Arial", 12)).pack(anchor="w")
        tk.Label(stats_frame, text=f"Best Score: {max(scores)}", font=("Arial", 12)).pack(anchor="w")
        tk.Label(stats_frame, text=f"Average: {sum(scores)/len(scores):.1f}", font=("Arial", 12)).pack(anchor="w")
        
        if len(scores) > 1:
            improvement = ((scores[-1] - scores[0]) / scores[0]) * 100
            color = "green" if improvement > 0 else "red"
            tk.Label(stats_frame, text=f"Improvement: {improvement:.1f}%", 
                    font=("Arial", 12, "bold"), fg=color).pack(anchor="w")
        
        # Simple chart
        chart_frame = tk.Frame(parent)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        chart_text = tk.Text(chart_frame, height=8, font=("Courier", 10))
        chart_text.pack(fill=tk.BOTH, expand=True)
        
        max_score = max(scores)
        for i, score in enumerate(scores):
            bar_length = int((score / max_score) * 20)
            bar = "█" * bar_length
            chart_text.insert(tk.END, f"Test {i+1:2d}: {bar} {score}\n")
        
        chart_text.config(state=tk.DISABLED)
        
    def show_journal_analytics(self, parent):
        """Show journal analytics"""
        session = get_session()
        try:
            rows = session.query(JournalEntry.sentiment_score, JournalEntry.emotional_patterns)\
                .filter_by(username=self.username)\
                .all()
        finally:
            session.close()
        
        if not rows:
            tk.Label(parent, text="No journal data available", font=("Arial", 14)).pack(pady=50)
            return
            
        tk.Label(parent, text="📝 Journal Analytics", font=("Arial", 14, "bold")).pack(pady=10)
        
        sentiments = [r[0] for r in rows]
        
        # Stats
        stats_frame = tk.Frame(parent)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(stats_frame, text=f"Total Entries: {len(rows)}", font=("Arial", 12)).pack(anchor="w")
        tk.Label(stats_frame, text=f"Avg Sentiment: {sum(sentiments)/len(sentiments):.1f}", 
                font=("Arial", 12)).pack(anchor="w")
        tk.Label(stats_frame, text=f"Most Positive: {max(sentiments):.1f}", 
                font=("Arial", 12)).pack(anchor="w")
        
        # Patterns
        patterns_frame = tk.Frame(parent)
        patterns_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(patterns_frame, text="Top Emotional Patterns:", 
                font=("Arial", 12, "bold")).pack(anchor="w")
        
        all_patterns = []
        for r in rows:
            if r[1]: # emotional_patterns
                all_patterns.extend(r[1].split('; '))
        
        pattern_counts = Counter(all_patterns)
        
        patterns_text = tk.Text(patterns_frame, height=6, font=("Arial", 11))
        patterns_text.pack(fill=tk.BOTH, expand=True)
        
        for pattern, count in pattern_counts.most_common(3):
            percentage = (count / len(rows)) * 100
            patterns_text.insert(tk.END, f"{pattern}: {count} times ({percentage:.1f}%)\n")
        
        patterns_text.config(state=tk.DISABLED)
        
    def show_insights(self, parent):
        """Show personalized insights"""
        tk.Label(parent, text="🔍 Your Insights", font=("Arial", 14, "bold")).pack(pady=10)
        
        insights_text = tk.Text(parent, wrap=tk.WORD, font=("Arial", 11), bg="#f8f9fa")
        insights_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        insights = self.generate_insights()
        
        for insight in insights:
            insights_text.insert(tk.END, f"• {insight}\n\n")
            
        insights_text.config(state=tk.DISABLED)
        
    def generate_insights(self):
        """Generate insights"""
        insights = []
        
        session = get_session()
        try:
            # EQ insights
            eq_rows = session.query(Score.total_score)\
                .filter_by(username=self.username)\
                .order_by(Score.id)\
                .all()
            scores = [r[0] for r in eq_rows]
            
            # Journal insights
            j_rows = session.query(JournalEntry.sentiment_score)\
                .filter_by(username=self.username)\
                .all()
            sentiments = [r[0] for r in j_rows]
        finally:
            session.close()
        
        if len(scores) > 1:
            improvement = ((scores[-1] - scores[0]) / scores[0]) * 100
            if improvement > 10:
                insights.append(f"📈 Great progress! Your EQ improved by {improvement:.1f}%")
            elif improvement > 0:
                insights.append(f"📊 Steady progress with {improvement:.1f}% EQ improvement")
            else:
                insights.append("💪 Focus on emotional awareness to boost EQ scores")
        
        if sentiments:
            avg_sentiment = sum(sentiments) / len(sentiments)
            if avg_sentiment > 20:
                insights.append("😊 Your journal shows positive emotional tone - keep it up!")
            elif avg_sentiment < -20:
                insights.append("🤗 Consider stress management techniques for better emotional balance")
            else:
                insights.append("⚖️ You maintain balanced emotional tone in your reflections")
        
        if not insights:
            insights.append("📝 Complete more assessments and journal entries for insights!")
            
        return insights