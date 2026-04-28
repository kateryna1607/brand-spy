import os
import json
import requests
from datetime import datetime
from pathlib import Path
from agent.tools import fetch_universal_content
from agent.reporter import generate_report

class UniversalPriceAgent:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.api_key = os.getenv("GROQ_API_KEY")
        self.results = {}

    def run(self, url, lang="en"):
        if not self.api_key:
            return None, "No GROQ_API_KEY found."

        if self.dry_run:
            self._handle_dry_run(url)
            return self._save_report(), None

        text = fetch_universal_content(url)
        if not text:
            return None, "Target website blocked access. The website firewall (e.g. Cloudflare) blocks bots. Try running locally or checking the URL."

        analysis = self._extract_with_groq(url, text, lang)
        if not analysis:
            return None, "AI analysis failed (Groq API error)."

        analysis['_lang'] = lang
        self.results[url] = analysis
        return self._save_report(), None

    def _save_report(self):
        report_dir = Path("output")
        report_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = report_dir / f"premium_report_{timestamp}.html"
        generate_report(self.results, str(output_file))
        return str(output_file)

    def _extract_with_groq(self, url, text, lang):
        lang_names = {"en": "English", "fr": "French", "ru": "Russian"}
        target_lang = lang_names.get(lang, "English")

        prompt = f"""
        You are an elite competitor analysis AI, specializing in high-ticket positioning, business strategy, and luxury brand psychology.
        Conduct an ultra-detailed, deep dive strategic audit of the following competitor website: {url}
        You are charging €5,000 for this report. It must be exceptionally detailed, incisive, and provide a 20-page-worth of actionable insight. 
        All text fields MUST be explicitly translated and written fluently in {target_lang}.
        CRITICAL: Make the text engaging and structurally easy to read. You MUST use Markdown formatting inside the JSON strings!
        - Use **bold text** for crucial concepts.
        - Embellish your content with relevant emojis (🚀, 💡, 💰, 🎯, 🔥) to make it look premium but engaging.
        - Use bullet points (start lines with "- ")
        - Include hyper-relevant URLs and references formatted as markdown links [click here](https://...) where applicable.
        - Focus on clear, step-by-step actionable recommendations grouped by category. when listing strategies, ideas, or complex points.
        - Structure your paragraphs. Give at least 3-5 sentences per analytical paragraph, broken up with bold points and lists.
        Never write 'string', provide real, deep analytical content. Give at least 3-5 sentences per analytical paragraph.

        Return ONLY a strictly valid JSON object matching this exact schema:
        {{
            "competitor_name": "String (Name of the brand or company)",
            "executive_summary": "String (An extensive, 3-5 paragraph summary detailing their history, trajectory, leadership aura, and market dominance)",
            "market_positioning": {{
                "tier": "String (e.g. Accessible Luxury, Hyper-Premium Niche, Mass Market Premium)",
                "perceived_valuation": "String (Estimated brand perception/valuation scale)",
                "core_promise": "String (The fundamental promise they sell to the client)"
            }},
            "the_vulnerability_gap": {{
                "description": "String (Where is the exact crack in their armor? Where are they failing to serve their clients?)",
                "attack_angle": "String (How exactly can a competitor exploit this gap? Give a specific actionable strategy.)",
                "estimated_roi_opportunity": "String (High/Medium/Low with a 1-sentence justification)"
            }},
            "target_audience_psychology": {{
                "demographics": "String",
                "fears_and_pain_points": ["String", "String", "String", "String"],
                "desires_and_aspirations": ["String", "String", "String", "String"],
                "objection_handling_tactics": "String (How they handle client doubts implicitly on their site)"
            }},
            "threat_level": 8, // Integer 1-10
            "swot_analysis": {{
                "strengths": ["Lengthy analysis 1", "Lengthy analysis 2", "Lengthy analysis 3"],
                "weaknesses": ["Lengthy analysis 1", "Lengthy analysis 2", "Lengthy analysis 3"],
                "opportunities": ["Lengthy analysis 1", "Lengthy analysis 2", "Lengthy analysis 3"],
                "threats": ["Lengthy analysis 1", "Lengthy analysis 2"]
            }},
            "brand_archetype_scores": {{
                "innovation": 85,
                "luxury_prestige": 90,
                "trust_authority": 75,
                "accessibility": 40,
                "digital_fluency": 80,
                "customer_intimacy": 60
            }},
            "competency_matrix": {{
                "branding_design": 90,
                "marketing_funnels": 85,
                "sales_closing": 70,
                "tech_infrastructure": 60,
                "client_success_signals": 50
            }},
            "pricing_architecture_analysis": "String (Analysis of how they structure their pricing, framing, and anchoring)",
            "content_and_seo_strategy": {{
                "primary_channels": ["String", "String"],
                "tone_of_voice": "String",
                "key_themes": ["String", "String", "String"],
                "estimated_traffic_trend": [50, 60, 65, 80, 90, 85] // Array of 6 integers representing a 6-month simulated trend
            }},
            "cta_tactics": ["String", "String", "String"],
            "products": [
                {{
                    "name": "String",
                    "price_estimate": 0,
                    "trend": "up|down|stable",
                    "unique_selling_point": "String (Detailed)",
                    "perceived_value": "ultra-premium|premium|standard|entry"
                }}
            ],
            "technological_sophistication": "String (Deep analysis of their website tech stack, UX/UI quality, and digital friction)",
            "blue_ocean_recommendations": [
                {{"title": "String", "strategy": "String (Detailed strategy)"}},
                {{"title": "String", "strategy": "String (Detailed strategy)"}}
            ]
        }}
        
        Website Text content to analyze:
        {text[:25000]}
        """

        models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"]
        
        for model in models:
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "response_format": {"type": "json_object"}
                    },
                    timeout=60
                )
                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    return json.loads(content)
                else:
                    print(f"Groq error {response.status_code}: {response.text}")
            except Exception as e:
                print(f"Exception with {model}: {e}")
        return None

    def _handle_dry_run(self, url):
        self.results[url] = {
            "_lang": "en",
            "competitor_name": "Test Competitor Luxury",
            "executive_summary": "Test Competitor is an apex entity operating in the ultra-luxury digital space. They have consistently demonstrated a profound ability to capture high-net-worth individuals through aggressive minimalism and intense exclusivity loops.\n\nTheir trajectory points heavily towards creating closed-door communities, isolating their clients from the broader market to instill a sense of absolute prestige. This creates a moat that is inherently difficult to bypass.\n\nHowever, beneath the elite veneer, their digital infrastructure shows signs of aging, relying heavily on manual concierge services rather than streamlined automation, which throttles their true scalability.",
            "market_positioning": {
                "tier": "Hyper-Premium Niche",
                "perceived_valuation": "$100M - $150M",
                "core_promise": "Absolute exclusivity and elite peer-level networking."
            },
            "the_vulnerability_gap": {
                "description": "Their reliance on manual concierge scaling creates a massive bottleneck. High-net-worth clients nowadays expect instant, high-fidelity digital delivery alongside the human touch.",
                "attack_angle": "Deploy a heavily automated, AI-augmented white-glove service that mimics human exclusivity but delivers value instantaneously.",
                "estimated_roi_opportunity": "High (Untapped digital efficiency)"
            },
            "target_audience_psychology": {
                "demographics": "C-Level Executive, 40-55 years old, High Net Worth",
                "fears_and_pain_points": [
                     "Fear of becoming obsolete in a fast-moving market",
                     "Fear of associating with lower-tier brands",
                     "Pain of dealing with disorganized luxury providers",
                     "Anxiety regarding legacy and long-term prestige"
                ],
                "desires_and_aspirations": [
                     "Absolute control over their time",
                     "Access to closed-door, elite networks",
                     "Status reinforcement",
                     "Frictionless scaling of their own assets"
                ],
                "objection_handling_tactics": "By putting prices behind application walls, they immediately invalidate price-shoppers and frame the relationship as 'you must qualify for us'."
            },
            "threat_level": 8,
            "swot_analysis": {
                "strengths": [
                     "Unparalleled brand aura of scarcity and exclusivity",
                     "High ticket ascension model strictly enforces LTV",
                     "Extremely tight-knit, high-profile existing network"
                ],
                "weaknesses": [
                     "Outdated digital infrastructure causing UX friction",
                     "Over-reliance on manual human capital for fulfillment",
                     "Poor organic traffic architecture"
                ],
                "opportunities": [
                     "Integration of sophisticated AI for instant fulfillment",
                     "Down-sell of digital assets to a mid-tier audience",
                     "Global expansion beyond their primary European hub"
                ],
                "threats": [
                     "New competitors entering with aggressive AI-powered operations",
                     "Economic cooling affecting pure-luxury discretionary spending"
                ]
            },
            "brand_archetype_scores": {
                "innovation": 40,
                "luxury_prestige": 98,
                "trust_authority": 90,
                "accessibility": 10,
                "digital_fluency": 30,
                "customer_intimacy": 85
            },
            "competency_matrix": {
                "branding_design": 95,
                "marketing_funnels": 40,
                "sales_closing": 90,
                "tech_infrastructure": 35,
                "client_success_signals": 85
            },
            "pricing_architecture_analysis": "They employ a strict 'Ascension' model. The entry tier is gated behind a high-friction application process to establish authority. The core tier is invisible to the public, and the high-ticket ascension is purely referral-based.",
            "content_and_seo_strategy": {
                "primary_channels": ["LinkedIn dark-posting", "Private Newsletters"],
                "tone_of_voice": "Assertive, refined, and aggressively exclusive",
                "key_themes": ["Digital Transformation", "Elite Networking", "Strategic Growth"],
                "estimated_traffic_trend": [12000, 11500, 11800, 11000, 10500, 10200]
            },
            "cta_tactics": ["Apply for Access", "Request Private Audit", "Join the Waitlist"],
            "products": [
                {
                    "name": "Elite Audit",
                    "price_estimate": 5000,
                    "trend": "up",
                    "unique_selling_point": "Bespoke 30-day deep dive by senior partners",
                    "perceived_value": "ultra-premium"
                },
                {
                    "name": "Mastermind Access",
                    "price_estimate": 100000,
                    "trend": "stable",
                    "unique_selling_point": "Global network restricted to 50 active CEOs",
                    "perceived_value": "ultra-premium"
                }
            ],
            "technological_sophistication": "They use a heavily customized but outdated monolithic architecture. Page loads are decent but lack the micro-interactions expected of modern luxury. High digital friction.",
            "blue_ocean_recommendations": [
                {"title": "The Silent Takeover", "strategy": "Bypass their gatekeeping entirely by offering their 'hidden' insights as a highly polished, mid-ticket entry product."},
                {"title": "Technological Domination", "strategy": "Outpace their clunky onboarding by building an ultra-sleek, iOS-app-like web experience that makes them look archaic by comparison."}
            ]
        }
