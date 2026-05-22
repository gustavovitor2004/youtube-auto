"""
Analytics Module — 100% gratuito
Usa: YouTube Analytics API (grátis, mesma autenticação do upload)
Analisa performance e gera recomendações automáticas
"""

import json
import pickle
from pathlib import Path
from datetime import datetime, timedelta

try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    GOOGLE_OK = True
except ImportError:
    GOOGLE_OK = False


class AnalyticsManager:
    def __init__(self, config):
        self.config = config
        self._analytics = None
        self._youtube   = None
        self.log_path   = Path("output/performance_log.json")

    # ─── PUBLIC ───────────────────────────────────────────────────────────────

    def analyze_recent(self, days: int = 7):
        """Analisa os últimos N dias e imprime recomendações."""
        if not GOOGLE_OK:
            print("Google API libs not installed")
            return

        client = self._get_analytics_client()
        if not client:
            return

        end_date   = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        try:
            # Métricas principais
            report = client.reports().query(
                ids="channel==MINE",
                startDate=start_date,
                endDate=end_date,
                metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained,likes",
                dimensions="video",
                sort="-views",
                maxResults=20
            ).execute()

            videos = self._parse_report(report)
            self._save_log(videos)
            self._print_insights(videos)
            return videos

        except Exception as e:
            print(f"Analytics error: {e}")
            return None

    def get_recommendations(self) -> dict:
        """
        Lê o log de performance e retorna recomendações
        para o próximo ciclo de criação.
        """
        if not self.log_path.exists():
            return {"status": "no_data", "recommendations": []}

        with open(self.log_path) as f:
            data = json.load(f)

        videos = data.get("videos", [])
        if not videos:
            return {"status": "no_data", "recommendations": []}

        # Separa top performers e underperformers
        avg_ctr       = sum(v.get("ctr", 0) for v in videos) / len(videos)
        avg_retention = sum(v.get("avg_view_duration", 0) for v in videos) / len(videos)

        top     = [v for v in videos if v.get("views", 0) > sum(v2["views"] for v2 in videos) / len(videos)]
        bottom  = [v for v in videos if v not in top]

        recs = []

        if avg_ctr < 0.05:
            recs.append("CTR BAIXO (<5%): Teste thumbnails mais agressivos com rostos/expressões. Use palavras de poder no título.")
        if avg_retention < 0.4:
            recs.append("RETENÇÃO BAIXA (<40%): Hook fraco. Torne os primeiros 5 segundos mais chocantes. Adicione open loops.")
        if top:
            recs.append(f"TOP PERFORMERS: Tópicos que mais converteram → replique esses ângulos.")
        if bottom:
            recs.append("UNDERPERFORMERS: Revise o hook e o thumbnail desses vídeos.")

        return {
            "status":          "ok",
            "avg_ctr":         round(avg_ctr, 3),
            "avg_retention":   round(avg_retention, 3),
            "top_videos":      top[:3],
            "recommendations": recs
        }

    # ─── PRIVATE ──────────────────────────────────────────────────────────────

    def _parse_report(self, report: dict) -> list[dict]:
        headers = [h["name"] for h in report.get("columnHeaders", [])]
        videos  = []
        for row in report.get("rows", []):
            d = dict(zip(headers, row))
            duration = float(d.get("averageViewDuration", 0))
            videos.append({
                "video_id":          d.get("video", ""),
                "views":             int(d.get("views", 0)),
                "watch_minutes":     float(d.get("estimatedMinutesWatched", 0)),
                "avg_view_duration": duration,
                "subscribers_gained":int(d.get("subscribersGained", 0)),
                "likes":             int(d.get("likes", 0)),
                "url":               f"https://youtube.com/watch?v={d.get('video','')}",
            })
        return videos

    def _save_log(self, videos: list):
        self.log_path.parent.mkdir(exist_ok=True)
        data = {
            "updated_at": datetime.now().isoformat(),
            "videos":     videos
        }
        with open(self.log_path, "w") as f:
            json.dump(data, f, indent=2)

    def _print_insights(self, videos: list):
        print("\n" + "═" * 50)
        print("📊 ANALYTICS REPORT")
        print("═" * 50)

        if not videos:
            print("No data available yet.")
            return

        total_views = sum(v["views"] for v in videos)
        total_watch = sum(v["watch_minutes"] for v in videos)
        total_subs  = sum(v["subscribers_gained"] for v in videos)

        print(f"Total views:       {total_views:,}")
        print(f"Total watch time:  {total_watch:,.0f} min ({total_watch/60:.1f} hours)")
        print(f"Subscribers gained:{total_subs}")
        print()

        print("TOP 5 VIDEOS:")
        for i, v in enumerate(videos[:5], 1):
            print(f"  {i}. {v['views']:,} views | {v['avg_view_duration']:.0f}s avg | {v['url']}")

        recs = self.get_recommendations()
        if recs["recommendations"]:
            print("\n💡 RECOMMENDATIONS:")
            for r in recs["recommendations"]:
                print(f"  → {r}")

        print("═" * 50)

    def _get_analytics_client(self):
        token_path = Path("token.pickle")
        if not token_path.exists():
            print("Not authenticated. Run upload first to generate token.")
            return None

        with open(token_path, "rb") as f:
            creds = pickle.load(f)

        if creds.expired:
            creds.refresh(Request())

        return build("youtubeAnalytics", "v2", credentials=creds)
