"""
Trend Finder — 100% gratuito
Usa: pytrends (Google Trends), Reddit (sem key), banco curado de tópicos
"""

import random
import time
import re

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

# ─── Banco de tópicos curados — sempre funciona ───────────────────────────────
CURATED_TOPICS = {
    "dark psychology": [
        "manipulation tactics most people don't recognize",
        "psychological tricks used to control you every single day",
        "signs someone is psychologically manipulating you right now",
        "cognitive biases that make you easy to manipulate",
        "the psychology of why you can't stop scrolling",
        "how narcissists secretly control their victims",
        "dark personality traits science actually explains",
        "why smart people are easier to manipulate",
        "the silent manipulation happening in every conversation",
        "psychological weapons used in advertising against you",
        "how to spot a liar using body language",
        "gaslighting: how to know if you're a victim right now",
        "the 6 manipulation tactics used by every narcissist",
        "why you do things without knowing why — explained",
        "the dark reason people stay in toxic relationships",
    ],
    "psychology facts": [
        "mind-blowing psychology facts about human behavior",
        "why your brain tricks you every single day",
        "psychological facts about attraction science confirmed",
        "the science behind why you procrastinate",
        "what your dreams actually mean according to science",
        "psychology facts that will change how you see yourself",
    ],
    "finance": [
        "money secrets the rich don't want you to know",
        "financial mistakes that keep you poor forever",
        "how the banking system really works",
        "passive income streams that actually work",
        "the truth about credit scores nobody tells you",
    ],
    "true crime": [
        "the crime that shocked the entire world",
        "criminal psychology: why killers do what they do",
        "the most disturbing unsolved cases in history",
        "inside the mind of a serial killer",
        "cold cases finally solved by DNA evidence",
    ],
}

# Palavras que indicam que o título veio de um artigo científico (não usar)
ACADEMIC_KEYWORDS = [
    "study", "research", "scientists", "substantially",
    "increased risk", "new study", "findings", "participants",
    "according to", "published", "journal", "percent of",
    "survey", "researchers", "analysis", "data show",
]

# Palavras que indicam bom tópico de vídeo
VIDEO_KEYWORDS = [
    "secret", "dark", "hidden", "truth", "signs", "why",
    "how", "never", "actually", "really", "exposed",
    "you", "your", "people", "someone", "everyone",
]


class TrendFinder:
    def __init__(self):
        self.session = requests.Session() if REQUESTS_OK else None
        if self.session:
            self.session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            })

    def get_trending_topics(self, niche: str, count: int = 5) -> list[str]:
        print(f"   Searching trends for niche: '{niche}'...")
        topics = []

        # Google Trends (pode dar 429 — é ok, tem fallback)
        try:
            from pytrends.request import TrendReq
            pytrends = TrendReq(hl="en-US", tz=0, timeout=(5, 15))
            pytrends.build_payload([niche], timeframe="now 7-d", geo="")
            related = pytrends.related_queries()
            data = related.get(niche, {})
            if data and data.get("top") is not None:
                gt = data["top"]["query"].tolist()[:5]
                topics.extend(gt)
                print(f"   ✓ Google Trends: {len(gt)} topics")
        except Exception as e:
            # 429 = rate limited. Acontece sempre quando roda muitas vezes.
            # Não é problema — o banco curado cobre isso.
            print(f"   ℹ️  Google Trends unavailable (rate limit) — using curated topics")

        # Reddit (sem autenticação)
        if REQUESTS_OK:
            try:
                reddit = self._reddit_trending(niche)
                topics.extend(reddit)
                if reddit:
                    print(f"   ✓ Reddit: {len(reddit)} topics")
            except Exception:
                pass

        # Banco curado (sempre roda, garante qualidade)
        curated = self._curated_fallback(niche)
        topics.extend(curated)

        # Filtra e rankeia
        filtered = self._filter_and_rank(topics)

        result = filtered[:count]
        if result:
            print(f"   → Selected top topic: \"{result[0][:70]}...\"" if len(result[0]) > 70 else f"   → Selected top topic: \"{result[0]}\"")
        return result

    # ─── REDDIT ───────────────────────────────────────────────────────────────

    def _reddit_trending(self, niche: str) -> list[str]:
        subreddits_map = {
            "dark psychology": ["psychology", "manipulation", "raisedbynarcissists", "NarcissisticAbuse"],
            "finance":         ["personalfinance", "financialindependence"],
            "true crime":      ["truecrime", "UnresolvedMysteries"],
            "psychology facts":["psychology", "YouShouldKnow", "todayilearned"],
        }
        key  = niche.lower()
        subs = subreddits_map.get(key, ["psychology", "YouShouldKnow"])

        topics = []
        for sub in subs[:2]:
            try:
                url = f"https://www.reddit.com/r/{sub}/hot.json?limit=10&t=week"
                r   = self.session.get(url, timeout=10)
                if r.status_code == 200:
                    posts = r.json()["data"]["children"]
                    for p in posts:
                        title = p["data"]["title"]
                        converted = self._reddit_to_video_topic(title, niche)
                        if converted:
                            topics.append(converted)
                time.sleep(0.5)
            except Exception:
                continue
        return topics[:4]

    def _reddit_to_video_topic(self, title: str, niche: str) -> str | None:
        """
        Converte título de post do Reddit em tópico de vídeo.
        Retorna None se o título for acadêmico/impróprio.
        """
        title_lower = title.lower()

        # Rejeita títulos acadêmicos
        if any(kw in title_lower for kw in ACADEMIC_KEYWORDS):
            return None

        # Rejeita títulos muito curtos ou muito longos
        words = title.split()
        if len(words) < 4 or len(words) > 20:
            return None

        # Rejeita perguntas pessoais ("My mom...", "I think...", "Am I...")
        personal_starts = ["my ", "i ", "am i", "aita", "update:", "[update"]
        if any(title_lower.startswith(p) for p in personal_starts):
            return None

        # Limpa e formata como tópico de vídeo
        title = re.sub(r'\[.*?\]', '', title).strip()
        title = re.sub(r'\(.*?\)', '', title).strip()
        title = title.rstrip("?!.")

        if len(title.split()) < 4:
            return None

        return title[:100]

    # ─── CURATED ──────────────────────────────────────────────────────────────

    def _curated_fallback(self, niche: str) -> list[str]:
        key = niche.lower()
        for k, topics in CURATED_TOPICS.items():
            if k in key or key in k:
                shuffled = topics.copy()
                random.shuffle(shuffled)
                return shuffled
        return [
            f"dark secrets about {niche} nobody talks about",
            f"the truth about {niche} that will change how you see it",
            f"psychological facts about {niche} explained",
        ]

    # ─── FILTER & RANK ────────────────────────────────────────────────────────

    def _filter_and_rank(self, topics: list[str]) -> list[str]:
        """Pontua e ordena tópicos por qualidade de vídeo."""
        scored = []
        seen   = set()

        for t in topics:
            t = t.strip()
            key = t.lower()[:50]
            if key in seen or len(t) < 15:
                continue
            seen.add(key)

            # Rejeita imediatamente se parecer acadêmico
            if any(kw in t.lower() for kw in ACADEMIC_KEYWORDS):
                continue

            score = 0
            words = t.split()
            score += min(len(words), 10)          # Mais palavras = melhor (até 10)
            score -= 5 if len(words) > 18 else 0  # Muito longo = pior
            score -= 3 if t.lower().startswith("the ") and len(words) < 5 else 0

            # Bônus por palavras-chave de vídeo viral
            score += sum(2 for kw in VIDEO_KEYWORDS if kw in t.lower())

            scored.append((score, t))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored]
