# How I built an analytics tool to track my IMVU shop (open source project)

Hey everyone,

I wanted to share a side project I've been working on. As an IMVU creator, I always struggled with understanding my shop's performance beyond the basic stats IMVU provides.

### The Problem I Was Trying to Solve

Every month I'd download my Product Stats XML, open it in Excel, and try to make sense of:
- Which products were actually profitable?
- Was my revenue trending up or down?
- Why do some products get cart adds but no purchases?

The data was there, but extracting insights was painful.

### What I Built

A simple web app that:
- Parses IMVU XML files
- Shows revenue trends over time
- Ranks products by sales/revenue
- Calculates conversion funnels (impressions → cart → purchase)
- Compares performance across different time periods

### Tech Stack

- **Backend:** Python/FastAPI
- **Frontend:** Vanilla JS + Bootstrap (keeping it simple)
- **Database:** SQLite for user data
- **AI:** DeepSeek API for insights
- **Deployed on:** Railway

### What I Learned

1. **Keep it simple** - Started with Django, switched to FastAPI for speed
2. **Users don't care about your tech stack** - They just want it to work
3. **Privacy matters** - Users are cautious about uploading sales data
4. **Free tier is essential** - Nobody pays without trying first

### Demo / Source

Live demo: https://imvucreators.com

It's not open source yet, but I'm considering it if there's interest. Happy to answer questions about the tech stack, architecture, or challenges I faced.

---

*This is a hobby project built for my own use. Sharing here in case other indie devs find the journey interesting.*

---

## 修改说明

**风格改变**：
- ❌ 不再说"Try my tool"
- ✅ 改为分享开发经验
- ✅ 强调技术栈和学习过程
- ✅ 适合 r/SideProject, r/IndieProjects

**适合发布的 Subreddit**：
1. **r/SideProject** ✅ 
2. **r/IndieProjects** ✅
3. **r/webdev** ✅ (如果强调技术)
4. **r/Python** ✅ (如果强调 FastAPI)
