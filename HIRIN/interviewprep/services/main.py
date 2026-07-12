# main.py
import os
import time
from .backend import InterviewAssistant


class ConsoleApp:
    def __init__(self):
        self.ai = InterviewAssistant()
        self.running = True
        self.aptitude_answers = []
        self.test_exited_early = False
        self.interview_answers = []
        self.resume_loaded = False
        self.jd_loaded = False
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, text):
        print("="*60)
        print(f"  {text}")
        print("="*60)
    
    def exit_to_menu(self):
        self.clear_screen()
        print("\n" + "="*60)
        print("  🚪 EXITING TO MAIN MENU")
        print("="*60)
        print("\n✅ Returning to main menu...")
        time.sleep(1.5)
    
    def print_menu(self):
        self.clear_screen()
        self.print_header("🤖 AI INTERVIEW PREPARATION ASSISTANT")
        print("\n" + "="*60)
        print("  1. 📝 Take Aptitude Test")
        print("  2. 🎤 Interview Practice")
        print("  3. 💼 HR Interview Tips (No Resume/JD Needed)")
        print("  4. 📊 View Performance Analytics")
        print("  5. 🚪 Exit")
        print("="*60)
        print("\n💡 Type 'exit' anytime to return to menu")
    
    def validate_aptitude_choice(self, choice):
        choice = choice.strip().upper()
        if choice == "EXIT":
            return (True, True, None)
        letter_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
        if choice in letter_map:
            return (True, False, letter_map[choice])
        if choice in ['1', '2', '3', '4']:
            return (True, False, int(choice) - 1)
        return (False, False, None)
    
    def take_aptitude(self):
        self.clear_screen()
        self.print_header("📝 APTITUDE TEST")
        
        print("\n🔄 Generating 35 aptitude questions...\n")
        print("💡 Each test generates DIFFERENT questions!\n")
        
        try:
            questions = self.ai.generate_aptitude()
            self.aptitude_answers = [None] * len(questions)
            self.test_exited_early = False
            
            print(f"✅ Test ready! You have 35 minutes.")
            print("💡 Type 'exit' to quit the test anytime.")
            print("💡 Enter A/B/C/D or 1/2/3/4 to answer.\n")
            
            start_time = time.time()
            time_limit = 35 * 60
            
            for i, q in enumerate(questions):
                elapsed = time.time() - start_time
                remaining = time_limit - elapsed
                if remaining <= 0:
                    print("\n⏰ Time is up!")
                    break
                
                mins = int(remaining // 60)
                secs = int(remaining % 60)
                
                print(f"\n{'='*60}")
                print(f"Q{i+1}/{len(questions)}  ⏱️ {mins}:{secs:02d}")
                print(f"Category: {q.get('category', 'General')}")
                print(f"Difficulty: {q.get('difficulty', 'Medium')}")
                print(f"{'='*60}")
                print(f"\n{q['question']}\n")
                
                options = q.get('options', [])
                if options and len(options) == 4:
                    for j, opt in enumerate(options):
                        print(f"  {chr(65+j)}. {opt}")
                
                print("\nEnter answer (A/B/C/D or 1/2/3/4) or type 'exit' to quit: ")
                choice = input("> ").strip()
                
                is_valid, is_exit, answer_index = self.validate_aptitude_choice(choice)
                
                if is_exit:
                    self.test_exited_early = True
                    self.exit_to_menu()
                    if any(a is not None for a in self.aptitude_answers[:i]):
                        print("\n📊 Showing partial results...")
                        self.show_aptitude_results()
                    else:
                        print("\n❌ No answers to show.")
                    return
                
                if is_valid and answer_index is not None:
                    self.aptitude_answers[i] = answer_index
                    print(f"✅ Answer recorded: {choice.upper()}")
                else:
                    print("❌ Invalid choice! Please enter A/B/C/D or 1/2/3/4")
                    print("⚠️ Skipping this question...")
                    self.aptitude_answers[i] = None
            
            self.show_aptitude_results()
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def show_aptitude_results(self):
        self.clear_screen()
        self.print_header("📊 APTITUDE EVALUATION & SUGGESTIONS")
        
        if not self.ai.aptitude_qs:
            return
        
        history = self.ai.save_aptitude_results(self.aptitude_answers, self.ai.aptitude_qs)
        suggestions = self.ai.get_aptitude_suggestions()
        
        correct = history["correct"]
        total = history["total"]
        percentage = (correct / total) * 100
        
        print(f"\n{'='*60}")
        print(f"📊 SCORE: {correct}/{total} ({percentage:.1f}%)")
        print(f"{'='*60}")
        
        print("\n📈 CATEGORY ANALYSIS:")
        for category, data in history["category_analysis"].items():
            cat_percent = (data['correct'] / data['total']) * 100 if data['total'] > 0 else 0
            bar = "█" * int(cat_percent / 10) if cat_percent > 0 else "░"
            print(f"   {category}: {data['correct']}/{data['total']} ({cat_percent:.0f}%) {bar}")
        
        print("\n" + "="*60)
        print("💡 AI-GENERATED SUGGESTIONS")
        print("="*60)
        
        if suggestions:
            print(f"\n📌 Summary: {suggestions.get('summary', '')}")
            print(f"\n✅ Strengths: {', '.join(suggestions.get('strengths', ['None']))}")
            print(f"\n🎯 Weak Areas: {', '.join(suggestions.get('weak_areas', ['None']))}")
            print(f"\n📝 Improvement Plan:")
            for step in suggestions.get('improvement_plan', ['Practice daily']):
                print(f"   • {step}")
        else:
            if percentage >= 80:
                print("   ⭐ Excellent! Focus on speed.")
            elif percentage >= 60:
                print("   👍 Good! Identify weak categories and practice more.")
            else:
                print("   📖 Review fundamentals. Take daily practice tests.")
        
        input("\nPress Enter to continue...")
    
    def interview_practice(self):
        self.clear_screen()
        self.print_header("🎤 INTERVIEW PRACTICE")
        
        if not self.resume_loaded:
            print("\n📄 Enter Resume PDF path: ")
            path = input("> ").strip()
            
            if path.lower() == "exit":
                self.exit_to_menu()
                return
            
            try:
                self.ai.load_resume(path)
                self.resume_loaded = True
                print(f"\n✅ Resume loaded for: {self.ai.name}")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("\nPress Enter to continue...")
                return
        
        if not self.jd_loaded:
            print("\n📝 Paste Job Description (type 'DONE' when finished):")
            print("   Type 'exit' to return to menu\n")
            lines = []
            while True:
                line = input()
                if line.strip().lower() == "exit":
                    self.exit_to_menu()
                    return
                if line.strip().upper() == "DONE":
                    break
                lines.append(line)
            
            jd = "\n".join(lines)
            if not jd.strip():
                print("❌ No description provided")
                input("\nPress Enter to continue...")
                return
            
            try:
                self.ai.load_job_description(jd)
                self.jd_loaded = True
                print(f"\n✅ JD loaded! Company: {self.ai.company}, Role: {self.ai.role}")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("\nPress Enter to continue...")
                return
        
        print("\nSelect Interview Type:")
        print("  1. Technical")
        print("  2. HR")
        print("  3. Mixed")
        print("  Type 'exit' to return to menu")
        
        choice = input("\nEnter choice (1-3): ").strip().lower()
        
        if choice == "exit":
            self.exit_to_menu()
            return
        
        modes = {"1": "technical", "2": "hr", "3": "mixed"}
        mode = modes.get(choice, "technical")
        
        print(f"\n🔄 Generating {mode} questions based on your resume and job role...")
        print("💡 Each interview generates DIFFERENT questions!\n")
        
        try:
            questions = self.ai.generate_questions(mode)
            if not questions:
                print("\n⚠️ No questions generated. Please check your resume and JD.")
                input("\nPress Enter to continue...")
                return
            
            print(f"✅ {len(questions)} questions generated!\n")
            
            self.ai.q_index = 0
            self.interview_answers = []
            total = len(questions)
            
            print("💡 Type 'exit' anytime to quit the interview and return to menu.\n")
            input("Press Enter to start the interview...")
            
            while self.ai.q_index < total:
                self.clear_screen()
                q = self.ai.questions[self.ai.q_index]
                
                print(f"\n{'='*60}")
                print(f"QUESTION {self.ai.q_index+1}/{total}")
                print(f"Difficulty: {q.get('difficulty', 'medium')}")
                print(f"{'='*60}\n")
                print(f"{q['question']}\n")
                print("-"*60)
                
                print("🔊 Speaking question...")
                self.ai.speak(f"Question {self.ai.q_index+1}. {q['question']}")
                
                print("\n🎤 Speak your answer now.")
                print("   Type 'skip' to skip this question")
                print("   Type 'exit' to quit the interview\n")
                
                user_input = input("👉 Press Enter after speaking (or type skip/exit): ").strip().lower()
                
                if user_input == "exit":
                    self.exit_to_menu()
                    return
                
                if user_input == "skip":
                    self.interview_answers.append(None)
                    self.ai.q_index += 1
                    if self.ai.q_index < total:
                        print(f"\n📊 Progress: {self.ai.q_index}/{total}")
                        input("\nPress Enter for next question...")
                    continue
                
                print("\n🎤 Listening...")
                self.ai.speak("Listening to your answer.")
                answer = self.ai.listen()
                
                if answer:
                    print(f"\n📝 You said: {answer}")
                    self.interview_answers.append(answer)
                    print(f"\n✅ Answer recorded!")
                else:
                    print("\n❌ No speech detected. Type your answer: ")
                    answer = input("> ").strip()
                    if answer.lower() == "exit":
                        self.exit_to_menu()
                        return
                    if answer.lower() == "skip":
                        self.interview_answers.append(None)
                    elif answer:
                        self.interview_answers.append(answer)
                    else:
                        self.interview_answers.append(None)
                
                self.ai.q_index += 1
                if self.ai.q_index < total:
                    print(f"\n📊 Progress: {self.ai.q_index}/{total}")
                    input("\nPress Enter for next question...")
            
            self.show_interview_results()
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def show_interview_results(self):
        self.clear_screen()
        self.print_header("📊 INTERVIEW EVALUATION & SUGGESTIONS")
        
        if not self.interview_answers or not any(ans is not None for ans in self.interview_answers):
            print("\n❌ No answers to evaluate.")
            return
        
        total_score = 0
        answered_count = 0
        
        print("\n📝 Evaluating your answers...\n")
        
        for i, (q, ans) in enumerate(zip(self.ai.questions[:len(self.interview_answers)], self.interview_answers)):
            print(f"{'='*60}")
            print(f"Q{i+1}: {q['question'][:70]}...")
            
            if ans is None:
                print("❌ Skipped")
                continue
            
            eval_result = self.ai.evaluate_answer(q, ans)
            score = eval_result.get('score', 0)
            total_score += score
            answered_count += 1
            
            print(f"\n📊 Score: {score}/10")
            print(f"✅ Strengths: {', '.join(eval_result.get('strengths', ['None'])[:2])}")
            print(f"🔧 Improve: {', '.join(eval_result.get('weaknesses', ['None'])[:2])}")
            print()
        
        print(f"\n{'='*60}")
        print("📊 SUMMARY")
        print(f"{'='*60}")
        print(f"Answered: {answered_count}/{len(self.interview_answers)}")
        
        if answered_count > 0:
            avg_score = total_score / answered_count
            print(f"Average Score: {avg_score:.1f}/10")
            
            if avg_score >= 8:
                print("\n⭐ EXCELLENT! You're well prepared!")
            elif avg_score >= 6:
                print("\n👍 GOOD! Keep practicing.")
            else:
                print("\n📖 NEEDS PRACTICE.")
        
        print("\n" + "="*60)
        print("💡 AI-GENERATED SUGGESTIONS")
        print("="*60)
        
        suggestions = self.ai.get_interview_suggestions()
        if suggestions:
            print(f"\n📌 Summary: {suggestions.get('summary', '')}")
            print(f"\n✅ Strengths: {', '.join(suggestions.get('strengths', ['None']))}")
            print(f"\n🎯 Areas to Improve: {', '.join(suggestions.get('weak_areas', ['None']))}")
            print(f"\n📝 Improvement Plan:")
            for step in suggestions.get('improvement_plan', ['Practice more']):
                print(f"   • {step}")
    
    def get_hr_tips(self):
        self.clear_screen()
        self.print_header("💼 HR INTERVIEW TIPS")
        
        print("\n💡 No Resume or Job Description needed!")
        print("   Get general HR tips and personalized advice.\n")
        
        print("="*60)
        print("  💡 TELL US ABOUT YOUR HR CHALLENGE")
        print("="*60)
        print("\nWhat makes HR interviews difficult for you?")
        print("Examples: 'I struggle with salary negotiation',")
        print("'I don't know how to answer weakness questions',")
        print("'I get nervous during HR interviews'")
        print("\nType 'skip' to get general HR tips")
        print("Type 'exit' to return to menu\n")
        
        concern = input("👉 Your concern: ").strip()
        
        if concern.lower() == "exit":
            self.exit_to_menu()
            return
        
        if concern.lower() == "skip":
            concern = ""
        
        try:
            # Generate tips based on concern
            tips = self.ai.generate_hr_tips(concern)
            
            if not tips:
                print("❌ No HR tips generated.")
                input("\nPress Enter to continue...")
                return
            
            print(f"\n✅ {len(tips)} HR questions generated!\n")
            
            for i, tip in enumerate(tips, 1):
                print(f"\n{'='*60}")
                print(f"HR QUESTION {i}/{len(tips)}")
                print(f"{'='*60}")
                print(f"\n❓ {tip.get('question', '')}")
                print(f"\n💡 Best Practice: {tip.get('best_practice', '')}")
                print(f"\n📝 Sample Answer: {tip.get('sample_answer', '')}")
                
                if i < len(tips):
                    print("\n" + "-"*40)
                    choice = input("\nPress Enter for next tip or type 'exit' to return: ").strip().lower()
                    if choice == "exit":
                        self.exit_to_menu()
                        return
            
            # If user had a concern, show personalized advice
            if concern:
                print("\n" + "="*60)
                print("  💡 PERSONALIZED HR ADVICE")
                print("="*60)
                print(f"\nBased on your concern: '{concern}'\n")
                
                advice = self.ai.get_hr_advice(concern)
                if advice:
                    print(f"📌 {advice.get('summary', '')}")
                    print(f"\n💡 Advice:")
                    for a in advice.get('advice', ['Practice more']):
                        print(f"   • {a}")
                    print(f"\n📝 Practice Tips:")
                    for p in advice.get('practice_tips', ['Practice daily']):
                        print(f"   • {p}")
                    print(f"\n💪 {advice.get('confidence_boost', 'Keep practicing and you will improve!')}")
                else:
                    print("📝 Keep practicing and you will improve with time!")
            
            print("\n" + "="*60)
            print("✅ All HR tips displayed!")
            
        except Exception as e:
            print(f"\n❌ Error generating HR tips: {e}")
            print("\n💡 Tip: Make sure your API key is valid.")
        
        input("\nPress Enter to continue...")
    
    def view_analytics(self):
        self.clear_screen()
        self.print_header("📊 PERFORMANCE ANALYTICS")
        
        stats = self.ai.get_statistics()
        
        print(f"\n👤 CANDIDATE: {stats.get('name', 'Not set')}")
        print(f"🎯 TARGET ROLE: {stats.get('role', 'Not set')}")
        print(f"🏢 COMPANY: {stats.get('company', 'Not set')}")
        
        print("\n📈 INTERVIEW PRACTICE:")
        print(f"   Questions Attempted: {stats['interview']['total']}")
        if stats['interview']['total'] > 0:
            print(f"   Average Score: {stats['interview']['avg_score']:.1f}/10")
            
            suggestions = self.ai.get_interview_suggestions()
            if suggestions:
                weak_areas = suggestions.get('weak_areas', ['None'])
                weak_str = ', '.join(weak_areas[:3]) if weak_areas else 'None'
                print(f"\n   💡 Last Interview Suggestions:")
                print(f"      Summary: {suggestions.get('summary', 'N/A')}")
                print(f"      Weak Areas: {weak_str}")
        else:
            print("   No interview practice taken yet")
        
        print("\n📝 APTITUDE TEST:")
        if stats['aptitude']['total'] > 0:
            print(f"   Score: {stats['aptitude']['correct']}/{stats['aptitude']['total']}")
            print(f"   Percentage: {stats['aptitude']['percentage']:.1f}%")
            
            apt_suggestions = self.ai.get_aptitude_suggestions()
            if apt_suggestions:
                weak_areas = apt_suggestions.get('weak_areas', ['None'])
                weak_str = ', '.join(weak_areas[:3]) if weak_areas else 'None'
                print(f"\n   💡 Last Aptitude Suggestions:")
                print(f"      Summary: {apt_suggestions.get('summary', 'N/A')}")
                print(f"      Weak Areas: {weak_str}")
        else:
            print("   No aptitude test taken yet")
        
        print("\n💡 RECOMMENDATIONS:")
        if stats['interview']['total'] < 5:
            print("   • Practice more interview questions")
        if stats['interview']['total'] > 0 and stats['interview']['avg_score'] < 7:
            print("   • Focus on improving answer quality")
        if stats['aptitude']['total'] == 0:
            print("   • Take an aptitude test")
        if stats['aptitude']['total'] > 0 and stats['aptitude']['percentage'] < 60:
            print("   • Practice aptitude fundamentals")
        
        input("\nPress Enter to continue...")
    
    def exit_application(self):
        self.clear_screen()
        print("\n" + "="*60)
        print("  👋 THANK YOU FOR USING AI INTERVIEW ASSISTANT!")
        print("="*60)
        print("\n  Good luck with your interviews! 🚀\n")
        self.running = False
    
    def run(self):
        while self.running:
            self.print_menu()
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == "1":
                self.take_aptitude()
            elif choice == "2":
                self.interview_practice()
            elif choice == "3":
                self.get_hr_tips()
            elif choice == "4":
                self.view_analytics()
            elif choice == "5":
                self.exit_application()
            else:
                print("\n❌ Invalid choice.")
                time.sleep(1)