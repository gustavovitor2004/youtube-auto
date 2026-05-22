"""
Script Generator — 100% gratuito
Modo 1: Ollama (LLM local, automático)
Modo 2: Claude manual (você cola o script gerado no Claude.ai)
Modo 3: Fallback interno de qualidade (quando nenhum LLM disponível)
"""

import json
import re
import requests


SHORTS_SCRIPT_PROMPT = """Write a 130-word YouTube Shorts narration script about: {topic}

Instructions:
- Do NOT say hello or introduce yourself
- Start immediately with a shocking or disturbing fact
- Use the word "you" in every paragraph
- Write short, punchy sentences (under 10 words each)
- Build tension sentence by sentence
- End with a question to provoke comments
- Write exactly around 130 words

Write ONLY the narration text. No title. No hashtags. No explanation. Just the words that will be spoken:"""

SHORTS_META_PROMPT = """Given this YouTube Shorts script, output a JSON with title, description and tags.

Script:
{script}

Output ONLY valid JSON, nothing else:
{{"title":"viral title under 60 chars","description":"60 word description with hashtags","tags":["tag1","tag2","tag3","tag4","tag5","tag6"]}}"""


LONGFORM_PROMPT = """You are an elite YouTube scriptwriter for dark psychology content.

Write a 10-minute video script about: "{topic}"

Structure:
[COLD OPEN 0:00] Shocking moment, no context
[HOOK 0:30] Promise + open loop  
[SECTION 1 2:00] Foundation + statistic
[SECTION 2 4:30] Core content + case studies
[SECTION 3 7:00] The twist/revelation
[SECTION 4 9:30] Practical application
[OUTRO 11:00] Close loops + CTA

Rules: 1400-1600 words. Use "you" constantly. Real study names for credibility.

OUTPUT: Valid JSON only.
{{"title":"clickbait title under 70 chars","script":"complete word-for-word script","description":"200 word SEO description","tags":["tag1","tag2","tag3","tag4","tag5","tag6","tag7","tag8"],"chapters":[{{"time":"0:00","title":"chapter name"}}]}}

Topic: {topic}"""


# ─── SCRIPTS DE FALLBACK — 8 TEMAS DISTINTOS ──────────────────────────────────

FALLBACK_SHORTS_SCRIPTS = [
    # 1. MANIPULATION / CONTROL
    {
        "theme": "manipulation",
        "keywords": ["manipulat", "control", "trick", "illusion", "choice", "exploit"],
        "script": """Most people are being psychologically manipulated right now — and they'll never figure it out.

Every decision you think you're making freely? It's been engineered.

Psychologists call it the Illusion of Choice. The people who design your apps, your grocery stores, your social media feeds — they know exactly how to exploit it.

Here's what makes it terrifying: the more intelligent you are, the MORE susceptible you become. Your brain is so good at finding patterns that it's easier to feed you false ones.

There are three specific triggers being used on you daily. Once you know them, you can't be manipulated the same way again.

The first one is happening to you right this second.

Have you ever noticed yourself doing something without knowing why? Comment below.""",
        "title": "You're Being Psychologically Controlled Right Now",
        "tags": ["dark psychology", "manipulation", "psychology facts", "mind control",
                 "psychological tricks", "behavior", "human psychology", "brain"]
    },
    # 2. BRAIN / CURIOSITY
    {
        "theme": "brain",
        "keywords": ["brain", "mind", "neuroscien", "decision", "thought", "conscious", "scroll", "dopamine"],
        "script": """Your brain makes 35,000 decisions every day. You're consciously aware of maybe 100 of them.

The rest? Made by systems running completely outside your control.

This is System 1 thinking. And the people who understand it — app engineers, advertisers, casino designers — use it against you constantly.

Here's one example that will change how you see everything. The color red triggers urgency and appetite in your brain. That's why every fast food chain uses it. That's why sale tags are red. That's why notification dots are red.

None of this is coincidence. All of it was designed after decades of studying exactly how your brain responds.

You've been living inside a psychological experiment your entire life. And until this second — you didn't even know you were a subject.

What do you do automatically without knowing why? Tell me below.""",
        "title": "Your Brain Makes 35,000 Decisions Daily — Here's Who Controls Them",
        "tags": ["brain facts", "psychology", "dark psychology", "decision making",
                 "dopamine", "human behavior", "cognitive bias", "neuroscience"]
    },
    # 3. NARCISSISM / TOXIC PEOPLE
    {
        "theme": "narcissism",
        "keywords": ["narcissist", "toxic", "hate", "fake", "nice", "secretly", "enemy", "pretend"],
        "script": """Narcissists don't choose their victims randomly. They follow a precise psychological pattern — and you might already be a target.

Research shows narcissists go after three specific types. Empathetic people. High achievers. And people with unhealed emotional wounds.

Sound familiar?

The manipulation begins before you notice anything is wrong. A compliment here. An intense connection there. They mirror your personality so perfectly you feel understood for the first time in your life.

That feeling isn't real connection. It's a calculated trap.

The moment you're fully attached, the real behavior appears. Criticism disguised as concern. Isolation framed as protection. Control wrapped in love.

The most disturbing part? By that point, your brain is chemically bonded to them.

Do you know someone like this? Comment below.""",
        "title": "Why Narcissists Choose YOU Specifically",
        "tags": ["narcissist", "dark psychology", "toxic relationship", "manipulation",
                 "narcissistic abuse", "psychology", "human behavior", "red flags"]
    },
    # 4. CREEPY / DARK FACTS
    {
        "theme": "creepy",
        "keywords": ["disturb", "creep", "dark", "truth", "secret", "hidden", "scary", "terrif", "horrify"],
        "script": """There are psychological facts about humans so disturbing that most scientists refuse to discuss them publicly.

Fact one: You have a second brain in your gut with more neurons than a cat's entire brain. It makes decisions before your conscious mind even knows something happened.

Fact two: Your brain physically changes shape when someone rejects you. A breakup causes the same neural damage as a broken bone. The pain is real — and it's structural.

Fact three: When you imagine doing something evil — even briefly — your brain cannot distinguish it from actually doing it. The same neural pathways fire.

Fact four: You are statistically surrounded by people who are lying to your face every single day. Research says you'll be lied to over 200 times before tonight.

Which of these disturbs you most? Tell me in the comments.""",
        "title": "4 Disturbing Facts About Humans Scientists Won't Tell You",
        "tags": ["disturbing facts", "dark psychology", "psychology facts", "brain facts",
                 "creepy facts", "human behavior", "dark truth", "psychology"]
    },
    # 5. SOCIAL MEDIA / ADDICTION
    {
        "theme": "addiction",
        "keywords": ["scroll", "social media", "tiktok", "instagram", "phone", "addict", "stop", "app", "algorithm"],
        "script": """The app you're using right now was designed by teams of psychologists specifically to make you unable to stop.

This isn't a theory. Former engineers from Meta, TikTok, and Google have confirmed it publicly.

Here's the mechanism: every time you open the app and something interesting appears, your brain releases a small hit of dopamine. Same as cocaine. Same pathway. Same effect.

But they didn't stop there. They made the reward unpredictable — you don't know when the next interesting thing will appear. And unpredictable rewards are the most addictive kind. That's why slot machines work.

You're not scrolling because you want to. You're scrolling because you've been conditioned to. Like a lab rat pressing a lever.

The fact that you're watching this right now — through the same mechanism — is the most disturbing part.

How many hours did you scroll today? Be honest below.""",
        "title": "Your Phone Was Designed to Be More Addictive Than Cocaine",
        "tags": ["social media addiction", "dark psychology", "dopamine", "phone addiction",
                 "psychology", "algorithm", "brain", "tech psychology"]
    },
    # 6. SLEEP / DREAMS (curiosity/fun angle)
    {
        "theme": "sleep",
        "keywords": ["sleep", "dream", "night", "unconscious", "memory", "rest", "tired", "insomnia"],
        "script": """While you sleep tonight, something terrifying will happen inside your brain — and there's nothing you can do to stop it.

Your brain will systematically delete memories it considers unimportant. It decides which experiences define you and which ones disappear forever. You don't vote on this.

But it gets darker. During REM sleep, your brain paralyzes your entire body. Completely. The reason? So you don't act out your dreams and hurt yourself. Your mind literally doesn't trust your body.

And here's the most unsettling part: the version of you that wakes up tomorrow is not quite the same person who fell asleep tonight. The deletions have already happened. The person you were yesterday is already partially gone.

Sleep scientists call it memory consolidation. I call it a nightly personality rewrite you never consented to.

What's the most vivid dream you remember? Drop it below.""",
        "title": "What Your Brain Does to You Every Night While You Sleep",
        "tags": ["sleep psychology", "brain facts", "dark psychology", "dreams", "REM sleep",
                 "memory", "neuroscience", "psychology facts"]
    },
    # 7. MONEY / SUCCESS DARK SIDE
    {
        "theme": "money",
        "keywords": ["money", "rich", "success", "casino", "gambling", "wealth", "poor", "work", "boss"],
        "script": """Everything you believe about money was taught to you by people who benefit from you staying poor.

This isn't conspiracy. It's documented psychology.

Rich people think about money completely differently than everyone else. And the gap isn't intelligence. It's not luck. It's one specific psychological framework — and you were never taught it.

Here's what wealthy people know that you don't: every dollar is either working for you or against you. There is no neutral money. Your savings account is actively making you poorer right now — while someone else uses your deposited money to get richer.

The rules of the financial game were written before you were born. You've been playing to survive. They've been playing to win.

Most people spend their entire life not knowing the board even exists.

What would you do with financial freedom? Tell me below.""",
        "title": "Why You Were Taught to Be Poor — Dark Psychology of Money",
        "tags": ["money psychology", "dark psychology", "wealth mindset", "financial psychology",
                 "psychology of money", "rich vs poor", "mindset", "success psychology"]
    },
    # 8. RELATIONSHIPS / LOVE DARK SIDE
    {
        "theme": "love",
        "keywords": ["love", "relationship", "partner", "attract", "dating", "heart", "feel", "emotion", "bond"],
        "script": """The person you fall in love with isn't a choice. It's a psychological profile your brain built when you were a child — and has been searching for ever since.

Psychologists call it the love map. It's a subconscious blueprint made up of your earliest experiences. The specific tone of voice that calms you. The type of humor that makes you feel safe. The emotional unavailability you keep mistaking for mystery.

Here's the disturbing part: most people are attracted to what's familiar — not what's healthy. You're not attracted to partners who are good for you. You're attracted to partners who match your earliest psychological wounds.

This is why you keep repeating the same relationship patterns. It's not bad luck. It's not bad judgment. It's your brain running the same psychological code it wrote before you were old enough to understand it.

Do you recognize this pattern in your life? Tell me honestly below.""",
        "title": "Why You Fall for the Wrong People — Dark Psychology of Love",
        "tags": ["love psychology", "dark psychology", "relationship psychology", "attachment",
                 "psychology of attraction", "toxic relationships", "mindset", "human behavior"]
    },
]

FALLBACK_LONGFORM = {
    "title": "The Dark Psychology Experiment That Proved Anyone Can Be Controlled",
    "description": "The Stanford Prison Experiment revealed something terrifying about human psychology and dark personality traits. This video breaks down the Dark Triad, Robert Cialdini's research, and how to build psychological immunity against manipulation.\n\n#darkpsychology #psychology #manipulation",
    "tags": ["dark psychology", "stanford prison experiment", "manipulation", "psychology",
             "dark triad", "narcissism", "psychopathy", "influence", "robert cialdini",
             "mind control", "behavior", "psychological manipulation"],
    "chapters": [
        {"time": "0:00", "title": "The Experiment That Changed Everything"},
        {"time": "2:00", "title": "The Dark Triad Explained"},
        {"time": "4:30", "title": "The Three Invisible Weapons"},
        {"time": "7:00", "title": "What Stanford Really Revealed"},
        {"time": "9:30", "title": "How to Protect Yourself"}
    ],
    "script": """[COLD OPEN]
In 1971, a Stanford psychologist ran an experiment so disturbing it had to be stopped after just six days. Ordinary students became monsters — not because they were evil — but because of a single psychological mechanism that lives inside every human brain. Including yours.

[HOOK]
What you're about to learn isn't just history. It's a warning. Because the same force that turned those students into something unrecognizable is actively shaping your behavior right now. And by the end of this video, you'll never see your own decisions the same way again.

But first — I need to tell you about something called the Dark Triad. We'll get to the Stanford experiment in a moment. But what I'm about to reveal first changes everything about how you interpret that story.

[SECTION 1]
Psychologists have identified three personality traits that, when combined, create what they call the most dangerous psychological profile in existence. Narcissism. Machiavellianism. And psychopathy.

Every human being has some degree of all three. The difference between someone who's mildly self-interested and someone who will destroy your life without losing sleep? It's not the presence of these traits. It's the degree. And the control.

A 2019 study in the Journal of Personality found that one in five people you interact with regularly scores high enough on these scales to be classified as psychologically dangerous. One in five. Think about the last five people you spent time with.

[SECTION 2]
The most effective manipulation doesn't look like manipulation at all.

Dr. Robert Cialdini spent thirty-five years studying influence. His conclusion? The most powerful psychological weapons are invisible. They work below conscious awareness. And they exploit the exact cognitive shortcuts your brain uses to function efficiently.

The first weapon is reciprocity. When someone does something for you — even something small you didn't ask for — your brain creates an automatic debt. Skilled manipulators use this constantly. A small gift. An unexpected compliment. A favor you didn't request. All calculated to create obligation.

The second weapon is social proof. Your brain is wired to assume that if others are doing something, it must be correct. This made sense for survival thousands of years ago. Today it's being weaponized in advertising, social media, and your closest relationships.

The third weapon — remember this — is manufactured scarcity. When something seems rare, your brain automatically assigns it higher value. Whether that's a product, an opportunity, or a person's attention. We're coming back to this.

[SECTION 3]
Now back to Stanford. 1971. Professor Philip Zimbardo randomly assigned students to be guards or prisoners in a mock prison. Within 24 hours, the guards began psychologically abusing the prisoners. Within 36 hours, the first prisoner had a complete breakdown. By day six, Zimbardo himself had become so absorbed in his role that he almost let it continue.

The conclusion that shocked the world: it wasn't the people who were broken. It was the situation. Change the context, and ordinary people do extraordinary evil.

But here's what Zimbardo's later research revealed — what the famous experiment actually missed. A small number of guards never participated in the abuse. Not once. Even under immense social pressure. What made them different?

Psychological autonomy. They were aware of the manipulation happening around them. That awareness alone was enough to protect them.

This is exactly why what you're learning right now matters.

[SECTION 4]
How do you build that same psychological autonomy?

Step one: Name it. When you feel an unusual obligation, sudden urgency, or intense desire to impress someone specific — stop. Name the mechanism out loud. "This is reciprocity being used on me." The moment you name a psychological trigger, its power drops by over forty percent, according to research from NYU's psychology department.

Step two: Create a twenty-four hour buffer. Before any significant decision in a high-pressure situation — walk away for twenty-four hours. Manipulative contexts depend on momentum. Remove the momentum, the illusion collapses.

Step three: Watch for the cluster. A single dark trait can be manageable. But when you see someone who simultaneously uses guilt, intermittent rewards, social isolation, and manufactured urgency — trust your pattern recognition. Your gut already knows.

[OUTRO]
The Stanford Prison Experiment taught us that context can override character. But it also taught us this: awareness is armor.

The people who never abused their power weren't stronger or born different. They simply knew something the others didn't. They saw the game being played.

Now you do too.

If someone came to mind while watching this — that's your brain trying to tell you something. Pay attention to it.

Next video, I break down the exact phrases psychological manipulators use — and the words that immediately neutralize their power.

Subscribe so you don't miss it. And drop a comment — what manipulation tactic have you experienced?"""
}


class ScriptGenerator:
    def __init__(self, config):
        self.config = config
        self.ollama_url = f"{config.OLLAMA_BASE_URL}/api/generate"
        self._ollama_available = None
        self._fallback_idx = 0  # Rotaciona entre os fallbacks

    def generate(self, topic: str, mode: str) -> dict:
        if mode == "shorts":
            return self._generate_shorts(topic)
        return self._generate_longform(topic)

    def generate_from_manual_script(self, topic: str, script_text: str, mode: str) -> dict:
        """Usa quando o script foi gerado manualmente no Claude.ai."""
        clean_topic = self._clean_topic_for_title(topic)
        title = f"The Hidden Truth About {clean_topic}"
        desc  = f"Discover the dark psychology behind {topic.lower()}. Mind-blowing psychological facts explained.\n\n#psychology #darkpsychology #mindset"
        tags  = ["dark psychology", "psychology facts", topic.lower()] + \
                ["mind", "psychology", "manipulation", "brain", "behavior"]
        base = {"title": title, "script": script_text, "description": desc, "tags": tags}
        if mode == "longform":
            base["chapters"] = [{"time": "0:00", "title": "Introduction"}]
        return base

    def _generate_shorts(self, topic: str) -> dict:
        MIN_WORDS = 80

        # Passo 1: gera só o texto do script
        script_text = self._call_ollama(SHORTS_SCRIPT_PROMPT.format(topic=topic))

        if script_text:
            # Limpa qualquer JSON acidental que o modelo possa ter colocado
            script_text = re.sub(r"```.*?```", "", script_text, flags=re.DOTALL).strip()
            script_text = re.sub(r'^\{.*?"script"\s*:\s*"', "", script_text, flags=re.DOTALL)
            script_text = re.sub(r'"\s*\}.*$', "", script_text, flags=re.DOTALL).strip()

            word_count = len(script_text.split())
            print(f"   [OK] Script word count: {word_count} words")

            if word_count >= MIN_WORDS:
                # Passo 2: pede metadata separado (titulo, tags)
                meta_raw = self._call_ollama(SHORTS_META_PROMPT.format(script=script_text[:800]))
                meta = self._parse_json(meta_raw) if meta_raw else {}
                if not meta or "title" not in meta:
                    meta = {}

                return self._clean_output({
                    "script":      script_text,
                    "title":       meta.get("title", ""),
                    "description": meta.get("description", ""),
                    "tags":        meta.get("tags", []),
                }, topic)

        # Fallback por tema — escolhe o script mais relevante para o topico
        print(f"   [i] Using themed fallback script")
        fb = self._pick_fallback(topic)
        return {
            **{k: v for k, v in fb.items() if k != "theme" and k != "keywords"},
            "description": f"{fb['title']}. Dark psychology facts you need to know. #darkpsychology #psychology #{fb.get('theme','mindset')}",
        }

    def _pick_fallback(self, topic: str) -> dict:
        """Escolhe o fallback mais adequado ao topico por palavras-chave."""
        topic_lower = topic.lower()
        best_score = -1
        best_fb = None
        for fb in FALLBACK_SHORTS_SCRIPTS:
            score = sum(1 for kw in fb.get("keywords", []) if kw in topic_lower)
            if score > best_score:
                best_score = score
                best_fb = fb
        # Se nenhuma keyword bateu, rotaciona
        if best_score == 0:
            best_fb = FALLBACK_SHORTS_SCRIPTS[self._fallback_idx % len(FALLBACK_SHORTS_SCRIPTS)]
        self._fallback_idx += 1
        return best_fb

    def _generate_longform(self, topic: str) -> dict:
        raw = self._call_ollama(LONGFORM_PROMPT.format(topic=topic), max_tokens=4000)
        if raw:
            parsed = self._parse_json(raw)
            if parsed and "script" in parsed:
                return self._clean_output(parsed, topic)
        return dict(FALLBACK_LONGFORM)

    def _clean_output(self, data: dict, topic: str) -> dict:
        """Limpa e valida o output do LLM."""
        # Garante que o título não seja o tópico bruto
        if "title" not in data or len(data["title"]) < 5:
            data["title"] = f"The Dark Truth About {self._clean_topic_for_title(topic)}"

        # Remove title case estranho (ex: "The Dark Truth About Mind'S")
        data["title"] = self._fix_title(data["title"])

        if "description" not in data:
            data["description"] = f"{data['title']}. Psychology facts explained. #darkpsychology"
        if "tags" not in data:
            data["tags"] = ["dark psychology", "psychology", "manipulation", topic[:30]]

        return data

    def _fix_title(self, title: str) -> str:
        """Corrige casing do título: capitaliza cada palavra, preserva siglas."""
        title = title.replace("...", "").strip()
        if len(title) > 80:
            title = title[:77] + "..."

        fixed = []
        for word in title.split():
            letters = [c for c in word if c.isalpha()]
            if not letters:
                fixed.append(word)
                continue
            is_all_upper = all(c.isupper() for c in letters)
            if is_all_upper and len(letters) <= 5:
                # Sigla curta (PTSD, AI, CNN) → preserva
                fixed.append(word)
            else:
                # Tudo mais → capitaliza primeira letra, resto minúsculo
                fixed.append(word.capitalize())
        return " ".join(fixed)

    def _clean_topic_for_title(self, topic: str) -> str:
        """Converte um tópico bruto em algo adequado para título."""
        # Remove artigos no início
        topic = re.sub(r"^(the|a|an)\s+", "", topic.lower()).strip()
        # Title case limpo
        return topic.title()[:50]

    def _call_ollama(self, prompt: str, max_tokens: int = 2000) -> str | None:
        if self._ollama_available is None:
            self._ollama_available = self._check_ollama()
        if not self._ollama_available:
            print("   ℹ️  Ollama not running — using built-in fallback script")
            print("   💡 TIP: Install Ollama (ollama.com) + run 'ollama pull llama3.2' for auto-generation")
            return None
        try:
            print(f"   Generating with Ollama ({self.config.OLLAMA_MODEL})...")
            r = requests.post(
                self.ollama_url,
                json={"model": self.config.OLLAMA_MODEL, "prompt": prompt,
                      "stream": False, "options": {"temperature": 0.85, "top_p": 0.9,
                                                    "num_predict": max_tokens}},
                timeout=180
            )
            if r.status_code == 200:
                text = r.json().get("response", "")
                print(f"   ✓ Generated {len(text)} chars")
                return text
        except requests.exceptions.ConnectionError:
            self._ollama_available = False
        except Exception as e:
            print(f"   ✗ Ollama error: {e}")
        return None

    def _check_ollama(self) -> bool:
        try:
            r = requests.get(f"{self.config.OLLAMA_BASE_URL}/api/tags", timeout=3)
            return r.status_code == 200
        except:
            return False

    def _parse_json(self, text: str) -> dict | None:
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*",     "", text)
        start, end = text.find("{"), text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
            try:
                snippet = re.sub(r",\s*}", "}", text[start:end])
                snippet = re.sub(r",\s*]", "]", snippet)
                return json.loads(snippet)
            except:
                pass
        return None
