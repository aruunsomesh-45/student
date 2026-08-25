"""
AI Pedagogical Co-Pilot Engine for Teachers
Integrates with LLMs (Google Gemini API / OpenAI / Groq / custom key)
or provides resilient pedagogic rule-based synthesis for offline/local environments.
"""

import json
import urllib.request
import urllib.error
from django.conf import settings

def call_gemini_or_llm(api_key=None, prompt="", system_instruction="You are an expert pedagogical psychologist and master educator."):
    """
    Calls Google Gemini API or returns a structured response.
    """
    if not api_key:
        api_key = getattr(settings, 'DEFAULT_AI_API_KEY', None)

    if not api_key:
        return None

    # Clean API key
    api_key = str(api_key).strip()
    
    # Try calling Google Gemini REST API across active models
    models_to_try = [
        "gemini-1.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-pro"
    ]
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_instruction}\n\nTask:\n{prompt}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 1400
        }
    }

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                result = json.loads(response.read().decode('utf-8'))
                candidates = result.get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    if parts:
                        return parts[0].get('text', '')
        except Exception:
            continue
    
    return None


def generate_cohort_ai_strategy(cohort_data, api_key=None):
    """
    Synthesizes overall classroom psychometric distribution and generates
    an actionable weekly lecture and assignment adaptation plan.
    """
    total = cohort_data.get('total_students', 0)
    visual_pct = cohort_data.get('visual_pct', 0)
    auditory_pct = cohort_data.get('auditory_pct', 0)
    kinesthetic_pct = cohort_data.get('kinesthetic_pct', 0)
    avg_growth = cohort_data.get('avg_growth', 0)
    stress_count = cohort_data.get('stress_count', 0)
    stress_pct = round((stress_count / total * 100)) if total > 0 else 0

    dominant_modality = 'Visual'
    if kinesthetic_pct >= visual_pct and kinesthetic_pct >= auditory_pct:
        dominant_modality = 'Kinesthetic'
    elif auditory_pct >= visual_pct and auditory_pct >= kinesthetic_pct:
        dominant_modality = 'Auditory'

    prompt = f"""
Analyze this classroom cohort psychometric profile:
- Total Students Tested: {total}
- Learning Modality Breakdown: Visual ({visual_pct}%), Kinesthetic ({kinesthetic_pct}%), Auditory ({auditory_pct}%)
- Dominant Class Learning Style: {dominant_modality}
- Class Average Growth Mindset: {avg_growth}%
- High Stress Watchlist Count: {stress_count} students ({stress_pct}% of class)

Provide a 4-part educator strategy:
1. Lecture & Instruction Adaptation (How to structure daily lessons)
2. Assignment & Project Formatting (How to assign tasks)
3. Stress Reduction & Exam Prep Protocol (How to de-escalate anxiety)
4. Key Warning Sign to Watch For in Class
"""

    llm_response = call_gemini_or_llm(api_key, prompt)
    if llm_response:
        return {
            'is_live_ai': True,
            'content': llm_response,
            'source': 'Google Gemini AI',
        }

    # Resilient high-level pedagogical synthesis if no API key or network offline
    fallback_content = f"""### 🎯 Classroom Lecture & Delivery Adaptation ({dominant_modality}-Oriented)
- **Primary Scaffolding:** With **{dominant_modality} ({max(visual_pct, auditory_pct, kinesthetic_pct)}%)** as your dominant classroom modality, anchor lectures with {"color-coded whiteboard schemas, structural slide outlines, and visual handouts" if dominant_modality == 'Visual' else ("interactive live demonstrations, sandbox code/problem stations, and experiential simulations" if dominant_modality == 'Kinesthetic' else "structured Socratic questioning, verbal analogies, and short peer debate pauses")}.
- **Pacing Control:** Insert a 2-minute synthesis pause every 15 minutes allowing students to self-summarize key concepts.

### 📝 Assignment & Project Structuring
- **Multi-Modal Options:** Allow students to submit project deliverables in varied formats (e.g. annotated architecture diagram vs recorded presentation vs sandbox demo).
- **Milestone Checkpoints:** Break major multi-week projects into 3 low-stakes weekly deliverables to prevent last-minute crunch panic.

### ⚡ Stress Mitigation & Exam Protocol ({stress_count} Students Flagged on Watchlist)
- **Advance Notice & Rubrics:** {f"⚠️ Attention: {stress_count} students ({stress_pct}% of your class) exhibit high vulnerability to sudden evaluations." if stress_count > 0 else "Overall stress levels are stable across the cohort."}
- Provide transparent, point-by-point grading rubrics at least 5 days before exams to remove ambiguity.

### 🔍 Key Classroom Signal to Monitor
- Watch for students who disengage during static lecture transitions or hesitate to ask questions in large group settings. Implement anonymous digital question drop-boxes."""

    return {
        'is_live_ai': False,
        'content': fallback_content,
        'source': 'Pedagogical Expert Engine (Offline Mode)',
    }


def generate_student_ai_playbook(student_data, api_key=None):
    """
    Generates a tailored 1-on-1 pedagogical lesson and conversation plan
    for an individual student based on their psychometric vectors and message.
    """
    name = student_data.get('name', 'The Student')
    tier = student_data.get('tier', 'General')
    persona = student_data.get('persona_title', 'Evolving Learner')
    v = student_data.get('visual_score', 50)
    k = student_data.get('kinesthetic_score', 50)
    a = student_data.get('auditory_score', 50)
    g = student_data.get('growth_score', 50)
    s = student_data.get('stress_score', 50)
    personality = student_data.get('personality_tag', 'Achiever')
    interests = student_data.get('interests_tag', 'STEM/Analytical')
    wellbeing = student_data.get('wellbeing_flag', 'Green')
    soft_skills = student_data.get('soft_skills', 'Collaborative')
    teacher_msg = student_data.get('open_message', '').strip()

    prompt = f"""
Student Name: {name}
Academic Level: {tier}
Dominant Archetype: {persona}
Personality Tag: {personality} | Interests: {interests} | Wellbeing Status: {wellbeing}
Psychometric Scores: Visual: {v}%, Kinesthetic: {k}%, Auditory: {a}%, Growth Mindset: {g}%, Stress Vulnerability: {s}%
Soft Skills: {soft_skills}
Student's Note to Teacher: "{teacher_msg or 'No custom message provided.'}"

Generate an individualized 4-pillar 1-on-1 teaching plan:
1. Customized Instruction & Scaffolding (Tailored to their {persona} style)
2. Assignment & Exam Customization (How to structure tasks and evaluate them)
3. Stress De-escalation Protocol (Specific steps for exam periods or crunch weeks)
4. 1-on-1 Conversation Script (Exact phrases/questions for the teacher to use in check-ins)
"""

    llm_response = call_gemini_or_llm(api_key, prompt)
    if llm_response:
        return {
            'is_live_ai': True,
            'content': llm_response,
            'source': 'Google Gemini AI',
        }

    # Resilient fallback synthesis
    dom_mod = 'Visual' if v >= max(k, a) else ('Kinesthetic' if k >= a else 'Auditory')
    fallback_content = f"""### 🎯 1. Individualized Instruction & Scaffolding ({persona})
- **Cognitive Channel:** Anchor core concepts using **{dom_mod}** delivery. {"Utilize structured visual charts, mind-maps, and color-coded hierarchy diagrams." if dom_mod == 'Visual' else ("Provide interactive code sandboxes, lab problem kits, or live physical case models." if dom_mod == 'Kinesthetic' else "Incorporate Socratic discussion pauses and verbal concept walkthroughs.")}
- **Personality Alignment ({personality}):** {"Align assignments with clear, measurable milestone targets and progress checklists." if personality == 'Achiever' else ("Encourage lateral problem exploration and novel research directions." if personality == 'Explorer' else ("Pair in collaborative study pods where team synergy fuels motivation." if personality == 'Collaborator' else "Provide deep first-principles datasets and root-cause logic challenges."))}

### 📝 2. Assignment & Assessment Customization
- **Deliverable Format:** Offer assignment options that leverage **{interests}** themes to maximize intrinsic engagement.
- **Scaffolding:** Break multi-phase deliverables into low-stakes formative checkpoints with actionable written or verbal feedback.

### ⚡ 3. Stress & Exam Protocol ({'⚠️ High Anxiety Risk' if s >= 65 or wellbeing == 'Red' else 'Stable Emotional Resilience'})
- **Preparation Buffer:** {f"⚠️ {name} has a stress vulnerability index of {s}% ({wellbeing} wellbeing flag). Ensure exam outlines and grading rubrics are shared at least 5 days in advance. Avoid sudden unannounced tests." if s >= 65 or wellbeing == 'Red' else "Student handles evaluation pressure steadily. Can be challenged with timed stretch problems."}

### 💬 4. 1-on-1 Teacher Conversation Script
- *Teacher Check-In Opener:* "Hey {name}, I noticed your strengths in {interests} and your {dom_mod.lower()} approach. How are you feeling about our recent assignments?"
- *Stress Triage Question:* "When deadlines pile up, what is one thing I can do to make the material clearer or more manageable for you?"
- *Actionable Wrap-Up:* "Let's set a concrete milestone for next Tuesday so you can test your approach early without any pressure." """

    return {
        'is_live_ai': False,
        'content': fallback_content,
        'source': 'Pedagogical Expert Engine (Offline Mode)',
    }
