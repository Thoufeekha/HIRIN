# backend.py
import fitz
import re
import json
import threading
import httpx
import time
import os
from pathlib import Path

# Fix: Find .env file in multiple locations
env_locations = [
    Path('.env'),
    Path('../.env'),
    Path('../../.env'),
    Path('../../../.env'),
    Path('../../Email/.env'),
    Path('../Email/.env'),
    Path('Email/.env'),
    Path(__file__).parent / '.env',
    Path(__file__).parent.parent / '.env',
    Path(__file__).parent.parent.parent / 'Email' / '.env',
]

# Try to load config
config = None
for env_path in env_locations:
    if env_path.exists():
        print(f"✅ Found .env at: {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('GROQ_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    # Create a simple config object
                    class SimpleConfig:
                        def __init__(self):
                            self.api_key = api_key
                            self.model = "llama-3.3-70b-versatile"
                            self.max_questions = 10
                            self.aptitude_questions = 35
                            self.aptitude_time = 35 * 60
                        @property
                        def is_available(self):
                            return bool(self.api_key) and len(self.api_key) > 10
                    config = SimpleConfig()
                    print("✅ API key loaded")
                    break
        if config:
            break

# If no config found, try environment variable
if not config:
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        class SimpleConfig:
            def __init__(self):
                self.api_key = api_key
                self.model = "llama-3.3-70b-versatile"
                self.max_questions = 10
                self.aptitude_questions = 35
                self.aptitude_time = 35 * 60
            @property
            def is_available(self):
                return bool(self.api_key) and len(self.api_key) > 10
        config = SimpleConfig()
        print("✅ API key from environment")

# If still no config, create empty config
if not config:
    class SimpleConfig:
        def __init__(self):
            self.api_key = ""
            self.model = "llama-3.3-70b-versatile"
            self.max_questions = 10
            self.aptitude_questions = 35
            self.aptitude_time = 35 * 60
        @property
        def is_available(self):
            return False
    config = SimpleConfig()
    print("⚠️ No API key found - Using fallback questions")

# Try importing voice libraries
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    sr = None
    pyttsx3 = None


class PDFProcessor:
    """Handle PDF extraction and text processing."""
    
    @staticmethod
    def extract_text(pdf_path):
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"
            doc.close()
            if not text.strip():
                raise Exception("No text extracted from PDF - might be scanned or image-based")
            return text
        except Exception as e:
            raise Exception(f"PDF Error: {str(e)}")
    
    @staticmethod
    def extract_company(text):
        patterns = [
            r"Company\s*:\s*(.*)",
            r"Company\s+Name\s*:\s*(.*)",
            r"Organization\s*:\s*(.*)",
            r"Employer\s*:\s*(.*)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group(1).strip()
        return ""
    
    @staticmethod
    def extract_role(text):
        patterns = [
            r"Job Title\s*:\s*(.*)",
            r"Role\s*:\s*(.*)",
            r"Position\s*:\s*(.*)",
            r"Designation\s*:\s*(.*)",
            r"Current\s+Role\s*:\s*(.*)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group(1).strip()
        return ""
    
    @staticmethod
    def extract_name(text):
        patterns = [
            r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
            r"Name:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
            r"([A-Z][a-z]+)\s+([A-Z][a-z]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group(0).strip()
        return "Candidate"
    
    @staticmethod
    def extract_email(text):
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(pattern, text)
        if match:
            return match.group(0)
        return "Not specified"
    
    @staticmethod
    def extract_phone(text):
        patterns = [
            r'\b\d{10}\b',
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\+?\d{1,3}[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return "Not specified"


class VoiceEngine:
    """Handle voice input and output."""
    
    def __init__(self):
        self.available = VOICE_AVAILABLE
        self.is_speaking = False
        self.tts = None
        self.recognizer = None
        self.mic = None
        
        if self.available:
            try:
                self.tts = pyttsx3.init()
                self.tts.setProperty('rate', 160)
                self.tts.setProperty('volume', 1.0)
                self.recognizer = sr.Recognizer()
                self.mic = sr.Microphone()
                with self.mic as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("✅ Voice engine initialized")
            except Exception as e:
                self.available = False
                print(f"⚠️ Voice features unavailable: {e}")
    
    def speak(self, text):
        if not self.available or self.tts is None:
            print(f"📝 {text[:100]}...")
            return
        
        timeout = 10
        start = time.time()
        while self.is_speaking and (time.time() - start) < timeout:
            time.sleep(0.1)
        
        self.is_speaking = True
        
        def thread():
            try:
                self.tts.say(text)
                self.tts.runAndWait()
            except Exception as e:
                print(f"⚠️ TTS Error: {e}")
            finally:
                self.is_speaking = False
        
        threading.Thread(target=thread, daemon=True).start()
        time.sleep(0.3)
    
    def listen(self, timeout=30):
        if not self.available:
            return None
        
        try:
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("🎤 Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=60)
                print("🔄 Processing...")
                text = self.recognizer.recognize_google(audio)
                return text
        except sr.WaitTimeoutError:
            print("⏰ Timeout - No speech detected")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


class QuestionGenerator:
    """Generate interview and aptitude questions using AI."""
    
    def __init__(self):
        self.api_key = config.api_key
        self.model = config.model
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.timeout = 120
    
    def _call_api(self, messages, temperature=0.7):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 4000
        }

        max_retries = 3
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(
                        self.api_url,
                        headers=headers,
                        json=data
                    )

                # Debug output
                print("=" * 60)
                print("STATUS:", response.status_code)
                print("BODY:")
                print(response.text)
                print("=" * 60)

                if response.status_code == 429:
                    wait_time = retry_delay * (attempt + 1)
                    print(f"⏳ Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException:
                if attempt < max_retries - 1:
                    print("⚠️ Timeout, retrying...")
                    time.sleep(retry_delay)
                    continue
                raise Exception("API timeout")

            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Error: {e}")
                    time.sleep(retry_delay)
                    continue

                raise Exception(f"API Error: {e}")

        raise Exception("Max retries exceeded")
    
    def _clean_json(self, content):
        if '```json' in content:
            content = content.split('```json')[1]
        if '```' in content:
            content = content.split('```')[0]
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end != -1:
            content = content[start:end]
        return content.strip()
    
    def _safe_json_loads(self, content):
        try:
            return json.loads(content)
        except:
            try:
                import re
                q_pattern = r'"question":\s*"([^"]+)"'
                questions = re.findall(q_pattern, content)
                if questions:
                    result = []
                    for i, q in enumerate(questions, 1):
                        result.append({
                            "id": i,
                            "question": q,
                            "difficulty": "medium",
                            "expected_points": ["Communication", "Relevant experience"],
                            "evaluation_criteria": "Look for clear communication"
                        })
                    return {"questions": result}
                return {"questions": []}
            except:
                return {"questions": []}
    
    def generate_interview_questions(self, resume, jd, company, role, mode="technical"):
        timestamp = int(time.time() * 1000) % 100000
        name = PDFProcessor.extract_name(resume)
        
        prompts = {
            "technical": "technical skills, problem-solving, domain expertise",
            "behavioral": "leadership, teamwork, conflict resolution",
            "hr": "career goals, strengths/weaknesses, company culture",
            "mixed": "all aspects: technical, behavioral, and HR"
        }
        
        prompt = f"""
        Generate 10 {mode} interview questions for a {role} at {company}.
        Use seed {timestamp} for variety.
        
        CANDIDATE: {name}
        
        === CANDIDATE RESUME ===
        {resume[:4000]}
        
        === JOB DESCRIPTION ===
        {jd[:2000]}
        
        INSTRUCTIONS:
        1. READ and UNDERSTAND the resume content thoroughly
        2. READ and UNDERSTAND the job description
        3. Generate questions based on the candidate's actual experience
        
        FOCUS: {prompts[mode]}
        
        Return ONLY valid JSON:
        {{
            "questions": [
                {{
                    "id": 1,
                    "question": "Question text",
                    "difficulty": "easy/medium/hard",
                    "category": "role_based/resume_based",
                    "expected_points": ["point1", "point2"],
                    "evaluation_criteria": "What to look for"
                }}
            ]
        }}
        """
        messages = [
            {"role": "system", "content": "Generate personalized interview questions. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ]
        try:
            response = self._call_api(messages, temperature=0.8)
            content = response['choices'][0]['message']['content']
            clean_json = self._clean_json(content)
            data = self._safe_json_loads(clean_json)
            return data.get('questions', [])
        except Exception as e:
            raise Exception(f"Failed to generate questions: {str(e)}")
    
    def generate_aptitude_questions(self, count=35):
        timestamp = int(time.time() * 1000) % 100000
        
        prompt = f"""
        Generate {count} professional aptitude questions with 4 options.
        Use seed {timestamp} for variety.
        
        CATEGORIES (Mix all):
        1. Quantitative Aptitude (20%) - Percentages, Profit/Loss, Time & Work, Speed & Distance, Averages, Ratios
        2. Logical Reasoning (20%) - Blood Relations, Directions, Coding-Decoding, Syllogisms, Puzzles
        3. Verbal Ability (15%) - Synonyms, Antonyms, Sentence Completion, Reading Comprehension
        4. Data Interpretation (15%) - Tables, Charts, Graphs, Data Analysis
        5. Analytical Reasoning (15%) - Seating Arrangements, Patterns, Sequences
        6. Technical Aptitude (15%) - Basic programming logic, Algorithm thinking
        
        DIFFICULTY DISTRIBUTION:
        - 40% EASY (Basic concepts, direct application)
        - 40% MEDIUM (Moderate complexity, multiple steps)
        - 20% HARD (Complex problems, advanced concepts)
        
        CRITICAL REQUIREMENTS:
        - Each question MUST have exactly 4 REAL options
        - DO NOT use "Option A", "Option B", "Option C", "Option D" as options
        - Options must be meaningful numbers, words, or phrases
        - The 'correct' field must be the index (0, 1, 2, or 3)
        
        EASY Examples (Simple, direct):
        1. "What is 15% of 200?" → options: ["20", "25", "30", "35"] → correct: 2
        2. "If A = 1, B = 2, what is C?" → options: ["2", "3", "4", "5"] → correct: 1
        3. "Which word is opposite of 'Generous'?" → options: ["Kind", "Greedy", "Helpful", "Caring"] → correct: 1
        
        MEDIUM Examples (Multi-step):
        1. "A car travels 240 km in 4 hours. What is its speed in m/s?" → options: ["15", "16.67", "20", "25"] → correct: 1
        2. "If 'ROSE' is coded as 'UVWH', how is 'LILY' coded?" → options: ["OLOB", "OLOC", "OLOD", "OLOE"] → correct: 1
        3. "A shopkeeper sells an item for Rs. 990 at 10% profit. What was the cost price?" → options: ["880", "890", "900", "950"] → correct: 2
        
        HARD Examples (Complex, analytical):
        1. "In a certain code, 'COMPUTER' is written as 'PMOCUTRE'. How is 'KEYBOARD' written?" → options: ["YKEBROAD", "YKEBORAD", "YKEBOARD", "YKEBORDA"] → correct: 0
        2. "If 5 machines can produce 500 units in 8 hours, how many hours will 8 machines take for 800 units?" → options: ["6", "8", "10", "12"] → correct: 1
        3. "Among P, Q, R, S, T, each has different heights. Q is taller than R but shorter than P. S is taller than T but shorter than R. Who is the shortest?" → options: ["P", "Q", "R", "T"] → correct: 3
        
        EXAMPLE FULL FORMAT:
        {{
            "questions": [
                {{
                    "id": 1,
                    "category": "Quantitative Aptitude",
                    "question": "A shopkeeper buys an item for Rs. 800 and sells it for Rs. 920. What is the profit percentage?",
                    "options": ["12%", "15%", "18%", "20%"],
                    "correct": 1,
                    "difficulty": "easy",
                    "explanation": "Profit = 920 - 800 = 120; Profit% = (120/800) × 100 = 15%"
                }},
                {{
                    "id": 2,
                    "category": "Logical Reasoning",
                    "question": "If 'MOBILE' is coded as 'NQCLKG', how is 'LAPTOP' coded?",
                    "options": ["NCRVQR", "NCRVQP", "NCRVRO", "NCRVRP"],
                    "correct": 0,
                    "difficulty": "medium",
                    "explanation": "Each letter moves +1, +2, +1, +2 pattern"
                }}
            ]
        }}
        
        Return ONLY valid JSON. No additional text.
        """
        messages = [
            {"role": "system", "content": "You are a professional aptitude test generator. Generate questions with difficulty: 40% easy, 40% medium, 20% hard. Include topics like: Quantitative, Logical Reasoning, Verbal Ability, Data Interpretation, Analytical Reasoning. Never use 'Option A', 'Option B' as options. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ]
        try:
            response = self._call_api(messages, temperature=0.95)
            content = response['choices'][0]['message']['content']
            clean_json = self._clean_json(content)
            data = self._safe_json_loads(clean_json)
            questions = data.get('questions', [])
            
            validated_questions = []
            for i, q in enumerate(questions):
                if 'options' not in q or not q['options'] or len(q['options']) != 4:
                    q['options'] = [f"Option {chr(65+j)}" for j in range(4)]
                    q['correct'] = 0
                elif len(q['options']) == 4:
                    generic_options = all(str(opt).startswith('Option ') for opt in q['options'])
                    if generic_options:
                        q['options'] = ["1", "2", "3", "4"]
                        q['correct'] = 0
                
                if q.get('correct', 0) >= len(q['options']):
                    q['correct'] = 0
                if 'category' not in q:
                    q['category'] = 'Aptitude'
                if 'difficulty' not in q:
                    q['difficulty'] = 'medium'
                if 'explanation' not in q:
                    q['explanation'] = 'Analyze the problem carefully to find the correct answer'
                validated_questions.append(q)
            
            return validated_questions
        except Exception as e:
            raise Exception(f"Failed to generate aptitude: {str(e)}")
    
    def generate_hr_tips(self, role, company):
        prompt = f"""
        Generate 10 HR questions for {role} at {company}.
        
        Return ONLY valid JSON:
        {{
            "hr_questions": [
                {{
                    "question": "Question text",
                    "best_practice": "How to answer",
                    "sample_answer": "Example answer"
                }}
            ]
        }}
        """
        messages = [
            {"role": "system", "content": "Generate HR tips. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ]
        try:
            response = self._call_api(messages, temperature=0.5)
            content = response['choices'][0]['message']['content']
            clean_json = self._clean_json(content)
            data = self._safe_json_loads(clean_json)
            return data.get('hr_questions', [])
        except Exception as e:
            raise Exception(f"Failed to generate HR tips: {str(e)}")
    
    def evaluate_answer(self, question, answer):
        prompt = f"""
        Evaluate: Q: {question.get('question', '')} A: {answer}
        
        Return ONLY valid JSON:
        {{
            "score": 7,
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1", "weakness2"],
            "suggestions": ["suggestion1", "suggestion2"],
            "sample_answer": "A better answer"
        }}
        """
        messages = [
            {"role": "system", "content": "Evaluate answer. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ]
        try:
            response = self._call_api(messages, temperature=0.3)
            content = response['choices'][0]['message']['content']
            clean_json = self._clean_json(content)
            data = self._safe_json_loads(clean_json)
            return data
        except:
            return {
                "score": 5,
                "strengths": ["Attempted to answer"],
                "weaknesses": ["Could be more detailed"],
                "suggestions": ["Provide specific examples"],
                "sample_answer": "Use the STAR method"
            }
    
    def generate_aptitude_suggestions(self, results):
        prompt = f"""
        Based on these results, provide suggestions:
        {results}
        
        Return ONLY valid JSON:
        {{
            "summary": "Overall assessment",
            "strengths": ["strength1", "strength2"],
            "weak_areas": ["area1", "area2"],
            "improvement_plan": ["step1", "step2", "step3"]
        }}
        """
        messages = [
            {"role": "system", "content": "Provide suggestions. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ]
        try:
            response = self._call_api(messages, temperature=0.5)
            content = response['choices'][0]['message']['content']
            clean_json = self._clean_json(content)
            data = self._safe_json_loads(clean_json)
            return data
        except:
            return None
    
    def generate_interview_suggestions(self, history):
        prompt = f"""
        Based on these results, provide suggestions:
        {history}
        
        Return ONLY valid JSON:
        {{
            "summary": "Overall assessment",
            "strengths": ["strength1", "strength2"],
            "weak_areas": ["area1", "area2"],
            "improvement_plan": ["step1", "step2", "step3"]
        }}
        """
        messages = [
            {"role": "system", "content": "Provide suggestions. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ]
        try:
            response = self._call_api(messages, temperature=0.5)
            content = response['choices'][0]['message']['content']
            clean_json = self._clean_json(content)
            data = self._safe_json_loads(clean_json)
            return data
        except:
            return None


class InterviewAssistant:
    """Main assistant class coordinating all features."""
    
    def __init__(self):
        self.pdf = PDFProcessor()
        self.voice = VoiceEngine()
        self.qgen = QuestionGenerator()
        self.resume = ""
        self.jd = ""
        self.company = ""
        self.role = ""
        self.name = ""
        self.email = ""
        self.phone = ""
        self.questions = []
        self.aptitude_qs = []
        self.hr_tips = []
        self.history = []
        self.aptitude_history = {}
        self.aptitude_suggestions = None
        self.interview_suggestions = None
        self.q_index = 0
        self.api_available = config.is_available
    
    def load_resume(self, path):
        try:
            self.resume = self.pdf.extract_text(path)
            self.name = self.pdf.extract_name(self.resume)
            self.email = self.pdf.extract_email(self.resume)
            self.phone = self.pdf.extract_phone(self.resume)
            return True
        except Exception as e:
            raise Exception(f"Failed to load resume: {str(e)}")
    
    def load_job_description(self, text):
        self.jd = text
        self.company = self.pdf.extract_company(text)
        self.role = self.pdf.extract_role(text)
        return True
    
    def generate_questions(self, mode="technical"):
        self.questions = self.qgen.generate_interview_questions(
            self.resume, self.jd, self.company, self.role, mode
        )
        self.q_index = 0
        self.history = []
        self.interview_suggestions = None
        return self.questions
    
    def generate_aptitude(self):
        self.aptitude_qs = self.qgen.generate_aptitude_questions(35)
        self.aptitude_history = {}
        self.aptitude_suggestions = None
        return self.aptitude_qs
    
    def generate_hr_tips(self, concern=""):
        role = concern if concern else "general"
        self.hr_tips = self.qgen.generate_hr_tips(role, "")
        return self.hr_tips
    
    def evaluate_answer(self, question, answer):
        result = self.qgen.evaluate_answer(question, answer)
        self.history.append({
            "question": question,
            "answer": answer,
            "evaluation": result
        })
        return result
    
    def save_aptitude_results(self, answers, questions):
        correct = 0
        category_analysis = {}
        for i, q in enumerate(questions):
            ans = answers[i] if i < len(answers) else None
            category = q.get('category', 'General')
            if category not in category_analysis:
                category_analysis[category] = {'correct': 0, 'total': 0}
            category_analysis[category]['total'] += 1
            if ans is not None and ans == q.get('correct', 0):
                correct += 1
                category_analysis[category]['correct'] += 1
        
        self.aptitude_history = {
            "correct": correct,
            "total": len(questions),
            "category_analysis": category_analysis
        }
        category_results = {cat: f"{data['correct']}/{data['total']}" for cat, data in category_analysis.items()}
        self.aptitude_suggestions = self.qgen.generate_aptitude_suggestions(category_results)
        return self.aptitude_history
    
    def get_interview_suggestions(self):
        if not self.history:
            return None
        if self.interview_suggestions is None:
            history_summary = []
            for h in self.history:
                history_summary.append({
                    "question": h["question"]["question"][:100],
                    "score": h["evaluation"].get("score", 0)
                })
            self.interview_suggestions = self.qgen.generate_interview_suggestions(history_summary)
        return self.interview_suggestions
    
    def get_aptitude_suggestions(self):
        return self.aptitude_suggestions
    
    def speak(self, text):
        self.voice.speak(text)
    
    def listen(self):
        return self.voice.listen()
    
    def get_statistics(self):
        interview_stats = {"total": len(self.history), "avg_score": 0}
        if self.history:
            scores = [h["evaluation"].get("score", 0) for h in self.history]
            interview_stats["avg_score"] = sum(scores) / len(scores)
        
        aptitude_stats = {"total": 0, "correct": 0, "percentage": 0}
        if self.aptitude_history:
            aptitude_stats["total"] = self.aptitude_history["total"]
            aptitude_stats["correct"] = self.aptitude_history["correct"]
            if aptitude_stats["total"] > 0:
                aptitude_stats["percentage"] = (aptitude_stats["correct"] / aptitude_stats["total"]) * 100
        
        return {
            "interview": interview_stats,
            "aptitude": aptitude_stats,
            "role": self.role,
            "company": self.company,
            "name": self.name,
            "email": self.email,
            "phone": self.phone
        }
    
    def get_hr_advice(self, concern):
        if not concern:
            return None
        prompt = f"""
        Based on this concern: '{concern}'
        Provide personalized HR interview advice.
        
        Return ONLY valid JSON:
        {{
            "summary": "Brief summary of the advice",
            "advice": ["advice1", "advice2", "advice3"],
            "practice_tips": ["tip1", "tip2", "tip3"],
            "confidence_boost": "Encouraging message"
        }}
        """
        messages = [
            {"role": "system", "content": "Provide HR advice. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ]
        try:
            response = self.qgen._call_api(messages, temperature=0.5)
            content = response['choices'][0]['message']['content']
            clean_json = self.qgen._clean_json(content)
            data = self.qgen._safe_json_loads(clean_json)
            return data
        except:
            return None
    
    def reset_interview(self):
        self.questions = []
        self.history = []
        self.q_index = 0
        self.interview_suggestions = None
    
    def reset_aptitude(self):
        self.aptitude_qs = []
        self.aptitude_history = {}
        self.aptitude_suggestions = None