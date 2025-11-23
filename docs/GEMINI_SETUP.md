# Gemini AI Integration Setup

## Get Your Free Gemini API Key

1. **Visit Google AI Studio:**
   https://makersuite.google.com/app/apikey

2. **Sign in** with your Google account

3. **Click "Create API Key"**

4. **Copy the API key**

5. **Add to `.env` file:**
   ```bash
   GEMINI_API_KEY="your-api-key-here"
   ```

## Features Enabled with Gemini

### 1. **Guardrails** 🛡️
- Only responds to warehouse/inventory queries
- Rejects off-topic questions politely
- Keywords: warehouse, inventory, stock, supply, forecast, etc.

### 2. **AI-Powered Summaries** ✨
- Executive summary of complete analysis
- Highlights key findings
- Action-oriented recommendations
- Natural language insights

### 3. **Carbon Reduction Tips** 🌱
- Personalized sustainability advice
- Packaging optimization suggestions
- Transportation efficiency tips
- Real-world examples (e.g., "500 jackets in 200 boxes")
- Estimated CO₂ savings

## Testing Without Gemini

The system works **without** a Gemini API key using fallback responses:

- ✅ All analysis features work
- ✅ Guardrails use keyword matching
- ✅ Generic summaries provided
- ✅ Standard carbon tips shown

**But with Gemini, you get:**
- 🚀 Smarter, context-aware responses
- 🚀 Personalized recommendations
- 🚀 Better natural language understanding

## Example Queries

### ✅ Valid (Warehouse-Related):
- "Analyze product WH-FP-0001 in New York"
- "Show me the forecast for WH-PC-0455"
- "Check supply chain status"
- "What's the carbon footprint?"
- "How can I reduce emissions?"

### ❌ Invalid (Will be Rejected):
- "What's the weather today?"
- "Tell me a joke"
- "How do I cook pasta?"
- "What's 2+2?"

The guardrail will politely redirect to warehouse topics!

## Cost

Gemini API is **FREE** for:
- 60 requests per minute
- 1,500 requests per day
- Perfect for this use case!

## Privacy

- API calls go directly to Google
- No data stored by Gemini
- Analysis data stays in your database
- Gemini only sees the summary request

---

**Ready to use!** Just add your API key to `.env` and restart the backend.
