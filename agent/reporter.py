"""Premium HTML report generator with Vibrant Luxury Mesh Background."""
import os
import re
from datetime import datetime
from pathlib import Path
from string import Template
import json

CSS = """
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Montserrat:wght@300;400;500;600&display=swap');
  
  :root {
      --bg-panel: rgba(255, 255, 255, 0.85);
      --primary: #bda37a; 
      --secondary: #0f0d0c; 
      --accent: #a45a3a; 
      --accent-success: #5c6b54; 
      --text-main: #33302d; 
      --text-dim: #736b60;
      --border: rgba(189, 163, 122, 0.4);
      --page-break: always;
  }
  
  body { 
      font-family: 'Montserrat', sans-serif; 
      margin: 0; 
      padding: 0; 
      min-height: 100vh;
      line-height: 1.8;
      color: var(--text-main);
      
      background-color: #f7f5f2;
      background-image: 
          radial-gradient(at 0% 0%, rgba(255, 255, 255, 1) 0%, transparent 50%),
          radial-gradient(at 100% 100%, rgba(189, 163, 122, 0.08) 0%, transparent 60%);
      background-attachment: fixed;
  }

  .document { max-width: 1200px; margin: 40px auto; position: relative; z-index: 10; padding: 20px;}
  
  .page { 
      background: #fff;
      box-shadow: 0 40px 80px -20px rgba(0, 0, 0, 0.1);
      padding: 80px;
      margin-bottom: 60px;
      position: relative;
      border: 1px solid rgba(189, 163, 122, 0.2);
  }
  
  .page::after {
      content: '';
      position: absolute;
      bottom: 0; left: 0; width: 100%; height: 6px;
      background: linear-gradient(90deg, var(--secondary), var(--primary), var(--secondary));
  }
  
  .dashboard-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 2px solid var(--border);
      padding-bottom: 30px;
      margin-bottom: 50px;
  }
  
  h1, h2, h3, .metric-value {
      font-family: 'Playfair Display', serif;
      color: var(--secondary);
  }

  h1 { font-weight: 600; font-size: 3.5rem; margin: 0; line-height: 1.1; letter-spacing: -0.02em;}
  h2 { font-weight: 600; font-size: 2rem; margin-top: 0; margin-bottom: 30px; border-bottom: 1px solid var(--border); padding-bottom: 15px; letter-spacing: 0.02em;}
  h3 { font-size: 1.4rem; margin-bottom: 15px; }
  
  .meta { color: var(--text-dim); font-size: 0.85rem; font-weight: 600; margin-top: 15px; letter-spacing: 0.15em; text-transform: uppercase;}
  
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-bottom: 40px; }
  .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 40px; margin-bottom: 40px; }
  
  .metric-card { 
      padding: 30px; 
      background: rgba(247, 245, 242, 0.5); 
      border-left: 3px solid var(--primary);
  }
  
  .metric-value { font-size: 3.2rem; font-weight: 400; line-height: 1; margin-bottom: 12px; }
  .metric-label { font-size: 0.8rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.15em; font-weight: 700;}
  
  .tag { 
      display: inline-block; 
      padding: 4px 12px; 
      background: #f0ebe1; 
      border-radius: 20px;
      font-size: 0.7rem; 
      margin: 4px 8px 4px 0; 
      color: var(--secondary); 
      font-weight: 700; 
      text-transform: uppercase; 
      letter-spacing: 0.1em;
  }
  
  table { width: 100%; border-collapse: collapse; margin-top: 20px;}
  th { color: var(--secondary); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.15em; padding: 20px 15px; text-align: left; border-bottom: 2px solid var(--primary); font-weight: 700;}
  td { padding: 20px 15px; border-bottom: 1px solid rgba(189, 163, 122, 0.2); vertical-align: middle; font-size: 1rem; }
  tr:hover td { background: rgba(189, 163, 122, 0.05); }
  
  .price { font-family: 'Playfair Display', serif; font-weight: 600; font-size: 1.4rem;}
  .paragraph-text { font-size: 1.05rem; margin-bottom: 20px; text-align: justify; font-weight: 500; line-height: 2.0; color: #4a453f;}
  
  .btn-print {
      background: var(--secondary);
      color: #ffffff;
      border: none;
      padding: 16px 36px;
      border-radius: 2px;
      font-weight: 700;
      font-size: 0.9rem;
      letter-spacing: 0.1em;
      cursor: pointer;
      transition: all 0.4s ease;
      text-transform: uppercase;
  }
  .btn-print:hover { background: var(--primary); }

  .faille-box {
      background: rgba(189, 163, 122, 0.05);
      border: 1px solid rgba(189, 163, 122, 0.3);
      border-left: 5px solid var(--accent);
      color: var(--text-main);
      padding: 40px;
      position: relative;
      margin-top: 20px;
  }
  .faille-box h2 { color: var(--accent); border-bottom-color: rgba(189,163,122, 0.3); }
  .faille-box p { color: var(--text-main); font-weight: 500;}
  
  .action-plan-card {
      background: #fff;
      border: 1px solid rgba(189, 163, 122, 0.3);
      border-radius: 12px;
      padding: 35px 35px 30px 45px;
      margin-bottom: 35px;
      position: relative;
      box-shadow: 0 10px 30px -10px rgba(0,0,0,0.05);
      transition: all 0.3s ease;
  }
  .action-plan-card:hover {
      transform: translateY(-3px);
      box-shadow: 0 15px 40px -15px rgba(0,0,0,0.1);
      border-color: var(--primary);
  }
  .action-number {
      position: absolute;
      top: -15px;
      left: -15px;
      width: 45px;
      height: 45px;
      background: var(--secondary);
      color: #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Playfair Display', serif;
      font-size: 1.4rem;
      font-weight: 600;
      border: 4px solid #f7f5f2;
      box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  }
  .action-title {
      font-size: 1.5rem;
      color: var(--secondary);
      margin-bottom: 20px;
      font-weight: 700;
  }
  .action-content ul {
      list-style: none;
      padding-left: 0;
  }
  .action-content li {
      position: relative;
      padding-left: 30px;
      margin-bottom: 12px;
      line-height: 1.6;
  }
  .action-content li::before {
      content: '✓';
      position: absolute;
      left: 0;
      top: 0;
      color: var(--accent-success);
      font-weight: 900;
  }
  .action-badge {
      display: inline-flex;
      align-items: center;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 15px;
  }
  .badge-blue { background: rgba(59, 130, 246, 0.1); color: #2563eb; border: 1px solid rgba(59, 130, 246, 0.2); }
  .badge-purple { background: rgba(147, 51, 234, 0.1); color: #7e22ce; border: 1px solid rgba(147, 51, 234, 0.2); }
  .badge-amber { background: rgba(245, 158, 11, 0.1); color: #b45309; border: 1px solid rgba(245, 158, 11, 0.2); }
  .link-styled {
      color: #2563eb; 
      text-decoration: none; 
      font-weight: 600;
      border-bottom: 1px dashed #2563eb;
      transition: all 0.2s;
  }
  .link-styled:hover {
      color: var(--secondary);
      border-bottom-color: var(--secondary);
  }
  
  @media print {
      body { background: #fff !important; }
      .document { margin: 0; padding: 0; max-width: 100%; }
      .page { box-shadow: none; border: none; padding: 40px; margin-bottom: 0; break-after: always; height: auto; }
      .page::after { content: none; }
      .btn-print { display: none; }
  }
"""

TEMPLATE = Template("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${T_TITLE}</title>
<style>$css</style>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="document">
        $content
    </div>
    $scripts
</body>
</html>""")

T_MAP = {
    'en': {
        'title': 'Target Intelligence Dossier',
        'confid': 'Highly Confidential',
        'export': 'Export 5K Dossier (PDF)',
        'market_tier': 'Market Tier',
        'valuat': 'Estimated Valuation',
        'threat_aggr': 'Threat Aggressiveness (1-10)',
        'exec_sum': 'Executive Summary',
        'crit_expl': 'Critical Exploitation Point',
        'vuln_gap': 'The Vulnerability Gap',
        'fracture': 'The Fracture:',
        'attack_ag': 'The Attack Angle:',
        'roi': 'Estimated ROI Opportunity:',
        'target_psych': 'Target Psychology',
        'demographics': 'Demographics:',
        'obj_hand': 'Objection Handling:',
        'fears': 'Fears & Pain Points',
        'desires': 'Desires & Aspirations',
        'brand_arch': 'Brand Archetype Matrix',
        'comp_mat': 'Deep Competency Matrix',
        'tech_fric': 'Technological Friction & Stack',
        'pricing_asc': 'Pricing Architecture & Ascension',
        'prod_foc': 'Product / Focus',
        'est_pricing': 'Estimated Pricing',
        'trend': 'Market Trend',
        'perceiv': 'Perceived Value Class',
        'content_str': 'Content Strategy',
        'tone': 'Tone:',
        'themes': 'Core Themes:',
        'channels': 'Channels:',
        'traffic': 'Estimated Traffic Footprint',
        'swot': 'S.W.O.T. Reconnaissance',
        'str': 'Strengths',
        'weak': 'Weaknesses',
        'opp': 'Opportunities',
        'thr': 'Threats',
        'blue_ocean': 'Blue Ocean Strategic Recommendations',
        'radar_labels': "['Innovation', 'Prestige', 'Trust', 'Accessibility', 'Intimacy']",
        'bar_labels': "['Branding', 'Funnels', 'Sales', 'Tech Stack', 'Client Success']",
        'drop_t': '▼ Drop',
        'rise_t': '▲ Rise',
        'stable_t': '— Stable'
    },
    'fr': {
        'title': "Dossier d'Intelligence Cible",
        'confid': 'Hautement Confidentiel',
        'export': 'Exporter Dossier 5K (PDF)',
        'market_tier': 'Niveau du Marché',
        'valuat': 'Valorisation Estimée',
        'threat_aggr': 'Agressivité de la Menace (1-10)',
        'exec_sum': 'Résumé Stratégique',
        'crit_expl': "Point d'Exploitation Critique",
        'vuln_gap': 'La Faille Vulnérable',
        'fracture': 'La Fracture :',
        'attack_ag': "L'Angle d'Attaque :",
        'roi': 'Opportunité de ROI Estimée :',
        'target_psych': 'Psychologie de la Cible',
        'demographics': 'Démographie :',
        'obj_hand': 'Gestion des Objections :',
        'fears': 'Peurs & Points de Douleur',
        'desires': 'Désirs & Aspirations',
        'brand_arch': 'Matrice : Archétype de Marque',
        'comp_mat': 'Matrice : Compétences Profondes',
        'tech_fric': 'Friction & Stack Technologique',
        'pricing_asc': 'Architecture de Prix & Ascension',
        'prod_foc': 'Produit / Focus',
        'est_pricing': 'Prix Estimé',
        'trend': 'Tendance',
        'perceiv': 'Classe de Valeur Perçue',
        'content_str': 'Stratégie de Contenu',
        'tone': 'Ton :',
        'themes': 'Thèmes Clés :',
        'channels': 'Canaux :',
        'traffic': 'Empreinte de Trafic Estimée',
        'swot': 'Reconnaissance S.W.O.T.',
        'str': 'Forces',
        'weak': 'Faiblesses',
        'opp': 'Opportunités',
        'thr': 'Menaces',
        'blue_ocean': 'Recommandations Stratégiques (Océan Bleu)',
        'radar_labels': "['Innovation', 'Prestige', 'Confiance', 'Accessibilité', 'Intimité']",
        'bar_labels': "['Branding', 'Tunnels', 'Ventes', 'Stack Tech', 'Succès Client']",
        'drop_t': '▼ Baisse',
        'rise_t': '▲ Hausse',
        'stable_t': '— Stable'
    },
    'ru': {
        'title': 'Досье Целевой Разведки',
        'confid': 'Строго Конфиденциально',
        'export': 'Экспорт Досье 5K (PDF)',
        'market_tier': 'Уровень Рынка',
        'valuat': 'Оценочная Стоимость',
        'threat_aggr': 'Агрессивность Угрозы (1-10)',
        'exec_sum': 'Стратегическое Резюме',
        'crit_expl': 'Критическая Точка Эксплуатации',
        'vuln_gap': 'Уязвимая Брешь',
        'fracture': 'Разрыв:',
        'attack_ag': 'Угол Атаки:',
        'roi': 'Оценка ROI / Возможность:',
        'target_psych': 'Психология Целевой Аудитории',
        'demographics': 'Демография:',
        'obj_hand': 'Работа с возражениями:',
        'fears': 'Страхи и Боли',
        'desires': 'Желания и Стремления',
        'brand_arch': 'Матрица Архетипа Бренда',
        'comp_mat': 'Матрица Глубинных Компетенций',
        'tech_fric': 'Технологические Трения и Стек',
        'pricing_asc': 'Архитектура Цен и Развитие',
        'prod_foc': 'Продукт / Фокус',
        'est_pricing': 'Оценочная Стоимость',
        'trend': 'Тренд на Рынке',
        'perceiv': 'Класс Воспринимаемой Ценности',
        'content_str': 'Контент-Стратегия',
        'tone': 'Тон:',
        'themes': 'Ключевые Темы:',
        'channels': 'Каналы:',
        'traffic': 'Оценочный След Трафика',
        'swot': 'S.W.O.T. Разведка',
        'str': 'Сильные Стороны',
        'weak': 'Слабые Стороны',
        'opp': 'Возможности',
        'thr': 'Угрозы',
        'blue_ocean': 'Стратегия Голубого Океана',
        'radar_labels': "['Инновации', 'Престиж', 'Доверие', 'Доступность', 'Близость к Клиенту']",
        'bar_labels': "['Брендинг', 'Воронки', 'Продажи', 'Тех. Стек', 'Успех Клиентов']",
        'drop_t': '▼ Спад',
        'rise_t': '▲ Рост',
        'stable_t': '— Стабильно'
    }
}

def md_to_html(text: str) -> str:
    if not isinstance(text, str): return str(text)
    
    # Links
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank" class="link-styled">\1 ↗</a>', text)
    
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: var(--secondary);">\1</strong>', text)
    
    lines = text.split('\n')
    out = []
    in_list = False
    
    for line in lines:
        cleaned = line.strip()
        if cleaned.startswith('- ') or cleaned.startswith('* '):
            if not in_list:
                out.append('<ul style="margin-bottom: 15px; padding-left: 25px; line-height: 1.8;">')
                in_list = True
            out.append(f"<li style='margin-bottom: 8px;'>{cleaned[2:]}</li>")
        else:
            if in_list:
                out.append('</ul>')
                in_list = False
            if cleaned:
                out.append(f"<p style='margin-top: 0; margin-bottom: 15px;'>{cleaned}</p>")
    
    if in_list:
        out.append('</ul>')
        
    return ''.join(out)

def _build_content(results: dict) -> tuple[str, str, dict]:
    html = ""
    scripts = ""
    
    # Extract language from first dict if present, default 'en'
    main_lang = 'en'
    for url, data in results.items():
        if data.get('_lang') in T_MAP:
            main_lang = data.get('_lang')
            break
            
    T = T_MAP[main_lang]
    
    for idx, (url, data) in enumerate(results.items()):
        comp_name = data.get("competitor_name", "Unknown Entity")
        market_pos = data.get("market_positioning", {})
        tier = market_pos.get("tier", "N/A") if isinstance(market_pos, dict) else "N/A"
        valuation = market_pos.get("perceived_valuation", "N/A") if isinstance(market_pos, dict) else "N/A"

        threat = int(data.get("threat_level", 5))
        threat_color = "var(--accent)" if threat >= 7 else ("#bda37a" if threat >= 4 else "var(--primary)")
        
        scores = data.get("brand_archetype_scores", {})
        radar_data = f"[{scores.get('innovation', 50)}, {scores.get('luxury_prestige', 50)}, {scores.get('trust_authority', 50)}, {scores.get('accessibility', 50)}, {scores.get('customer_intimacy', 50)}]"
        
        comps = data.get("competency_matrix", {})
        comp_data = f"[{comps.get('branding_design', 50)}, {comps.get('marketing_funnels', 50)}, {comps.get('sales_closing', 50)}, {comps.get('tech_infrastructure', 50)}, {comps.get('client_success_signals', 50)}]"

        content_seo = data.get("content_and_seo_strategy", {})
        traffic_trend = content_seo.get("estimated_traffic_trend", [0,0,0,0,0,0])
        
        products = data.get("products", [])
        p_rows = ""
        for p in products:
            trend = p.get("trend", "stable")
            
            t_badge = f"<span class='tag'>{T['stable_t']}</span>"
            if trend == "down":
                t_badge = f"<span class='tag' style='color:var(--accent); background:rgba(164,90,58,0.1)'>{T['drop_t']}</span>"
            elif trend == "up":
                t_badge = f"<span class='tag' style='color:var(--accent-success); background:rgba(92,107,84,0.1)'>{T['rise_t']}</span>"

            pv = (p.get('perceived_value') or 'standard').title()
            price = p.get('price_estimate') or 'N/A'
            price_display = f"${price}" if isinstance(price, (int, float)) else price
            p_rows += f"<tr><td><strong>{p.get('name') or '—'}</strong><br><small style='color:var(--text-dim)'>{p.get('unique_selling_point') or ''}</small></td><td class='price'>{price_display}</td><td>{t_badge}</td><td><span class='tag'>{pv}</span></td></tr>"

        swot = data.get('swot_analysis', {})
        s_list = "".join([f"<li style='margin-bottom: 10px;'>{md_to_html(s).replace('<p','<span').replace('</p>','</span>')}</li>" for s in swot.get("strengths", [])])
        w_list = "".join([f"<li style='margin-bottom: 10px;'>{md_to_html(w).replace('<p','<span').replace('</p>','</span>')}</li>" for w in swot.get("weaknesses", [])])
        o_list = "".join([f"<li style='margin-bottom: 10px;'>{md_to_html(o).replace('<p','<span').replace('</p>','</span>')}</li>" for o in swot.get("opportunities", [])])
        t_list = "".join([f"<li style='margin-bottom: 10px;'>{md_to_html(t).replace('<p','<span').replace('</p>','</span>')}</li>" for t in swot.get("threats", [])])
        
        bo_html = []
        badges = ['badge-blue', 'badge-amber', 'badge-purple']
        for i, b in enumerate(data.get("blue_ocean_recommendations", [])):
            badge = badges[i % len(badges)]
            bo_html.append(f"""
            <div class='action-plan-card'>
                <div class='action-number'>{i+1}</div>
                <div class='action-badge {badge}'>{T.get('blue_ocean', 'Strategy').split(':')[0]}</div>
                <div class='action-title'>{b.get('title')}</div>
                <div class='action-content paragraph-text'>
                    {md_to_html(b.get('strategy'))}
                </div>
            </div>
            """)
        blue_ocean = "".join(bo_html)

        vulnerability = data.get("the_vulnerability_gap", {})

        html += f"""
        <!-- PAGE 1: TITLE & EXECUTIVE -->
        <div class="page">
            <div class="dashboard-header">
                <div>
                    <div style="font-family: 'Montserrat', sans-serif; font-size: 0.85rem; letter-spacing: 0.4em; text-transform: uppercase; color: var(--primary); margin-bottom: 15px;">{T['title']}</div>
                    <h1 style="font-size: 4rem;">{comp_name}</h1>
                    <div class="meta">URL: {url} &middot; {T['confid']}</div>
                </div>
                <button class="btn-print" onclick="window.print()">{T['export']}</button>
            </div>
            
            <div class="grid-3">
                <div class="metric-card">
                    <div class="metric-label">{T['market_tier']}</div>
                    <div class="metric-value" style="font-size: 2rem; margin-top: 10px;">{tier}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">{T['valuat']}</div>
                    <div class="metric-value" style="font-size: 2rem; margin-top: 10px;">{valuation}</div>
                </div>
                <div class="metric-card" style="border-left-color: {threat_color};">
                    <div class="metric-label">{T['threat_aggr']}</div>
                    <div class="metric-value" style="color: {threat_color}; margin-top: 10px;">{threat}</div>
                </div>
            </div>

            <h2>{T['exec_sum']}</h2>
            <div class="paragraph-text" style="column-count: 2; column-gap: 50px;">
                {md_to_html(data.get('executive_summary', ''))}
            </div>
        </div>

        <!-- PAGE 2: THE VULNERABILITY GAP & TARGET PSYCHOLOGY -->
        <div class="page">
            <div class="faille-box" style="margin-top: 0; margin-bottom: 50px;">
                <div style="font-family: 'Montserrat', sans-serif; font-size: 0.8rem; letter-spacing: 0.3em; text-transform: uppercase; color: var(--accent); margin-bottom: 10px;">{T['crit_expl']}</div>
                <h2 style="border-bottom: none; font-size: 2.8rem; margin-bottom: 10px;">{T['vuln_gap']}</h2>
                
                <h3 style="color: var(--secondary); margin-top: 30px;">{T['fracture']}</h3>
                <div class="paragraph-text">{md_to_html(vulnerability.get('description', ''))}</div>
                
                <h3 style="color: var(--secondary); margin-top: 30px;">{T['attack_ag']}</h3>
                <div class="paragraph-text" style="color: var(--primary); font-size: 1.15rem; font-weight: 600;">{md_to_html(vulnerability.get('attack_angle', ''))}</div>
                
                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid rgba(189,163,122,0.3);">
                    <span style="font-family: 'Montserrat'; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-dim);">{T['roi']}</span> 
                    <span style="color: var(--secondary); font-weight: 600; margin-left: 10px;">{vulnerability.get('estimated_roi_opportunity', '')}</span>
                </div>
            </div>

            <div class="grid-2">
                <div>
                    <h2>{T['target_psych']}</h2>
                    <div class="paragraph-text"><strong>{T['demographics']}</strong><br>{md_to_html(data.get('target_audience_psychology', {}).get('demographics', ''))}</div>
                    <div class="paragraph-text"><strong>{T['obj_hand']}</strong><br>{md_to_html(data.get('target_audience_psychology', {}).get('objection_handling_tactics', ''))}</div>
                </div>
                <div>
                    <h3>{T['fears']}</h3>
                    <ul style="color: var(--text-dim); line-height: 1.8; margin-bottom: 30px;">
                        {"".join([f"<li>{f}</li>" for f in data.get('target_audience_psychology', {}).get('fears_and_pain_points', [])])}
                    </ul>
                    <h3 style="margin-top: 20px;">{T['desires']}</h3>
                    <ul style="color: var(--primary); font-weight: 500; line-height: 1.8;">
                        {"".join([f"<li>{d}</li>" for d in data.get('target_audience_psychology', {}).get('desires_and_aspirations', [])])}
                    </ul>
                </div>
            </div>
        </div>

        <!-- PAGE 3: BRAND METRICS & COMPETENCY -->
        <div class="page">
            <div class="grid-2">
                <div>
                    <h2>{T['brand_arch']}</h2>
                    <div style="position: relative; height: 350px;">
                        <canvas id="radarChart_{idx}"></canvas>
                    </div>
                </div>
                <div>
                    <h2>{T['comp_mat']}</h2>
                    <div style="position: relative; height: 350px;">
                        <canvas id="barChart_{idx}"></canvas>
                    </div>
                </div>
            </div>
            
            <h2 style="margin-top: 50px;">{T['tech_fric']}</h2>
            <div class="paragraph-text">{md_to_html(data.get('technological_sophistication', ''))}</div>
        </div>

        <!-- PAGE 4: ARSENAL & SEO -->
        <div class="page">
            <h2>{T['pricing_asc']}</h2>
            <div class="paragraph-text">{md_to_html(data.get('pricing_architecture_analysis', ''))}</div>
            
            <table style="margin-top: 40px; margin-bottom: 50px;">
                <tr><th>{T['prod_foc']}</th><th>{T['est_pricing']}</th><th>{T['trend']}</th><th>{T['perceiv']}</th></tr>
                {p_rows}
            </table>
            
            <div class="grid-2">
                <div>
                    <h2>{T['content_str']}</h2>
                    <p class="paragraph-text"><strong>{T['tone']}</strong> {content_seo.get('tone_of_voice', '')}</p>
                    <p class="paragraph-text"><strong>{T['themes']}</strong> {md_to_html(', '.join(content_seo.get('key_themes', []))).replace('<p','<span').replace('</p>','</span>')}</p>
                    <p class="paragraph-text"><strong>{T['channels']}</strong> {md_to_html(', '.join(content_seo.get('primary_channels', []))).replace('<p','<span').replace('</p>','</span>')}</p>
                </div>
                <div>
                    <h2>{T['traffic']}</h2>
                    <div style="position: relative; height: 200px;">
                        <canvas id="lineChart_{idx}"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- PAGE 5: SWOT & BLUE OCEAN -->
        <div class="page">
            <h2 style="text-align: center; border:none;">{T['swot']}</h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 60px;">
                <div style="background: rgba(92, 107, 84, 0.05); padding: 30px; border-top: 4px solid var(--accent-success);">
                    <h3 style="color: var(--accent-success);">{T['str']}</h3>
                    <ul style="padding-left: 20px; font-size: 0.95rem; line-height: 1.6;">{s_list}</ul>
                </div>
                <div style="background: rgba(164, 90, 58, 0.05); padding: 30px; border-top: 4px solid var(--accent);">
                    <h3 style="color: var(--accent);">{T['weak']}</h3>
                    <ul style="padding-left: 20px; font-size: 0.95rem; line-height: 1.6;">{w_list}</ul>
                </div>
                <div style="background: rgba(189, 163, 122, 0.05); padding: 30px; border-top: 4px solid var(--primary);">
                    <h3 style="color: var(--primary);">{T['opp']}</h3>
                    <ul style="padding-left: 20px; font-size: 0.95rem; line-height: 1.6;">{o_list}</ul>
                </div>
                <div style="background: rgba(26, 24, 22, 0.05); padding: 30px; border-top: 4px solid var(--secondary);">
                    <h3 style="color: var(--secondary);">{T['thr']}</h3>
                    <ul style="padding-left: 20px; font-size: 0.95rem; line-height: 1.6;">{t_list}</ul>
                </div>
            </div>

            <h2 style="color: var(--primary);">{T['blue_ocean']}</h2>
            {blue_ocean}
        </div>
        """

        scripts += f"""
        <script>
        document.addEventListener("DOMContentLoaded", function() {{
            const radarCtx = document.getElementById('radarChart_{idx}');
            if(radarCtx) {{
                new Chart(radarCtx, {{
                    type: 'radar',
                    data: {{
                        labels: {T['radar_labels']},
                        datasets: [{{
                            label: 'Archetype Score',
                            data: {radar_data},
                            backgroundColor: 'rgba(189, 163, 122, 0.4)',
                            borderColor: '#bda37a',
                            borderWidth: 2,
                            pointBackgroundColor: '#0f0d0c'
                        }}]
                    }},
                    options: {{ scales: {{ r: {{ max: 100, min: 0, ticks: {{display:false}} }} }}, plugins: {{ legend: {{display:false}} }} }}
                }});
            }}

            const barCtx = document.getElementById('barChart_{idx}');
            if(barCtx) {{
                new Chart(barCtx, {{
                    type: 'bar',
                    data: {{
                        labels: {T['bar_labels']},
                        datasets: [{{
                            label: 'Competency %',
                            data: {comp_data},
                            backgroundColor: '#0f0d0c',
                        }}]
                    }},
                    options: {{ scales: {{ y: {{ max: 100, min: 0}} }}, plugins: {{ legend: {{display:false}} }} }}
                }});
            }}

            const lineCtx = document.getElementById('lineChart_{idx}');
            if(lineCtx) {{
                new Chart(lineCtx, {{
                    type: 'line',
                    data: {{
                        labels: ['M-6', 'M-5', 'M-4', 'M-3', 'M-2', 'Current'],
                        datasets: [{{
                            label: 'Traffic Propensity',
                            data: {traffic_trend},
                            borderColor: '#bda37a',
                            tension: 0.4,
                            fill: true,
                            backgroundColor: 'rgba(189, 163, 122, 0.1)'
                        }}]
                    }},
                    options: {{ plugins: {{ legend: {{display:false}} }} }}
                }});
            }}
        }});
        </script>
        """

    return html, scripts, T

def generate_report(results: dict, output_path: str) -> str:
    content, scripts, T = _build_content(results)
    
    html = TEMPLATE.substitute(
        css=CSS,
        content=content,
        scripts=scripts,
        T_TITLE=T['title']
    )
    Path(output_path).write_text(html, encoding="utf-8")
    return output_path
