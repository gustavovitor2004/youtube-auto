# 🚀 SETUP GUIDE — YouTube Automation System
## Stack 100% Gratuito

---

## PRÉ-REQUISITOS

### 1. Python 3.10+
```bash
python --version  # Deve ser 3.10 ou superior
```

### 2. FFmpeg (OBRIGATÓRIO — edição de vídeo)
**Windows:**
- Baixe em: https://www.gyan.dev/ffmpeg/builds/
- Versão: `ffmpeg-release-essentials.zip`
- Extraia e adicione a pasta `bin/` ao PATH do Windows
- Teste: `ffmpeg -version`

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg -y
```

---

## INSTALAÇÃO

```bash
# 1. Clone ou baixe o projeto
cd youtube_auto

# 2. (Recomendado) Crie ambiente virtual
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis
cp .env.example .env
# Abra .env e preencha as keys
```

---

## CONFIGURAÇÃO: PEXELS API (grátis)

1. Acesse: https://www.pexels.com/api/
2. Crie conta gratuita
3. Vá em "Your API Key"
4. Copie a key e cole no `.env`:
   ```
   PEXELS_API_KEY=sua_key_aqui
   ```

**Limite:** 200 requests/hora — suficiente para ~10 vídeos/hora

---

## CONFIGURAÇÃO: OLLAMA (LLM local gratuito)

> Se não quiser instalar o Ollama, o sistema usa scripts prontos de fallback
> e você pode usar o Claude.ai manualmente para gerar scripts melhores.

```bash
# 1. Instale o Ollama
# Windows/Mac: https://ollama.com/download
# Linux:
curl -fsSL https://ollama.com/install.sh | sh

# 2. Baixe o modelo (faça uma vez, ~2GB)
ollama pull llama3.2

# 3. Teste
ollama run llama3.2 "Say hello"

# Para PCs com menos de 8GB RAM:
ollama pull llama3.2:1b   # Versão menor, mais rápida
# Depois altere no .env: OLLAMA_MODEL=llama3.2:1b
```

---

## CONFIGURAÇÃO: YOUTUBE API (grátis)

> Necessário apenas para fazer upload automático.
> Sem isso, o vídeo é gerado localmente e você faz upload manualmente.

### Passo a passo:

1. **Google Cloud Console**
   - Acesse: https://console.cloud.google.com/
   - Crie um projeto novo (ex: "youtube-automation")

2. **Ativar YouTube Data API v3**
   - Menu: APIs & Services → Library
   - Busque "YouTube Data API v3"
   - Clique em "Enable"

3. **Criar credenciais OAuth2**
   - APIs & Services → Credentials
   - "+ Create Credentials" → OAuth client ID
   - Application type: **Desktop app**
   - Nome: "YouTube Automation"
   - Clique em "Create"
   - **Baixe o JSON** → renomeie para `client_secrets.json`
   - Coloque na pasta raiz do projeto

4. **Configurar OAuth Consent Screen**
   - APIs & Services → OAuth consent screen
   - User Type: External
   - App name: "YouTube Automation"
   - Adicione seu email em "Test users"
   - Scopes: adicione `youtube.upload`

5. **Primeiro uso**
   - Execute com `--upload`
   - Um browser vai abrir pedindo autorização
   - Autorize com sua conta Google
   - O token é salvo em `token.pickle` (não precisa fazer isso de novo)

---

## USO

```bash
# Gerar 1 Short (modo mais simples)
python main.py

# Gerar vídeo long-form
python main.py --mode longform

# Com tópico específico
python main.py --topic "signs of a narcissist"

# Com script do Claude.ai (modo manual)
# 1. Vá ao claude.ai, peça um script, salve em script.txt
python main.py --script script.txt

# Gerar E fazer upload automaticamente
python main.py --upload

# Gerar 5 vídeos em sequência
python main.py --bulk 5

# Mudar nicho
python main.py --niche "true crime"
python main.py --niche "finance facts"

# Ver analytics do canal
python main.py --analytics
```

---

## MODO MANUAL COM CLAUDE PRO (melhor qualidade)

Como você tem Claude Pro, pode usar isso para qualidade máxima nos scripts:

### Para Shorts (copie este prompt no Claude.ai):
```
Write a 50-second YouTube Short script about: [SEU TÓPICO]

Rules:
- First line MUST be a shocking hook (no greeting, no intro)
- Use "you" in every other sentence
- Maximum 130 words
- End with a debate-triggering question
- Simple vocabulary, punchy sentences

Format: Just the narration script, nothing else.
```

### Para Long-form (copie este prompt no Claude.ai):
```
Write a 10-minute YouTube video script about: [SEU TÓPICO]

Structure:
- Cold open (30s): most shocking moment, no context
- Hook (90s): promise + open loop
- 4 sections (2-3min each): content with open loops
- Outro (30s): close loops + CTA

Rules: Use "you" constantly. Include real study names.
About 1,400 words total.

Format: Just the narration script with [SECTION] markers.
```

Salve o resultado em `script.txt` e execute:
```bash
python main.py --script script.txt
```

---

## MÚSICA DE FUNDO (opcional, melhora qualidade)

O sistema usa músicas da pasta `music/` automaticamente.
Fontes gratuitas de música sem copyright:

- **Pixabay Music:** https://pixabay.com/music/
  - Busque: "dark ambient", "thriller background", "suspense"
  - Baixe como MP3 → coloque em `music/`

- **Free Music Archive:** https://freemusicarchive.org/
  - Filtro: License = CC0 (domínio público)

- **YouTube Audio Library:** https://studio.youtube.com/
  - Menu: Áudio → Biblioteca de áudio
  - Filtro: "Dark", "Cinematic", sem atribuição

---

## ESTRUTURA DE PASTAS

```
youtube_auto/
├── main.py                    # Ponto de entrada
├── config.py                  # Configurações
├── requirements.txt
├── .env                       # Suas API keys (não commite!)
├── client_secrets.json        # YouTube OAuth (não commite!)
├── token.pickle               # Token gerado automaticamente
│
├── modules/
│   ├── trend_finder.py        # Pesquisa de tendências
│   ├── script_generator.py    # Geração de scripts (Ollama)
│   ├── voice_generator.py     # TTS (edge-tts)
│   ├── subtitle_generator.py  # Legendas (Whisper)
│   ├── video_creator.py       # Montagem (Pexels + FFmpeg)
│   ├── thumbnail_creator.py   # Thumbnail (Pillow)
│   ├── uploader.py            # Upload YouTube
│   └── analytics.py           # Análise de performance
│
├── output/                    # Vídeos finais ficam aqui
├── temp/                      # Arquivos temporários
└── music/                     # Coloque suas músicas aqui
```

---

## SOLUÇÃO DE PROBLEMAS

| Erro | Solução |
|------|---------|
| `ffmpeg: not found` | Instale FFmpeg e adicione ao PATH |
| `edge-tts` falha | `pip install edge-tts --upgrade` |
| Whisper lento | Normal na 1ª vez (baixa o modelo). Depois é rápido. |
| Pexels 401 | Verifique a PEXELS_API_KEY no .env |
| YouTube 403 | Verifique se a YouTube API está ativada no Cloud Console |
| `No module named X` | `pip install -r requirements.txt` novamente |
| Thumbnail sem fonte | Instale fontes no sistema ou aceite a fonte padrão |

---

## CUSTOS

| Item | Custo |
|------|-------|
| Python, FFmpeg, Whisper, edge-tts | **$0** |
| Pexels API (200 req/hora) | **$0** |
| YouTube Data API (10k units/dia) | **$0** |
| Ollama + Llama 3.2 | **$0** |
| Google Cloud (dentro do free tier) | **$0** |
| **TOTAL** | **$0/mês** |

---

## ROADMAP DE CRESCIMENTO

```
Semana 1-2: Setup + primeiros 20 vídeos (aprenda o sistema)
Semana 3-4: 2-3 Shorts/dia + 1 long-form/semana
Mês 2:      Chegou em 1.000 subs? Ative monetização
Mês 3:      Upgrade para ElevenLabs ($22/mês) para voz melhor
Mês 4:      Add Kling AI ($35/mês) para visuais gerados por IA
Mês 6+:     Sistema paga os upgrades com AdSense
```
