# Better “Listen” voice (professional AI)

The **Listen** button on blog posts uses your browser’s built-in text-to-speech. Quality depends on your device (e.g. **Google**, **Microsoft Zira/David**, or **Samantha/Daniel** on Mac). Use the **Voice** dropdown next to Listen to pick the best one available.

If you want a **professional AI voice** (e.g. for all visitors, same quality everywhere), you have two main options.

---

## Option 1: Pre-generated audio (no API key on the site)

1. When you publish a post, generate an MP3 with a service like **[Play.ht](https://play.ht)** or **[ElevenLabs](https://elevenlabs.io)** (both have free tiers).
2. Upload the MP3 (e.g. to your repo in an `audio/posts/` folder, or to a CDN).
3. On the post page, add a second button **“Play”** that plays this file instead of (or in addition to) the browser Listen button.

**Pros:** Same high quality for everyone, no API key on the site, works on static hosting.  
**Cons:** Manual step per post (or you automate it with a script).

---

## Option 2: API via a small backend (on-demand AI voice)

1. Sign up for **Play.ht** or **ElevenLabs** and get an API key.
2. Add a **serverless function** (e.g. [Netlify](https://www.netlify.com), [Vercel](https://vercel.com), or [Cloudflare Workers](https://workers.cloudflare.com)) that:
   - Accepts the post text (or post URL).
   - Calls the TTS API with your key.
   - Returns or streams the audio.
3. Point the **Listen** button on your site to this function instead of the browser TTS.

**Pros:** Professional voice on demand, no pre-generating.  
**Cons:** You need to create and deploy the function and set the API key in the backend (never in the page).

---

## Quick links

- [Play.ht – free tier & embed](https://play.ht/)
- [ElevenLabs – text to speech](https://elevenlabs.io/text-to-speech)
- [Play.ht – add audio player to website](https://help.play.ht/en/article/how-to-add-a-playht-audio-player-to-your-website-9oerst/)
