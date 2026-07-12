# interviewprep/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import json
import traceback
from .models import (
    InterviewSession, InterviewQuestion, InterviewAnswer,
    AptitudeTest, AptitudeQuestion, AptitudeAnswer,
    HRTip, Profile
)
from .services.backend import InterviewAssistant

@login_required
def interview_home(request):
    """Main interview preparation dashboard"""
    
    total_interviews = InterviewSession.objects.filter(
        user=request.user
    ).count()

    completed_interviews = InterviewSession.objects.filter(
        user=request.user,
        is_completed=True
    ).count()

    aptitude_tests = AptitudeTest.objects.filter(
        user=request.user,
        is_completed=True
    )

    recent_sessions = InterviewSession.objects.filter(
        user=request.user
    ).order_by("-created_at")[:5]

    average_score = 0

    if aptitude_tests.exists():
        scores = [
            (test.correct_answers / test.total_questions) * 100
            for test in aptitude_tests
            if test.total_questions > 0
        ]

        if scores:
            average_score = round(sum(scores) / len(scores), 1)

    # ============================================
    # DEBUG OUTPUT - Check these in your terminal
    # ============================================
    print("=" * 60)
    print("📊 DASHBOARD DEBUG")
    print("=" * 60)
    print("👤 User:", request.user.username)
    print("📝 Total Interviews:", total_interviews)
    print("✅ Completed Interviews:", completed_interviews)
    print("🧠 Completed Aptitude Tests:", aptitude_tests.count())

    for test in aptitude_tests:
        print(
            f"  Test ID={test.id}, "
            f"Correct={test.correct_answers}, "
            f"Total={test.total_questions}, "
            f"Completed={test.is_completed}"
        )

    print("📊 Average Score:", average_score)
    print("=" * 60)

    context = {
        "total_interviews": total_interviews,
        "completed_interviews": completed_interviews,
        "aptitude_tests": aptitude_tests.count(),
        "average_score": average_score,
        "recent_sessions": recent_sessions,
    }

    return render(
        request,
        "jobseeker/interviewprep.html",
        context,
    )

@login_required
def aptitude_test(request):
    """Start or continue aptitude test"""
    ongoing_test = AptitudeTest.objects.filter(
        user=request.user, 
        is_completed=False
    ).first()
    
    context = {
        'ongoing_test': ongoing_test,
    }
    return render(request, "jobseeker/aptitude_test.html", context)

@csrf_exempt
@login_required
def generate_aptitude_questions(request):
    """Generate aptitude questions using AI"""
    if request.method == 'POST':
        try:
            test = AptitudeTest.objects.create(
                user=request.user,
                total_questions=35
            )
            
            assistant = InterviewAssistant()
            questions = assistant.generate_aptitude()
            
            for i, q in enumerate(questions):
                AptitudeQuestion.objects.create(
                    test=test,
                    category=q.get('category', 'General'),
                    question_text=q['question'],
                    options=q.get('options', ['A', 'B', 'C', 'D']),
                    correct_answer=q.get('correct', 0),
                    difficulty=q.get('difficulty', 'medium'),
                    explanation=q.get('explanation', ''),
                    order=i
                )
            
            return JsonResponse({
                'success': True,
                'test_id': test.id,
                'total_questions': len(questions)
            })
            
        except Exception as e:
            print("\n========== APTITUDE GENERATE ERROR ==========")
            traceback.print_exc()
            print("=============================================\n")
            
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def get_aptitude_question(request, test_id):
    """Get current aptitude question"""
    try:
        test = get_object_or_404(AptitudeTest, id=test_id, user=request.user)
        answered_count = AptitudeAnswer.objects.filter(
            question__test=test
        ).count()
        
        if answered_count >= test.total_questions:
            return JsonResponse({
                'completed': True,
                'test_id': test.id
            })
        
        question = AptitudeQuestion.objects.filter(
            test=test,
            order=answered_count
        ).first()
        
        if not question:
            return JsonResponse({
                'completed': True,
                'test_id': test.id
            })
        
        return JsonResponse({
            'question': {
                'id': question.id,
                'order': question.order + 1,
                'total': test.total_questions,
                'category': question.category,
                'text': question.question_text,
                'options': question.options,
                'difficulty': question.difficulty
            }
        })
        
    except Exception as e:
        print("\n========== GET APTITUDE QUESTION ERROR ==========")
        traceback.print_exc()
        print("================================================\n")
        
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def submit_aptitude_answer(request):
    """Submit aptitude answer"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question_id = data.get('question_id')
            selected_answer = data.get('selected_answer')
            
            question = get_object_or_404(AptitudeQuestion, id=question_id)
            test = question.test
            
            if test.user != request.user:
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            existing_answer = AptitudeAnswer.objects.filter(
                question=question
            ).first()
            
            if existing_answer:
                return JsonResponse({'error': 'Already answered'}, status=400)
            
            is_correct = (selected_answer == question.correct_answer)
            
            AptitudeAnswer.objects.create(
                question=question,
                selected_answer=selected_answer,
                is_correct=is_correct
            )
            
            answered_count = AptitudeAnswer.objects.filter(
                question__test=test
            ).count()
            
            if answered_count >= test.total_questions:
                test.is_completed = True
                test.completed_at = timezone.now()
                test.correct_answers = AptitudeAnswer.objects.filter(
                    question__test=test,
                    is_correct=True
                ).count()
                test.save()
            
            return JsonResponse({
                'success': True,
                'is_correct': is_correct,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation,
                'progress': {
                    'answered': answered_count,
                    'total': test.total_questions,
                    'completed': answered_count >= test.total_questions
                }
            })
            
        except Exception as e:
            print("\n========== SUBMIT APTITUDE ANSWER ERROR ==========")
            traceback.print_exc()
            print("==================================================\n")
            
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def aptitude_results(request, test_id):
    """Show aptitude test results"""
    try:
        test = get_object_or_404(AptitudeTest, id=test_id, user=request.user)
        
        if not test.is_completed:
            messages.warning(request, "Test not completed yet!")
            return redirect('interviewprep:aptitude_test')
        
        answers = AptitudeAnswer.objects.filter(question__test=test)
        
        category_data = {}
        for answer in answers:
            category = answer.question.category
            if category not in category_data:
                category_data[category] = {'correct': 0, 'total': 0}
            category_data[category]['total'] += 1
            if answer.is_correct:
                category_data[category]['correct'] += 1
        
        context = {
            'test': test,
            'answers': answers,
            'category_data': category_data,
            'percentage': (test.correct_answers / test.total_questions) * 100 if test.total_questions > 0 else 0
        }
        
        return render(request, "jobseeker/aptitude_results.html", context)
        
    except Exception as e:
        print("\n========== APTITUDE RESULTS ERROR ==========")
        traceback.print_exc()
        print("============================================\n")
        
        messages.error(request, f"Error loading results: {str(e)}")
        return redirect('interviewprep:aptitude_test')

@login_required
def start_interview(request):
    """Start a new interview session"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mode = data.get('mode', 'mixed')
            
            # Get or create profile
            try:
                profile = request.user.profile
            except:
                profile = Profile.objects.create(user=request.user)
            
            # Check if user has resume and JD
            has_resume = bool(profile.resume)
            has_jd = bool(profile.job_description)
            
            if not has_resume:
                return JsonResponse({
                    'success': False,
                    'error': 'Please upload your resume first'
                }, status=400)
            
            if not has_jd:
                return JsonResponse({
                    'success': False,
                    'error': 'Please add a job description first'
                }, status=400)
            
            session = InterviewSession.objects.create(
                user=request.user,
                mode=mode
            )
            
            assistant = InterviewAssistant()
            
            resume_path = profile.resume.path
            jd_text = profile.job_description
            
            assistant.load_resume(resume_path)
            assistant.load_job_description(jd_text)
            
            questions = assistant.generate_questions(mode)
            
            for i, q in enumerate(questions):
                InterviewQuestion.objects.create(
                    session=session,
                    question_text=q['question'],
                    difficulty=q.get('difficulty', 'medium'),
                    category=q.get('category', ''),
                    expected_points=q.get('expected_points', []),
                    evaluation_criteria=q.get('evaluation_criteria', ''),
                    order=i
                )
            
            return JsonResponse({
                'success': True,
                'session_id': session.id,
                'total_questions': len(questions)
            })
            
        except Exception as e:
            print("\n========== START INTERVIEW ERROR ==========")
            traceback.print_exc()
            print("===========================================\n")
            
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    # GET request
    try:
        profile = request.user.profile
        has_resume = bool(profile.resume)
        has_jd = bool(profile.job_description)
    except:
        has_resume = False
        has_jd = False
    
    context = {
        'has_resume': has_resume,
        'has_jd': has_jd
    }
    
    return render(request, "jobseeker/interview_practice.html", context)

@login_required
def get_interview_question(request, session_id):
    """Get next interview question"""
    try:
        session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
        answered_count = InterviewAnswer.objects.filter(question__session=session).count()
        
        if answered_count >= session.questions.count():
            return JsonResponse({
                'completed': True,
                'session_id': session.id
            })
        
        question = InterviewQuestion.objects.filter(session=session).order_by('order')[answered_count]
        
        return JsonResponse({
            'question': {
                'id': question.id,
                'order': question.order + 1,
                'total': session.questions.count(),
                'text': question.question_text,
                'difficulty': question.difficulty,
                'category': question.category
            }
        })
        
    except Exception as e:
        print("\n========== GET INTERVIEW QUESTION ERROR ==========")
        traceback.print_exc()
        print("==================================================\n")
        
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def submit_interview_answer(request):
    """Submit interview answer"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question_id = data.get('question_id')
            answer_text = data.get('answer')
            
            question = get_object_or_404(InterviewQuestion, id=question_id)
            session = question.session
            
            if session.user != request.user:
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            assistant = InterviewAssistant()
            evaluation = assistant.evaluate_answer(
                {'question': question.question_text},
                answer_text
            )
            
            interview_answer = InterviewAnswer.objects.create(
                question=question,
                answer_text=answer_text,
                score=evaluation.get('score', 0),
                strengths=evaluation.get('strengths', []),
                weaknesses=evaluation.get('weaknesses', []),
                suggestions=evaluation.get('suggestions', []),
                sample_answer=evaluation.get('sample_answer', '')
            )
            
            answered_count = InterviewAnswer.objects.filter(question__session=session).count()
            if answered_count >= session.questions.count():
                session.is_completed = True
                session.completed_at = timezone.now()
                session.save()
            
            return JsonResponse({
                'success': True,
                'evaluation': {
                    'score': interview_answer.score,
                    'strengths': interview_answer.strengths,
                    'weaknesses': interview_answer.weaknesses,
                    'suggestions': interview_answer.suggestions,
                    'sample_answer': interview_answer.sample_answer
                },
                'progress': {
                    'answered': answered_count,
                    'total': session.questions.count(),
                    'completed': answered_count >= session.questions.count()
                }
            })
            
        except Exception as e:
            print("\n========== SUBMIT INTERVIEW ANSWER ERROR ==========")
            traceback.print_exc()
            print("===================================================\n")
            
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def interview_results(request, session_id):
    """Show interview results"""
    try:
        session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
        answers = InterviewAnswer.objects.filter(question__session=session)
        
        context = {
            'session': session,
            'answers': answers,
            'total_score': sum(a.score for a in answers) / len(answers) if answers else 0,
            'total_questions': session.questions.count(),
            'answered_questions': answers.count()
        }
        
        return render(request, "jobseeker/interview_results.html", context)
        
    except Exception as e:
        print("\n========== INTERVIEW RESULTS ERROR ==========")
        traceback.print_exc()
        print("=============================================\n")
        
        messages.error(request, f"Error loading results: {str(e)}")
        return redirect('interviewprep:home')

@login_required
def hr_tips(request):
    """HR interview tips page"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            concern = data.get('concern', '')
            
            assistant = InterviewAssistant()
            tips = assistant.generate_hr_tips(concern)
            
            for tip in tips:
                HRTip.objects.create(
                    user=request.user,
                    question=tip.get('question', ''),
                    best_practice=tip.get('best_practice', ''),
                    sample_answer=tip.get('sample_answer', '')
                )
            
            return JsonResponse({
                'success': True,
                'tips': tips,
                'count': len(tips)
            })
            
        except Exception as e:
            print("\n========== HR TIPS ERROR ==========")
            traceback.print_exc()
            print("===================================\n")
            
            return JsonResponse({'error': str(e)}, status=500)
    
    saved_tips = HRTip.objects.filter(user=request.user).order_by('-created_at')[:10]
    context = {'saved_tips': saved_tips}
    return render(request, "jobseeker/hr_tips.html", context)

@login_required
def analytics(request):
    """Performance analytics dashboard"""
    try:
        interview_sessions = InterviewSession.objects.filter(user=request.user)
        completed_interviews = interview_sessions.filter(is_completed=True)
        
        interview_data = {
            'total': interview_sessions.count(),
            'completed': completed_interviews.count(),
            'average_score': 0,
            'recent_scores': []
        }
        
        if completed_interviews.exists():
            all_scores = []
            for session in completed_interviews:
                answers = InterviewAnswer.objects.filter(question__session=session)
                if answers:
                    avg_score = sum(a.score for a in answers) / len(answers)
                    all_scores.append(avg_score)
                    interview_data['recent_scores'].append({
                        'date': session.completed_at,
                        'score': round(avg_score, 1),
                        'role': session.role
                    })
            
            if all_scores:
                interview_data['average_score'] = sum(all_scores) / len(all_scores)
        
        aptitude_tests = AptitudeTest.objects.filter(user=request.user, is_completed=True)
        aptitude_data = {
            'total': aptitude_tests.count(),
            'average_score': 0,
            'recent_scores': []
        }
        
        if aptitude_tests.exists():
            scores = [test.correct_answers / test.total_questions * 100 for test in aptitude_tests]
            aptitude_data['average_score'] = sum(scores) / len(scores)
            aptitude_data['recent_scores'] = [
                {
                    'date': test.completed_at,
                    'score': round(test.correct_answers / test.total_questions * 100, 1)
                }
                for test in aptitude_tests.order_by('-completed_at')[:5]
            ]
        
        context = {
            'interview_stats': interview_data,
            'aptitude_stats': aptitude_data,
            'has_data': interview_data['total'] > 0 or aptitude_data['total'] > 0
        }
        
        return render(request, "jobseeker/analytics.html", context)
        
    except Exception as e:
        print("\n========== ANALYTICS ERROR ==========")
        traceback.print_exc()
        print("=====================================\n")
        
        messages.error(request, f"Error loading analytics: {str(e)}")
        return redirect('interviewprep:home')

# ============================================
# Save Profile Data View
# ============================================

@csrf_exempt
@login_required
def save_profile_data(request):
    """Save resume and job description to user profile"""
    if request.method == 'POST':
        try:
            # Get or create profile
            try:
                profile = request.user.profile
            except:
                profile = Profile.objects.create(user=request.user)
            
            # Save resume if uploaded
            if request.FILES.get('resume'):
                # Delete old resume if exists
                if profile.resume:
                    import os
                    if os.path.isfile(profile.resume.path):
                        profile.resume.delete()
                profile.resume = request.FILES['resume']
            
            # Save job description
            job_description = request.POST.get('job_description', '')
            if job_description:
                profile.job_description = job_description
            
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Profile data saved successfully',
                'has_resume': bool(profile.resume),
                'has_jd': bool(profile.job_description)
            })
            
        except Exception as e:
            print("\n========== SAVE PROFILE ERROR ==========")
            traceback.print_exc()
            print("========================================\n")
            
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# ============================================
# Get Profile Data View (Optional)
# ============================================

@login_required
def get_profile_data(request):
    """Get user profile data"""
    try:
        profile = request.user.profile
        return JsonResponse({
            'success': True,
            'has_resume': bool(profile.resume),
            'has_jd': bool(profile.job_description),
            'resume_name': profile.resume.name if profile.resume else None,
            'job_description': profile.job_description
        })
    except Exception as e:
        print("\n========== GET PROFILE ERROR ==========")
        traceback.print_exc()
        print("=======================================\n")
        
        return JsonResponse({
            'success': True,
            'has_resume': False,
            'has_jd': False,
            'resume_name': None,
            'job_description': None
        })